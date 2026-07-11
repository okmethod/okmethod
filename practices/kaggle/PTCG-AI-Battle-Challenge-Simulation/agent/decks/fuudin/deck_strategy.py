"""フーディンデッキ固有の戦略ロジック。

フーディン「ハンドパワー」をメインアタッカーに、ノコッチ/ノコッチを壁として使うデッキ。
詳細: docs/decks/strategy_fuudin.md
"""

from dataclasses import dataclass, field

from cg.api import (
    AreaType,
    Card,
    CardType,
    EnergyType,
    Observation,
    Option,
    OptionType,
    Pokemon,
    SelectContext,
    SelectData,
)

from models import AttackPlan, GameContext
from utils import (
    calc_damage,
    card_table,
    collect_zone_counts,
    get_card,
    prize_count,
    read_deck_csv,
)


@dataclass
class FuudinTurnState:
    """フーディンデッキのターン内スコープ状態"""

    plan: AttackPlan = field(default_factory=AttackPlan)


class FuudinDeckStrategy:
    """フーディンデッキの戦略実装。

    DeckStrategyProtocol を満たす具象クラス。
    デッキ固有のカードID定数・スコアリングロジックをここに閉じ込める。

    ## メソッド構成（呼び出し階層）
    - reset_turn                   : ターン開始時にターン内状態をリセット
    - collect_context              : 盤面スナップショットを GameContext に収集
        - collect_zone_counts [util] : フィールド・手札・捨て札枚数を集計
    - update_attack_plan           : フーディンのハンドパワー最善計画を立案
        - _collect_switch_flags    : MAIN で可能なスイッチフラグを収集
    - score_option [基底]          : NUMBER/YES を処理し _score_deck_option へ委譲
    - _score_deck_option           : OptionType 別スコア関数へディスパッチ
        - _score_card              : CARD を SelectContext 別サブ関数へディスパッチ
            - _score_card_switch   : SWITCH / TO_ACTIVE コンテキスト
            - _score_card_setup    : SETUP_ACTIVE_POKEMON コンテキスト
            - _score_card_to_hand  : TO_HAND コンテキスト
            - _score_energy  (*)   : エネルギー手張り先ポケモンへのスコア
        - _score_play              : PLAY オプションのスコア
        - _score_attach            : ATTACH オプションのスコア
            - _score_energy  (*)   : (上記と共有)
        - _score_evolve            : EVOLVE オプションのスコア
        - _score_ability           : ABILITY オプションのスコア
        - _score_retreat           : RETREAT オプションのスコア
        - _score_attack            : ATTACK オプションのスコア
    - post_pick                    : アクション選択後に状態を更新（現状ノーオペ）
    """

    # カードID定数（自デッキ）
    Abra = 741  # ケーシィ
    Kadabra = 742  # ユンゲラー
    Alakazam = 743  # フーディン
    Noctachi = 65  # ノコッチ
    Noctachi_Evo = 66  # ノコッチ（進化後）
    Fezandipiti_ex = 140  # キチキギスex

    Poffin = 1086  # なかよしポフィン
    Poke_Pad = 1152  # ポケパッド
    Rare_Candy = 1079  # ふしぎなアメ
    Night_Stretcher = 1097  # 夜のタンカ
    Wonder_Patch = 1146  # ワンダーパッチ
    Sacred_Ash = 1129  # せいなるはい

    Dawn = 1231  # ヒカリ
    Touko = 1225  # トウコ
    Boss_Orders = 1182  # ボスの指令
    Suilens_Care = 1184  # スイレンのお世話

    Battle_Colosseum = 1264  # バトルコロシアム

    Telepass_Psychic = 19  # テレパス【超】エネルギー
    Basic_Psychic = 5  # 基本【超】エネルギー
    Rich_Energy = 13  # リッチエネルギー (ACE SPEC)

    # カードID定数（相手デッキ識別用：対メガルカリオ戦の退場判断に使用）
    Riolu = 677
    Mega_Lucario_ex = 678

    def __init__(self) -> None:
        self.OWN_DECK = read_deck_csv("decks/fuudin/deck_recipe.csv")
        self._state = FuudinTurnState()

    def reset_turn(self) -> None:
        """ターン開始時にターン内スコープの状態をリセットする。"""
        self._state = FuudinTurnState()

    # --- コンテキスト収集 ---

    def collect_context(self, obs: Observation) -> GameContext:
        """agent() 1回分の盤面スナップショットを収集して GameContext を返す。

        sub_attacker_ready を conserve_energy フラグとして流用する。
        場の全フーディンライン（ケーシィ/ユンゲラー/フーディン）が
        1枚以上エネルギーを保有している場合に True となり、エネルギー付与を停止する。
        """
        assert obs.current is not None
        game_state = obs.current
        own_index = game_state.yourIndex
        own_state = game_state.players[own_index]

        field_counts, hand_counts, discard_counts, stadium_id, can_attack = (
            collect_zone_counts(obs, own_index)
        )

        main_attacker_ready = False
        psychic_line_on_field: list[Pokemon] = []
        for card in own_state.active + own_state.bench:
            if card is None:
                continue
            if card.id in (self.Abra, self.Kadabra, self.Alakazam):
                assert isinstance(card, Pokemon)
                psychic_line_on_field.append(card)
                if card.id in (self.Kadabra, self.Alakazam) and len(card.energies) >= 1:
                    main_attacker_ready = True

        conserve_energy = len(psychic_line_on_field) > 0 and all(
            len(c.energies) >= 1 for c in psychic_line_on_field
        )

        return GameContext(
            own_index=own_index,
            own_prize=len(own_state.prize),
            field_counts=field_counts,
            hand_counts=hand_counts,
            discard_counts=discard_counts,
            main_attacker_ready=main_attacker_ready,
            sub_attacker_ready=conserve_energy,
            stadium_id=stadium_id,
            can_attack=can_attack,
        )

    # --- 攻撃計画 ---

    def _collect_switch_flags(
        self, obs: Observation, own_index: int, select: SelectData
    ) -> tuple[bool, bool]:
        """MAINコンテキストで可能なスイッチフラグを収集する。"""
        can_switch = False
        can_op_switch = False
        for o in select.option:
            if o.type == OptionType.PLAY:
                card = get_card(obs, AreaType.HAND, o.index, own_index)
                if card is not None and card.id == self.Boss_Orders:
                    can_op_switch = True
            elif o.type == OptionType.RETREAT:
                can_switch = True
            elif o.type == OptionType.ABILITY:
                card = (
                    get_card(obs, o.area, o.index, own_index)
                    if o.area is not None
                    else None
                )
                if card is not None and card.id == self.Noctachi_Evo:
                    can_switch = True  # にげあしドローで場を空けてフーディンを出せる
        return can_switch, can_op_switch

    def update_attack_plan(self, obs: Observation, ctx: GameContext) -> None:
        """フーディンのハンドパワーによる最善の攻撃計画を _state.plan に保存する。"""
        assert obs.current is not None
        assert obs.select is not None
        game_state = obs.current
        select = obs.select

        if select.context != SelectContext.MAIN:
            return
        if game_state.turn < 2:
            return

        own_index = ctx.own_index
        own_state = game_state.players[own_index]
        op_state = game_state.players[1 - own_index]
        can_switch, can_op_switch = self._collect_switch_flags(obs, own_index, select)

        hand_size = len(own_state.hand) if own_state.hand is not None else 0
        own_cards = [own_state.active[0]] + list(own_state.bench)
        op_cards = [op_state.active[0]] + list(op_state.bench)
        best_score = -1

        for i, own_pokemon in enumerate(own_cards):
            if own_pokemon is None:
                continue
            if i != 0 and not can_switch:
                break
            if own_pokemon.id != self.Alakazam:
                continue

            energy_count = len(own_pokemon.energies)
            needs_energy_attach = False
            psychic_in_hand = (
                ctx.hand_counts[self.Basic_Psychic]
                + ctx.hand_counts[self.Telepass_Psychic]
            )

            if energy_count < 1:
                if psychic_in_hand >= 1 and not game_state.energyAttached:
                    energy_count = 1
                    needs_energy_attach = True
                else:
                    continue

            # 手張り分だけ手札が減るため、ハンドパワーのダメージを補正
            effective_hand = max(0, hand_size - (1 if needs_energy_attach else 0))
            base_damage = effective_hand * 20

            for j, op_pokemon in enumerate(op_cards):
                if op_pokemon is None:
                    continue
                if j != 0 and not can_op_switch:
                    break

                damage = calc_damage(base_damage, op_pokemon, EnergyType.PSYCHIC)
                score = self._score_target(op_pokemon, op_state)
                prize = prize_count(op_pokemon) if op_pokemon.hp <= damage else 0
                if op_pokemon.hp > damage:
                    score = int(score * damage / op_pokemon.hp)
                if len(op_state.prize) <= prize:
                    score = 50000
                if i == 0:
                    score += 220
                if j == 0:
                    score += 300

                if best_score < score:
                    best_score = score
                    self._state.plan.attacker = i
                    self._state.plan.target = j
                    self._state.plan.attack_index = 0
                    self._state.plan.remain_hp = op_pokemon.hp - damage
                    self._state.plan.needs_energy_attach = needs_energy_attach

    # --- スコアリング（OptionType 別） ---

    def _score_target(self, pokemon: Pokemon, op_state) -> int:
        """相手ポケモンの撃破優先度スコアを返す。"""
        data = card_table[pokemon.id]
        score = prize_count(pokemon) * 1000
        score += len(pokemon.energies) * 150
        score += len(pokemon.tools) * 100
        if data.stage2:
            score += 250
        elif data.stage1:
            score += 130
        score += pokemon.hp
        return score

    def _score_energy(self, pokemon: Pokemon, active: bool, ctx: GameContext) -> int:
        """エネルギー手張り先ポケモンへのスコアを返す。

        conserve_energy (ctx.sub_attacker_ready) が True のとき、
        フーディンラインへの通常エネルギー追加を停止する。
        ノコッチラインへの基本エネルギー付与は常に低優先（リッチエネルギーのみで管理）。
        """
        energy_count = len(pokemon.energies)
        conserve_energy = ctx.sub_attacker_ready

        score = 8000
        if active:
            score += 10

        if pokemon.id in (self.Abra, self.Kadabra, self.Alakazam):
            if pokemon.id == self.Alakazam:
                score += 2
            elif pokemon.id == self.Kadabra:
                score += 1
            if conserve_energy:
                score -= 5000
            elif energy_count < 1:
                score += 100
        elif pokemon.id in (self.Noctachi, self.Noctachi_Evo):
            score -= 5000  # 基本エネルギーは不要（リッチエネルギーのみで管理）
        elif pokemon.id == self.Fezandipiti_ex:
            score -= 8000

        return score

    def _score_card_switch(
        self, o: Option, card: Pokemon | Card, ctx: GameContext
    ) -> int:
        """SWITCH / TO_ACTIVE コンテキストでのカードスコア。"""
        ec = len(card.energies) if isinstance(card, Pokemon) else 0
        if o.playerIndex == ctx.own_index:
            score = ec * 2
            if o.index == self._state.plan.attacker - 1:
                score += 100
            if card.id == self.Alakazam:
                score += 30
            elif card.id == self.Kadabra:
                score += 10 if ec >= 1 else 5
            elif card.id == self.Abra:
                score += 3
            elif card.id == self.Noctachi_Evo:
                score += 8
            elif card.id == self.Noctachi:
                score += 5
            elif card.id == self.Fezandipiti_ex:
                score -= 100  # 自分から選ばない
            return score
        else:
            return 100 if o.index == self._state.plan.target - 1 else 0

    def _score_card_setup(
        self, card: Pokemon | Card, obs: Observation, ctx: GameContext
    ) -> int:
        """SETUP_ACTIVE_POKEMON（ゲーム開始時バトル場配置）でのカードスコア。"""
        if card.id == self.Noctachi:
            return 10  # 壁として先頭に置く
        if card.id == self.Abra:
            return 5
        if card.id == self.Fezandipiti_ex:
            return 1
        return 0

    def _score_card_to_hand(
        self, card: Pokemon | Card, obs: Observation, ctx: GameContext
    ) -> int:
        """TO_HAND コンテキストでのカードスコア。"""
        score = 200 - ctx.hand_counts[card.id] * 100
        if card.id == self.Abra:
            total = (
                ctx.field_counts[self.Abra]
                + ctx.field_counts[self.Kadabra]
                + ctx.field_counts[self.Alakazam]
            )
            score += 30 if total < 3 else -50
        elif card.id == self.Kadabra:
            score += 20 if ctx.field_counts[self.Abra] >= 1 else -10
        elif card.id == self.Alakazam:
            score += 30 if ctx.field_counts[self.Kadabra] >= 1 else 10
        elif card.id == self.Noctachi:
            total = (
                ctx.field_counts[self.Noctachi] + ctx.field_counts[self.Noctachi_Evo]
            )
            score += 20 if total < 2 else -50
        elif card.id == self.Noctachi_Evo:
            score += 15 if ctx.field_counts[self.Noctachi] >= 1 else -20
        elif card.id == self.Rich_Energy:
            score += 50
        elif card.id in (self.Basic_Psychic, self.Telepass_Psychic):
            score += 10
        return score

    def _score_card(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """CARD オプションを SelectContext に応じたサブ関数へディスパッチする。"""
        assert o.area is not None and o.playerIndex is not None
        card = get_card(obs, o.area, o.index, o.playerIndex)
        if card is None:
            return 0
        assert obs.select is not None
        match obs.select.context:
            case SelectContext.SWITCH | SelectContext.TO_ACTIVE:
                return self._score_card_switch(o, card, ctx)
            case SelectContext.SETUP_ACTIVE_POKEMON:
                return self._score_card_setup(card, obs, ctx)
            case SelectContext.TO_HAND:
                return self._score_card_to_hand(card, obs, ctx)
            case SelectContext.ATTACH_FROM:
                assert isinstance(card, Pokemon)
                return self._score_energy(card, o.area == AreaType.ACTIVE, ctx)
            case _:
                return 0

    def _score_play(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """PLAY（手札からカードを場に出す）オプションのスコア。"""
        card = get_card(obs, AreaType.HAND, o.index, ctx.own_index)
        assert card is not None
        data = card_table[card.id]
        conserve_energy = ctx.sub_attacker_ready

        if data.cardType == CardType.POKEMON:
            if card.id == self.Abra:
                # ケーシィは3枚目以降スコアを下げてノコッチを優先
                return 20000 if ctx.field_counts[self.Abra] < 3 else 15000
            if card.id == self.Fezandipiti_ex:
                return 18000  # ベンチ待機で特性を活かす
            return 20000

        if card.id == self.Rare_Candy:
            # ふしぎなアメはユンゲラーのサイコドロートリガーを失うため全体的に低優先
            return 5000
        if card.id == self.Wonder_Patch:
            # conserve_energy 中、または基本超エネが手札にない場合は使わない
            if conserve_energy or ctx.hand_counts[self.Basic_Psychic] < 1:
                return -1
            return 7000
        if card.id == self.Boss_Orders:
            return 3200 if self._state.plan.target >= 1 else -1
        if card.id == self.Battle_Colosseum:
            return -1 if ctx.stadium_id == self.Battle_Colosseum else 10000

        return 10000

    def _score_attach(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """ATTACH（エネルギー手張り）オプションのスコア。"""
        assert o.inPlayArea is not None
        card = get_card(obs, AreaType.HAND, o.index, ctx.own_index)
        pokemon = get_card(obs, o.inPlayArea, o.inPlayIndex, ctx.own_index)
        assert card is not None
        assert pokemon is not None
        assert isinstance(pokemon, Pokemon)

        # リッチエネルギーはノコッチ/ノコッチ専用ループ
        if card.id == self.Rich_Energy:
            return 9000 if pokemon.id in (self.Noctachi, self.Noctachi_Evo) else -1

        # テレパスエネルギーはノコッチラインに付けない（ワンダーパッチの対象外でもある）
        if card.id == self.Telepass_Psychic:
            if pokemon.id not in (self.Abra, self.Kadabra, self.Alakazam):
                return -1

        score = self._score_energy(pokemon, o.inPlayArea == AreaType.ACTIVE, ctx)
        if o.inPlayArea == AreaType.ACTIVE:
            if self._state.plan.attacker == 0 and self._state.plan.needs_energy_attach:
                score += 200
        else:
            assert o.inPlayIndex is not None
            if (
                self._state.plan.attacker == 1 + o.inPlayIndex
                and self._state.plan.needs_energy_attach
            ):
                score += 200
        return score

    def _score_evolve(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """EVOLVE（進化）オプションのスコア。"""
        assert o.inPlayArea is not None
        pokemon = get_card(obs, o.inPlayArea, o.inPlayIndex, ctx.own_index)
        evolve_card = get_card(obs, AreaType.HAND, o.index, ctx.own_index)
        assert pokemon is not None
        assert isinstance(pokemon, Pokemon)

        energy_count = len(pokemon.energies)
        base = 9000

        # ユンゲラー→フーディン: エネルギー数を強く重み付け（エネ付きで即攻撃可能）
        if (
            pokemon.id == self.Kadabra
            and evolve_card is not None
            and evolve_card.id == self.Alakazam
        ):
            return base + energy_count * 300

        # ケーシィ→フーディン（ふしぎなアメ）: ユンゲラーのサイコドロートリガーを失うため減点
        if (
            pokemon.id == self.Abra
            and evolve_card is not None
            and evolve_card.id == self.Alakazam
        ):
            return base - 3000

        # バトル場のノコッチ→ノコッチ: フーディンがベンチから攻撃プランを持つターンは抑制
        # （進化後はそのターン中にげあしドローが使えず、フーディンを出せなくなるため）
        if pokemon.id == self.Noctachi and o.inPlayArea == AreaType.ACTIVE:
            if self._state.plan.attacker >= 1 and ctx.main_attacker_ready:
                return -1
            return base + energy_count

        return base + energy_count

    def _score_ability(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """ABILITY（特性）オプションのスコア。"""
        assert o.area is not None
        card = get_card(obs, o.area, o.index, ctx.own_index)
        assert card is not None

        # ノコッチの「にげあしドロー」: フーディン攻撃準備済みならさらに高優先
        if card.id == self.Noctachi_Evo:
            return 25000 if ctx.main_attacker_ready else 20000

        return 30000

    def _score_retreat(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """RETREAT オプションのスコア。"""
        assert obs.current is not None
        own_state = obs.current.players[ctx.own_index]
        op_state = obs.current.players[1 - ctx.own_index]

        own_active = own_state.active[0] if own_state.active else None

        # 対メガルカリオ系: ノコッチがバトル場にいればソルロックに倒される前に退場
        op_all = list(op_state.active) + list(op_state.bench)
        is_vs_megalucario = any(
            p is not None and p.id in (self.Riolu, self.Mega_Lucario_ex) for p in op_all
        )
        if (
            own_active is not None
            and own_active.id == self.Noctachi
            and is_vs_megalucario
        ):
            return 5000

        return 2000 if self._state.plan.attacker >= 1 else -1

    def _score_attack(self, o: Option) -> int:
        """ATTACK オプションのスコア。フーディンはワザが1つのため固定値を返す。"""
        return 1000

    def score_option(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """OptionType に応じてスコア関数をディスパッチする。

        負のスコアを返すと他の選択肢が優先される。
        ただし全選択肢が負の場合は最高スコアのものが選ばれる。
        """
        match o.type:
            case OptionType.NUMBER:
                assert o.number is not None
                return o.number
            case OptionType.YES:
                return 1
            case OptionType.CARD:
                return self._score_card(obs, o, ctx)
            case OptionType.PLAY:
                return self._score_play(obs, o, ctx)
            case OptionType.ATTACH:
                return self._score_attach(obs, o, ctx)
            case OptionType.EVOLVE:
                return self._score_evolve(obs, o, ctx)
            case OptionType.ABILITY:
                return self._score_ability(obs, o, ctx)
            case OptionType.RETREAT:
                return self._score_retreat(obs, o, ctx)
            case OptionType.ATTACK:
                return self._score_attack(o)
            case _:
                return 0

    def post_pick(self, obs: Observation, top_option: Option) -> None:
        """MAINコンテキストでのアクション選択後の状態更新（現状ノーオペ）。"""
        pass
