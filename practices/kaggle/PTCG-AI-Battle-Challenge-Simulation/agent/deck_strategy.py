"""デッキ固有の戦略ロジック（Mega Lucario ex Deck）。

メガルカリオexをメインアタッカーに、ハリテヤマとソルロックをサブに使い分けるデッキ。
"""

from collections import defaultdict

from cg.api import (
    AreaType,
    CardType,
    EnergyType,
    Observation,
    OptionType,
    Pokemon,
    SelectContext,
)

from models import AgentState, GameContext
from utils import card_table, get_card, prize_count, read_deck_csv

# --- カードID定数 ---
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
Basic_Fighting_Energy = 6


class MegaLucarioDeckStrategy:
    OWN_DECK: list[int] = read_deck_csv()

    # --- ポケモン評価 ---

    def _pokemon_score(self, pokemon: Pokemon) -> int:
        data = card_table[pokemon.id]
        score = prize_count(pokemon) * 1000
        score += len(pokemon.energies) * 150
        score += len(pokemon.tools) * 100
        if data.stage2:
            score += 250
        elif data.stage1:
            score += 130
        card_id = pokemon.id
        if card_id in (173, 174, 190, 1071):  # ヤミカラス・ファンロトム・アーマーガアex・ニャースex
            score -= 200
        if card_id == 112 and len(pokemon.energies) >= 1:  # ムンクドリ
            score += 300
        score += pokemon.hp
        return score

    def _energy_score(self, pokemon: Pokemon, active: bool, ctx: GameContext) -> int:
        energy_count = len(pokemon.energies)
        score = 8000
        if active:
            score += 10
        if pokemon.id in (Makuhita, Hariyama):
            if pokemon.id == Hariyama:
                score += 1
            if energy_count < 3:
                score += 100
            if ctx.sub_attacker_ready:
                score -= 50
        elif pokemon.id == Lunatone:
            score -= 100
        elif pokemon.id == Solrock:
            score += 20 if energy_count < 1 else -100
        elif pokemon.id in (Riolu, Mega_Lucario_ex):
            if pokemon.id == Mega_Lucario_ex:
                score += 1
            if energy_count < 2:
                score += 100
            if ctx.main_attacker_ready:
                score -= 50
        return score

    # --- コンテキスト収集 ---

    def collect_context(self, obs: Observation) -> GameContext:
        state = obs.current
        own_index = state.yourIndex
        own_state = state.players[own_index]

        field_counts: defaultdict[int, int] = defaultdict(int)
        hand_counts: defaultdict[int, int] = defaultdict(int)
        discard_counts: defaultdict[int, int] = defaultdict(int)

        main_attacker_ready = False
        sub_attacker_ready = False
        for card in own_state.active + own_state.bench:
            if card is None:
                continue
            field_counts[card.id] += 1
            if card.id in (Makuhita, Hariyama):
                if len(card.energies) >= 3:
                    sub_attacker_ready = True
            elif card.id in (Riolu, Mega_Lucario_ex):
                if len(card.energies) >= 2:
                    main_attacker_ready = True

        for card in own_state.hand:
            hand_counts[card.id] += 1

        for card in own_state.discard:
            discard_counts[card.id] += 1

        stadium_id = 0
        for card in state.stadium:
            stadium_id = card.id

        return GameContext(
            own_index=own_index,
            own_prize=len(own_state.prize),
            field_counts=field_counts,
            hand_counts=hand_counts,
            discard_counts=discard_counts,
            main_attacker_ready=main_attacker_ready,
            sub_attacker_ready=sub_attacker_ready,
            stadium_id=stadium_id,
        )

    # --- 攻撃計画 ---

    def update_attack_plan(self, obs: Observation, ctx: GameContext, state: AgentState) -> None:
        game_state = obs.current
        select = obs.select

        if select.context != SelectContext.MAIN:
            return

        own_index = ctx.own_index
        own_state = game_state.players[own_index]
        op_state = game_state.players[1 - own_index]

        can_switch = False
        can_op_switch = False
        can_use_mega_brave = False
        for o in select.option:
            if o.type == OptionType.PLAY:
                card = get_card(obs, AreaType.HAND, o.index, own_index)
                if card.id == Switch:
                    can_switch = True
                elif card.id == Boss_Orders:
                    can_op_switch = True
            elif o.type == OptionType.EVOLVE:
                card = get_card(obs, AreaType.HAND, o.index, own_index)
                if card.id == Hariyama:
                    can_op_switch = True
            elif o.type == OptionType.RETREAT:
                can_switch = True
            elif o.type == OptionType.ATTACK:
                ctx.can_attack = True
                if o.attackId == 983:  # メガブレイブ
                    can_use_mega_brave = True

        if game_state.turn < 2:
            return

        own_cards = [own_state.active[0]] + list(own_state.bench)
        op_cards = [op_state.active[0]] + list(op_state.bench)
        best_score = -1

        for i, own_pokemon in enumerate(own_cards):
            if i != 0 and not can_switch:
                break
            for a in range(2):
                energy_required = 0
                base_damage = 0
                base_score = 0
                if own_pokemon.id == Mega_Lucario_ex:
                    if a == 0:
                        energy_required = 1
                        base_damage = 130
                        base_score += 60 * min(3, ctx.discard_counts[Basic_Fighting_Energy])
                    else:
                        energy_required = 2
                        base_damage = 270
                    if ctx.own_prize in (2, 3):
                        base_score -= 500
                elif a == 1:
                    break
                elif own_pokemon.id == Hariyama:
                    energy_required = 3
                    base_damage = 210
                elif own_pokemon.id == Makuhita:
                    for o in select.option:
                        if o.type == OptionType.EVOLVE:
                            index = o.inPlayIndex + (1 if o.inPlayArea == AreaType.BENCH else 0)
                            if index == i:
                                break
                    else:
                        break
                    base_score -= 100
                    energy_required = 3
                    base_damage = 210
                elif own_pokemon.id == Solrock:
                    if ctx.field_counts[Lunatone] >= 1:
                        energy_required = 1
                        base_damage = 70

                if base_damage <= 0:
                    continue

                needs_energy_attach = False
                energy_count = len(own_pokemon.energies)
                if a == 1 and i == 0 and energy_count >= 2 and not can_use_mega_brave:
                    break
                if energy_count < energy_required:
                    if ctx.hand_counts[Basic_Fighting_Energy] >= 1 and not game_state.energyAttached:
                        energy_count += 1
                        if energy_count < energy_required:
                            continue
                        else:
                            needs_energy_attach = True
                    else:
                        continue

                for j, op_pokemon in enumerate(op_cards):
                    if j != 0 and not can_op_switch:
                        break
                    damage = base_damage
                    data = card_table[op_pokemon.id]
                    if data.weakness == EnergyType.FIGHTING:
                        damage *= 2
                    elif data.resistance == EnergyType.FIGHTING:
                        damage -= 30
                    score = self._pokemon_score(op_pokemon)
                    prize = prize_count(op_pokemon) if op_pokemon.hp <= damage else 0
                    if op_pokemon.hp > damage:
                        score = int(score * damage / op_pokemon.hp)
                    score += base_score
                    if len(op_state.prize) <= prize:
                        score = 50000
                    if i == 0:
                        score += 220
                    if j == 0:
                        score += 300
                    score += energy_count
                    if best_score < score:
                        best_score = score
                        state.plan.attacker = i
                        state.plan.target = j
                        state.plan.attack_index = a
                        state.plan.remain_hp = op_pokemon.hp - damage
                        state.plan.needs_energy_attach = needs_energy_attach

    # --- スコアリング（OptionType 別） ---

    def _score_card(self, obs: Observation, o, ctx: GameContext, state: AgentState) -> int:
        card = get_card(obs, o.area, o.index, o.playerIndex)
        if card is None:
            return 0
        game_state = obs.current
        context = obs.select.context
        ec = len(card.energies) if isinstance(card, Pokemon) else 0
        score = 0

        if context in (SelectContext.SWITCH, SelectContext.TO_ACTIVE):
            if o.playerIndex == ctx.own_index:
                score += ec * 2
                if o.index == state.plan.attacker - 1:
                    score += 100
                if card.id == Mega_Lucario_ex:
                    score += 8 if ctx.own_prize in (2, 3) else 20
                elif card.id == Hariyama and ec >= 2:
                    score += 15
                elif card.id == Makuhita and ec >= 2:
                    score += 10
                elif card.id == Solrock:
                    score += 5
                elif card.id == Riolu:
                    score += 4
            else:
                if o.index == state.plan.target - 1:
                    score += 100
        elif context == SelectContext.SETUP_ACTIVE_POKEMON:
            if card.id == Solrock:
                score = 2 if game_state.firstPlayer == ctx.own_index else 4
            elif card.id == Riolu:
                score = 3
            elif card.id == Makuhita:
                score = 1
        elif context == SelectContext.TO_HAND:
            score = 200 - ctx.hand_counts[card.id] * 100
            if card.id == Makuhita:
                score += 10 if ctx.field_counts[card.id] < 1 else -10
            elif card.id == Hariyama:
                score += 20 if ctx.field_counts[Makuhita] >= 1 else -20
            elif card.id == Lunatone:
                score += 60 if ctx.field_counts[card.id] < 1 else -250
            elif card.id == Solrock:
                score += 50 if ctx.field_counts[card.id] < 1 else -250
            elif card.id == Riolu:
                total = ctx.field_counts[card.id] + ctx.field_counts[Mega_Lucario_ex]
                score += -150 if total >= 2 else -3 if total >= 1 else 40
            elif card.id == Mega_Lucario_ex:
                score += 40 if ctx.field_counts[Riolu] >= 1 else -15
            elif card.id == Basic_Fighting_Energy:
                score += 30 if not state.ability_used or not game_state.energyAttached else -1
        elif context == SelectContext.ATTACH_FROM:
            score = self._energy_score(card, o.area == AreaType.ACTIVE, ctx)

        return score

    def _score_play(self, obs: Observation, o, ctx: GameContext, state: AgentState) -> int:
        card = get_card(obs, AreaType.HAND, o.index, ctx.own_index)
        data = card_table[card.id]

        if data.cardType == CardType.POKEMON:
            if card.id in (Lunatone, Solrock):
                return -1 if ctx.field_counts[card.id] >= 1 else 20000
            if card.id == Riolu:
                return -1 if ctx.field_counts[card.id] + ctx.field_counts[Mega_Lucario_ex] >= 2 else 20000
            return 20000

        if card.id == Switch:
            return 6000 if state.plan.attacker > 0 else -1
        if card.id == Premium_Power_Pro:
            game_state = obs.current
            if game_state.supporterPlayed and state.plan.remain_hp <= 0:
                return -1
            if not ctx.can_attack:
                if (
                    not game_state.supporterPlayed
                    and ctx.hand_counts[Carmine] > 0
                    and ctx.hand_counts[Lillie_Determination] == 0
                ):
                    return 3050
                return -1
            return 5000
        if card.id == Boss_Orders:
            return 3200 if state.plan.target >= 1 else -1
        if card.id == Carmine:
            return 3000
        if card.id == Lillie_Determination:
            return 3100
        if card.id == Gravity_Mountain:
            return -1 if ctx.stadium_id == 0 else 10000
        return 10000

    def _score_attach(self, obs: Observation, o, ctx: GameContext, state: AgentState) -> int:
        card = get_card(obs, AreaType.HAND, o.index, ctx.own_index)
        pokemon = get_card(obs, o.inPlayArea, o.inPlayIndex, ctx.own_index)

        if card.id == Hero_Cape:
            score = 7000
            if pokemon.id == Riolu:
                score += 100
            elif pokemon.id == Mega_Lucario_ex:
                score += 200
            return score

        score = self._energy_score(pokemon, o.inPlayArea == AreaType.ACTIVE, ctx)
        if o.inPlayArea == AreaType.ACTIVE:
            if state.plan.attacker == 0 and state.plan.needs_energy_attach:
                score += 200
        else:
            if state.plan.attacker == 1 + o.inPlayIndex and state.plan.needs_energy_attach:
                score += 200
        return score

    def _score_evolve(self, obs: Observation, o, ctx: GameContext, state: AgentState) -> int:
        pokemon = get_card(obs, o.inPlayArea, o.inPlayIndex, ctx.own_index)
        if pokemon.id == Makuhita and state.plan.target == 0:
            return -1
        return 9000 + len(pokemon.energies)

    def _score_ability(self, obs: Observation, o, ctx: GameContext) -> int:
        card = get_card(obs, o.area, o.index, ctx.own_index)
        return 1 if card.id == 1267 else 30000  # 1267: ルミオスシティ

    def _score_attack(self, o, state: AgentState) -> int:
        score = 1000
        is_mega_brave = o.attackId == 983  # メガブレイブ
        score += 100 if (state.plan.attack_index == 1) == is_mega_brave else 0
        return score

    def score_option(self, obs: Observation, o, ctx: GameContext, state: AgentState) -> int:
        """OptionType に応じてスコア関数をディスパッチする。"""
        match o.type:
            case OptionType.NUMBER:
                return o.number
            case OptionType.YES:
                return 1
            case OptionType.CARD:
                return self._score_card(obs, o, ctx, state)
            case OptionType.PLAY:
                return self._score_play(obs, o, ctx, state)
            case OptionType.ATTACH:
                return self._score_attach(obs, o, ctx, state)
            case OptionType.EVOLVE:
                return self._score_evolve(obs, o, ctx, state)
            case OptionType.ABILITY:
                return self._score_ability(obs, o, ctx)
            case OptionType.RETREAT:
                return 2000 if state.plan.attacker >= 1 else -1
            case OptionType.ATTACK:
                return self._score_attack(o, state)
            case _:
                return 0

    def post_pick(self, obs: Observation, top_option, state: AgentState) -> None:
        """MAINコンテキストでのアクション選択後に状態を更新する。"""
        if top_option.type == OptionType.ABILITY:
            card = get_card(obs, top_option.area, top_option.index, obs.current.yourIndex)
            if card.id == Lunatone:
                state.ability_used = True
