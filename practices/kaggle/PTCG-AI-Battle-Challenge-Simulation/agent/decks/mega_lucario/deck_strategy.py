"""メガルカリオデッキ固有の戦略ロジック。

メガルカリオexをメインアタッカーに、ハリテヤマとソルロックをサブに使い分けるデッキ。
詳細: docs/decks/strategy_mega_lucario.md
"""

from collections.abc import Iterator
from dataclasses import dataclass
from typing import NamedTuple

from cg.api import (
    AreaType,
    Card,
    CardType,
    EnergyType,
    Observation,
    Option,
    OptionType,
    PlayerState,
    Pokemon,
    SelectContext,
    SelectData,
    State,
)

from deck_strategy_base import DeckStrategyBase
from models import AttackCandidate, GameContext, PlanFlags
from utils import (
    calc_damage,
    card_table,
    collect_zone_counts,
    get_card,
)


class AttackConfig(NamedTuple):
    """ポケモンが使用可能な攻撃設定"""

    energy_required: int  # 必要エネルギー枚数
    base_damage: int  # ワザの基本ダメージ
    base_score: int  # 攻撃計画スコアの基本値（コンボボーナスなどを加算する前の値）


@dataclass
class MegaLucarioTurnState:
    """メガルカリオデッキのターン内スコープ状態"""

    lunatone_ability_used: bool = False  # ルナトーン特性を今ターン使用済みかどうか


@dataclass(frozen=True)
class MegaLucarioPlanFlags(PlanFlags):
    """メガルカリオデッキ固有の行動フラグ"""

    can_use_mega_brave: bool  # メガブレイブアタックが使用可能か


class MegaLucarioDeckStrategy(DeckStrategyBase):
    """メガルカリオexデッキの戦略実装。

    DeckStrategyProtocol を満たす具象クラス。
    デッキ固有のカードID定数・スコアリングロジックをここに閉じ込める。
    """

    DECK_RECIPE_PATH = "decks/mega_lucario/deck_recipe.csv"

    # カードID定数（自デッキ）
    Makuhita = 673
    Hariyama = 674
    Lunatone = 675
    Solrock = 676
    Riolu = 677
    Mega_Lucario_ex = 678
    Dusk_Ball = 1102
    Switch = 1123
    Premium_Power_Pro = 1141
    Fighting_Gong = 1142
    Poke_Pad = 1152
    Hero_Cape = 1159
    Boss_Orders = 1182
    Carmine = 1192
    Lillie_Determination = 1227
    Gravity_Mountain = 1252
    Lumiose_City = 1267
    Basic_Fighting_Energy = 6

    # カードID定数（スコアリング対象の相手ポケモン）
    Noctowl = 173
    Fan_Rotom = 174
    Archaludon_ex = 190
    Munkidori = 112
    Meowth_ex = 1071

    # ワザID定数
    Mega_Brave_Attack = 983

    def __init__(self) -> None:
        super().__init__()
        self._state = MegaLucarioTurnState()

    def _reset_turn_state(self) -> None:
        """ターン内状態（ルナトーン特性フラグ）をリセットする。"""
        self._state = MegaLucarioTurnState()

    # --- コンテキスト収集 ---

    def collect_context(self, obs: Observation) -> GameContext:
        """agent() 1回分の盤面スナップショットを収集して GameContext を返す。"""
        assert obs.current is not None
        game_state = obs.current
        own_index = game_state.yourIndex
        own_state = game_state.players[own_index]

        field_counts, hand_counts, discard_counts, stadium_id, can_attack = (
            collect_zone_counts(obs, own_index)
        )

        main_attacker_ready = False
        sub_attacker_ready = False
        for card in own_state.active + own_state.bench:
            if card is None:
                continue
            if card.id in (self.Makuhita, self.Hariyama):
                if len(card.energies) >= 3:
                    sub_attacker_ready = True
            elif card.id in (self.Riolu, self.Mega_Lucario_ex):
                if len(card.energies) >= 2:
                    main_attacker_ready = True

        return GameContext(
            own_index=own_index,
            own_prize=len(own_state.prize),
            field_counts=field_counts,
            hand_counts=hand_counts,
            discard_counts=discard_counts,
            stadium_id=stadium_id,
            main_attacker_ready=main_attacker_ready,
            sub_attacker_ready=sub_attacker_ready,
            can_attack=can_attack,
        )

    # --- 攻撃計画立案 ---

    def _collect_plan_flags(
        self, obs: Observation, own_index: int, select: SelectData
    ) -> MegaLucarioPlanFlags:
        """MAINコンテキストで可能な行動フラグを収集する。"""
        can_switch = False
        can_op_switch = False
        can_use_mega_brave = False
        for o in select.option:
            if o.type == OptionType.PLAY:
                card = get_card(obs, AreaType.HAND, o.index, own_index)
                if card is not None and card.id == self.Switch:
                    can_switch = True
                elif card is not None and card.id == self.Boss_Orders:
                    can_op_switch = True
            elif o.type == OptionType.EVOLVE:
                card = get_card(obs, AreaType.HAND, o.index, own_index)
                if card is not None and card.id == self.Hariyama:
                    can_op_switch = True  # 特性「どすこいキャッチャー」: 進化時に相手ベンチを呼び出せる
            elif o.type == OptionType.RETREAT:
                can_switch = True
            elif o.type == OptionType.ATTACK:
                if o.attackId == self.Mega_Brave_Attack:
                    can_use_mega_brave = True
        return MegaLucarioPlanFlags(can_switch, can_op_switch, can_use_mega_brave)

    def _can_makuhita_evolve(self, position: int, select: SelectData) -> bool:
        """指定位置のマクノシタが今ターン進化できるか判定する。"""
        for o in select.option:
            if o.type != OptionType.EVOLVE or o.inPlayIndex is None:
                continue
            index = o.inPlayIndex + (1 if o.inPlayArea == AreaType.BENCH else 0)
            if index == position:
                return True
        return False

    def _build_attack_configs(
        self,
        own_pokemon: Pokemon,
        i: int,
        ctx: GameContext,
        select: SelectData,
        can_use_mega_brave: bool,
    ) -> list[AttackConfig]:
        """§6 — ポケモンが使用可能な攻撃設定を返す。

        返り値のリスト添字が attackIndex。空リストはこのポケモンで攻撃できないことを意味する。
        """
        if own_pokemon.id == self.Mega_Lucario_ex:
            prize_adj = -500 if ctx.own_prize in (2, 3) else 0
            a0_score = (
                60 * min(3, ctx.discard_counts[self.Basic_Fighting_Energy]) + prize_adj
            )
            configs: list[AttackConfig] = [AttackConfig(1, 130, a0_score)]
            mega_brave_blocked = (
                i == 0 and len(own_pokemon.energies) >= 2 and not can_use_mega_brave
            )
            if not mega_brave_blocked:
                configs.append(AttackConfig(2, 270, prize_adj))
            return configs
        if own_pokemon.id == self.Hariyama:
            return [AttackConfig(3, 210, 0)]
        if own_pokemon.id == self.Makuhita:
            return (
                [AttackConfig(3, 210, -100)]
                if self._can_makuhita_evolve(i, select)
                else []
            )
        if own_pokemon.id == self.Solrock:
            return (
                [AttackConfig(1, 70, 0)] if ctx.field_counts[self.Lunatone] >= 1 else []
            )
        return []

    def plan_attack(self, obs: Observation, ctx: GameContext) -> None:
        """全攻撃者×全対象の組み合わせを総当たりして最善の攻撃計画を _plan に保存する。"""
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
        flags = self._collect_plan_flags(obs, own_index, select)

        own_cards = [own_state.active[0]] + list(own_state.bench)
        op_cards = [op_state.active[0]] + list(op_state.bench)
        self._commit_best_plan(
            self._generate_plan_candidates(
                game_state,
                ctx,
                select,
                own_cards,
                op_cards,
                flags.can_switch,
                flags.can_op_switch,
                flags.can_use_mega_brave,
                op_state,
            )
        )

    def _generate_plan_candidates(
        self,
        game_state: State,
        ctx: GameContext,
        select: SelectData,
        own_cards: list[Pokemon | None],
        op_cards: list[Pokemon | None],
        can_switch: bool,
        can_op_switch: bool,
        can_use_mega_brave: bool,
        op_state: PlayerState,
    ) -> Iterator[AttackCandidate]:
        """攻撃計画候補を列挙する。"""
        for i, own_pokemon in enumerate(own_cards):
            if own_pokemon is None:
                continue
            if i != 0 and not can_switch:
                break
            attack_configs = self._build_attack_configs(
                own_pokemon, i, ctx, select, can_use_mega_brave
            )
            for a, (energy_required, base_damage, base_score) in enumerate(
                attack_configs
            ):
                needs_energy_attach = False
                energy_count = len(own_pokemon.energies)
                if energy_count < energy_required:
                    if (
                        ctx.hand_counts[self.Basic_Fighting_Energy] >= 1
                        and not game_state.energyAttached
                    ):
                        energy_count += 1
                        if energy_count < energy_required:
                            continue
                        else:
                            needs_energy_attach = True
                    else:
                        continue
                for j, op_pokemon in enumerate(op_cards):
                    if op_pokemon is None:
                        continue
                    if j != 0 and not can_op_switch:
                        break
                    damage = calc_damage(base_damage, op_pokemon, EnergyType.FIGHTING)
                    score = (
                        self._calc_combo_score(
                            damage, op_pokemon, op_state, i, j, bonus=base_score
                        )
                        + energy_count
                    )
                    yield AttackCandidate(
                        i,
                        j,
                        a,
                        op_pokemon.hp - damage,
                        needs_energy_attach,
                        score=score,
                    )

    # --- OptionType 別スコアリング ---

    def _score_opponent_pokemon_priority(self, pokemon: Pokemon) -> int:
        """§6 — 相手ポケモンの撃破優先度スコアを返す。

        サイド枚数・エネルギー・進化段階を基準に、特定カードを補正する。
        """
        score = super()._score_opponent_pokemon_priority(pokemon)
        card_id = pokemon.id
        if card_id in (
            self.Noctowl,
            self.Fan_Rotom,
            self.Archaludon_ex,
            self.Meowth_ex,
        ):
            score -= 200
        if card_id == self.Munkidori and len(pokemon.energies) >= 1:
            score += 300
        return score

    def _score_energy(self, pokemon: Pokemon, active: bool, ctx: GameContext) -> int:
        """§4 — エネルギー手張り先ポケモンへのスコアを返す。

        ポケモン種別ごとに必要枚数・アタッカー準備状況を参照して優先度を補正する。
        """
        energy_count = len(pokemon.energies)
        score = self.TIERS.energy_base
        if active:
            score += 10
        if pokemon.id in (self.Makuhita, self.Hariyama):
            if pokemon.id == self.Hariyama:
                score += 1
            if energy_count < 3:
                score += 100
            if ctx.sub_attacker_ready:
                score -= 50
        elif pokemon.id == self.Lunatone:
            score -= 100
        elif pokemon.id == self.Solrock:
            score += 20 if energy_count < 1 else -100
        elif pokemon.id in (self.Riolu, self.Mega_Lucario_ex):
            if pokemon.id == self.Mega_Lucario_ex:
                score += 1
            if energy_count < 2:
                score += 100
            if ctx.main_attacker_ready:
                score -= 50
        return score

    def _score_card_switch_own(
        self, card: Pokemon | Card, o: Option, ctx: GameContext
    ) -> int:
        """§5 — 自側ベンチ切替スコア。次ターンのアタッカー優先で点数を付ける。"""
        ec = len(card.energies) if isinstance(card, Pokemon) else 0
        score = ec * 2
        if o.index == self._plan.attacker - 1:
            score += 100
        if card.id == self.Mega_Lucario_ex:
            score += 8 if ctx.own_prize in (2, 3) else 20
        elif card.id == self.Hariyama and ec >= 2:
            score += 15
        elif card.id == self.Makuhita and ec >= 2:
            score += 10
        elif card.id == self.Solrock:
            score += 5
        elif card.id == self.Riolu:
            score += 4
        return score

    def _score_card_setup(
        self, card: Pokemon | Card, obs: Observation, ctx: GameContext
    ) -> int:
        """§2 — SETUP_ACTIVE_POKEMON（ゲーム開始時バトル場配置）でのカードスコア。

        先攻・後攻によってソルロックの優先度が変わる。
        """
        assert obs.current is not None
        if card.id == self.Solrock:
            return 2 if obs.current.firstPlayer == ctx.own_index else 4
        if card.id == self.Riolu:
            return 3
        if card.id == self.Makuhita:
            return 1
        return 0

    def _score_card_to_hand(
        self, card: Pokemon | Card, obs: Observation, ctx: GameContext
    ) -> int:
        """§7 — TO_HAND コンテキストでのカードスコア。

        フィールド・手札の枚数を見て、過剰になるカードを低優先にする。
        """
        assert obs.current is not None
        score = 200 - ctx.hand_counts[card.id] * 100
        if card.id == self.Makuhita:
            score += 10 if ctx.field_counts[card.id] < 1 else -10
        elif card.id == self.Hariyama:
            score += 20 if ctx.field_counts[self.Makuhita] >= 1 else -20
        elif card.id == self.Lunatone:
            score += 60 if ctx.field_counts[card.id] < 1 else -250
        elif card.id == self.Solrock:
            score += 50 if ctx.field_counts[card.id] < 1 else -250
        elif card.id == self.Riolu:
            total = ctx.field_counts[card.id] + ctx.field_counts[self.Mega_Lucario_ex]
            score += -150 if total >= 2 else -3 if total >= 1 else 40
        elif card.id == self.Mega_Lucario_ex:
            score += 40 if ctx.field_counts[self.Riolu] >= 1 else -15
        elif card.id == self.Basic_Fighting_Energy:
            score += (
                30
                if not self._state.lunatone_ability_used
                or not obs.current.energyAttached
                else -1
            )
        return score

    def _score_play(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """PLAY（手札からカードを場に出す）オプションのスコア。

        カード種別・攻撃計画・サポーター使用済みフラグを参照して優先度を返す。
        """
        card = get_card(obs, AreaType.HAND, o.index, ctx.own_index)
        assert card is not None
        data = card_table[card.id]

        if data.cardType == CardType.POKEMON:
            if card.id in (self.Lunatone, self.Solrock):
                return -1 if ctx.field_counts[card.id] >= 1 else self.TIERS.play_pokemon
            if card.id == self.Riolu:
                return (
                    -1
                    if ctx.field_counts[card.id]
                    + ctx.field_counts[self.Mega_Lucario_ex]
                    >= 2
                    else self.TIERS.play_pokemon
                )
            return self.TIERS.play_pokemon

        if card.id == self.Switch:
            return 6000 if self._plan.attacker > 0 else -1
        if card.id == self.Premium_Power_Pro:
            assert obs.current is not None
            game_state = obs.current
            if game_state.supporterPlayed and self._plan.remain_hp <= 0:
                return -1
            if not ctx.can_attack:
                can_discard_setup = (
                    not game_state.supporterPlayed
                    and ctx.hand_counts[self.Carmine] > 0
                    and ctx.hand_counts[self.Lillie_Determination] == 0
                )
                return 3050 if can_discard_setup else -1
            return 5000
        if card.id == self.Boss_Orders:
            return 3200 if self._plan.target >= 1 else -1
        if card.id == self.Carmine:
            return 3000
        if card.id == self.Lillie_Determination:
            return 3100
        if card.id == self.Gravity_Mountain:
            return (
                -1
                if ctx.stadium_id == self.Gravity_Mountain
                else self.TIERS.play_trainer
            )
        return self.TIERS.play_trainer

    def _score_attach_raw(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """§4 — ATTACH（ツール・エネルギーをポケモンに付ける）オプションのスコア。

        攻撃計画の手張り必要フラグと照合してアタッカーへの付与を優遇する。
        """
        assert o.inPlayArea is not None
        card = get_card(obs, AreaType.HAND, o.index, ctx.own_index)
        pokemon = get_card(obs, o.inPlayArea, o.inPlayIndex, ctx.own_index)
        assert card is not None
        assert pokemon is not None

        if card.id == self.Hero_Cape:
            score = 7000
            if pokemon.id == self.Riolu:
                score += 100
            elif pokemon.id == self.Mega_Lucario_ex:
                score += 200
            return score

        assert isinstance(pokemon, Pokemon)
        return self._score_energy(pokemon, o.inPlayArea == AreaType.ACTIVE, ctx)

    def _score_evolve(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """§3 — EVOLVE（進化）オプションのスコア。

        相手バトルポケモンをマクノシタで倒せる場面では進化を抑制する。
        """
        assert o.inPlayArea is not None
        pokemon = get_card(obs, o.inPlayArea, o.inPlayIndex, ctx.own_index)
        assert pokemon is not None
        if pokemon.id == self.Makuhita and self._plan.target == 0:
            return -1
        assert isinstance(pokemon, Pokemon)
        return self.TIERS.evolve_base + len(pokemon.energies)

    def _score_ability(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """ABILITY（特性）オプションのスコア。

        ルミオスシティジムは手張りの代替手段なので低優先にする。
        """
        assert o.area is not None
        card = get_card(obs, o.area, o.index, ctx.own_index)
        assert card is not None
        return 1 if card.id == self.Lumiose_City else self.TIERS.ability

    def _score_retreat(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """RETREAT オプションのスコア。"""
        return self.TIERS.retreat_base if self._plan.attacker >= 1 else -1

    def _score_attack(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """§7 — ATTACK オプションのスコア。

        攻撃計画で選んだワザインデックスと一致する場合に加点する。
        """
        score = self.TIERS.attack
        is_mega_brave = o.attackId == self.Mega_Brave_Attack
        score += 100 if (self._plan.attack_index == 1) == is_mega_brave else 0
        return score

    # --- アクション選択後の状態更新 ---

    def post_pick(self, obs: Observation, top_option: Option) -> None:
        """MAINコンテキストでのアクション選択後に状態を更新する。"""
        if top_option.type == OptionType.ABILITY:
            assert obs.current is not None
            assert top_option.area is not None
            card = get_card(
                obs, top_option.area, top_option.index, obs.current.yourIndex
            )
            assert card is not None
            if card.id == self.Lunatone:
                self._state.lunatone_ability_used = True
