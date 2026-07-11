"""デッキ戦略の抽象基底クラス。

score_option / _score_card の共通ディスパッチロジックを Template Method パターンで提供する。
新デッキを追加する際は DeckStrategyBase を継承し、@abstractmethod をすべて実装すること。
"""

import warnings
from abc import ABC, abstractmethod
from collections.abc import Iterator
from typing import final

from cg.api import (
    AreaType,
    Card,
    Observation,
    Option,
    OptionType,
    PlayerState,
    Pokemon,
    SelectContext,
)

from models import AttackCandidate, AttackPlan, DeckWeights, GameContext, ScoreTiers
from utils import card_table, get_card, prize_count, read_deck_csv


def _best_plan_from(candidates: Iterator[AttackCandidate]) -> AttackCandidate | None:
    """candidatesからスコア最大の候補を返す純粋関数。スコアが全て -1 以下なら None。"""
    best_score = -1
    best: AttackCandidate | None = None
    for candidate in candidates:
        if candidate.score > best_score:
            best_score = candidate.score
            best = candidate
    return best


class DeckStrategyBase(ABC):
    """デッキ戦略の抽象基底クラス（Template Method パターン）。

    Protocol の 5 メソッドに対応するブロック構成。
    - 1. 初期化: reset_turn / _reset_turn_state
    - 2. コンテキスト収集: collect_context
    - 3. 攻撃計画立案: plan_attack / _commit_best_plan
    - 4. OptionType 別スコアリング: score_option / _score_xxx / etc.
      - 4a. 共通デフォルト実装（必要に応じて override）
      - 4b. スコア実装（abstract、サブクラスで定義必須）
      - 4c. フック（デフォルト: return 0、必要に応じて override）
    - 5. アクション選択後の状態更新: post_pick

    デッキ固有の abstractmethod をサブクラス側で実装すること。
    """

    # 共通パラメータ：デッキ単位で override 可能
    TIERS: ScoreTiers = ScoreTiers()
    WEIGHTS: DeckWeights = DeckWeights()

    # サブクラスのクラス変数として定義すること
    DECK_RECIPE_PATH: str

    def __init__(self) -> None:
        self._plan = AttackPlan()
        self.OWN_DECK = read_deck_csv(self.DECK_RECIPE_PATH)

    # --- 1. 初期化 ---

    @final
    def reset_turn(self) -> None:
        """ターン開始時に攻撃計画をリセットし、デッキ固有の状態リセットを呼ぶ。"""
        self._plan = AttackPlan()
        self._reset_turn_state()

    def _reset_turn_state(self) -> None:
        """デッキ固有のターン内状態をリセットする。追加状態があるデッキでは override する。"""
        pass

    # --- 2. コンテキスト収集 ---

    @abstractmethod
    def collect_context(self, obs: Observation) -> GameContext: ...

    # --- 3. 攻撃計画立案 ---

    @abstractmethod
    def plan_attack(self, obs: Observation, ctx: GameContext) -> None: ...

    @final
    def _commit_best_plan(self, candidates: Iterator[AttackCandidate]) -> None:
        """スコア最大の候補から _plan を確定する。"""
        if plan := _best_plan_from(candidates):
            self._plan = plan

    # --- 4. OptionType 別スコアリング ---

    @final
    def score_option(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """OptionType に応じてスコア関数をディスパッチする。

        負のスコアを返すと他の選択肢が優先される。
        ただし、全選択肢が負の場合は最高スコアのものが選ばれる。
        """
        match o.type:
            case OptionType.NUMBER:  # 数値指定（カード枚数等）
                assert o.number is not None
                return o.number
            case OptionType.YES:  # Yes 選択（常に Yes）
                return 1
            case OptionType.NO:  # No 選択
                return self._score_no(obs, o, ctx)
            case OptionType.CARD:  # カード選択
                return self._score_card(obs, o, ctx)
            case OptionType.TOOL_CARD:  # ツールカード選択
                return self._score_tool_card(obs, o, ctx)
            case OptionType.ENERGY_CARD:  # エネルギーカード選択
                return self._score_energy_card(obs, o, ctx)
            case OptionType.ENERGY:  # エネルギー選択
                return self._score_energy_option(obs, o, ctx)
            case OptionType.PLAY:  # プレイ（カードを手札から場に出す or 使用する）
                return self._score_play(obs, o, ctx)
            case OptionType.ATTACH:  # アタッチ（カードを手札から場のポケモンに付ける）
                return self._score_attach(obs, o, ctx)
            case OptionType.EVOLVE:  # 進化（カードを手札から場のポケモンに重ねる）
                return self._score_evolve(obs, o, ctx)
            case OptionType.ABILITY:  # 特性（場のポケモンの能力を使う）
                return self._score_ability(obs, o, ctx)
            case OptionType.DISCARD:  # 捨てる（場のカードを捨てる）
                return self._score_discard(obs, o, ctx)
            case OptionType.RETREAT:  # 交代（バトル場のポケモンをベンチと入れ替える）
                return self._score_retreat(obs, o, ctx)
            case OptionType.ATTACK:  # 攻撃（場のポケモンのワザを使う）
                return self._score_attack(obs, o, ctx)
            case OptionType.END:  # ターン終了（ターンを終了する）
                return self._score_end(obs, o, ctx)
            case OptionType.SKILL:  # カード効果（複数効果を処理する際に順番を選択する）
                return self._score_skill(obs, o, ctx)
            case OptionType.SPECIAL_CONDITION:  # 状態異常（付与または回復を選択する）
                return self._score_special_condition(obs, o, ctx)
            case _:  # 存在しないケースのフォールバック（警告のみ）
                warnings.warn(f"Unhandled OptionType: {o.type}", stacklevel=2)
                return 0

    @final
    def _score_card(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """CARD オプションを SelectContext に応じたサブ関数へディスパッチする。"""
        assert o.area is not None and o.playerIndex is not None
        card = get_card(obs, o.area, o.index, o.playerIndex)
        if card is None:
            return 0
        assert obs.select is not None
        match obs.select.context:
            case (
                SelectContext.SWITCH | SelectContext.TO_ACTIVE | SelectContext.TO_BENCH
            ):
                return self._score_card_switch(card, o, ctx)
            case SelectContext.SETUP_ACTIVE_POKEMON | SelectContext.SETUP_BENCH_POKEMON:
                return self._score_card_setup(card, obs, ctx)
            case SelectContext.TO_HAND:
                return self._score_card_to_hand(card, obs, ctx)
            case SelectContext.ATTACH_FROM:
                return self._score_card_attach_from(card, o, ctx)
            case SelectContext.ATTACH_TO | SelectContext.TO_DECK:
                return 0
            case _:
                warnings.warn(
                    f"Unhandled SelectContext: {obs.select.context}", stacklevel=2
                )
                return 0

    @final
    def _score_card_switch(
        self, card: Pokemon | Card, o: Option, ctx: GameContext
    ) -> int:
        """SWITCH / TO_ACTIVE コンテキストでのカードスコア。

        自側は _score_card_switch_own に委譲（各デッキで override）し、
        相手側は攻撃目標と一致するかで点数を付ける。
        """
        if o.playerIndex == ctx.own_index:
            return self._score_card_switch_own(card, o, ctx)
        else:
            # target は全体位置（0=バトル場 / 1以降=ベンチ）、o.index はベンチ内 0-origin
            if o.index != self._plan.target - 1:
                return 0
            assert isinstance(card, Pokemon)  # フィールドには Pokemon しか置けない
            return self._score_opponent_pokemon_priority(card)

    @final
    def _score_card_attach_from(
        self, card: Pokemon | Card, o: Option, ctx: GameContext
    ) -> int:
        """ATTACH_FROM コンテキストでのカードスコア。"""
        if not isinstance(card, Pokemon):
            return 0
        assert o.area is not None
        return self._score_energy(card, o.area == AreaType.ACTIVE, ctx)

    # 4a. 共通デフォルト実装（必要に応じて override）

    def _apply_energy_attach_bonus(self, score: int, o: Option) -> int:
        """攻撃計画のアタッカーへのエネルギー手張りボーナスを加算する。"""
        if o.inPlayArea == AreaType.ACTIVE:
            if self._plan.attacker == 0 and self._plan.needs_energy_attach:
                return score + self.WEIGHTS.energy_attach_bonus
        elif o.inPlayArea is not None:
            assert o.inPlayIndex is not None
            if (
                self._plan.attacker == 1 + o.inPlayIndex
                and self._plan.needs_energy_attach
            ):
                return score + self.WEIGHTS.energy_attach_bonus
        return score

    def _calc_combo_score(
        self,
        damage: int,
        op_pokemon: Pokemon,
        op_state: PlayerState,
        attacker_pos: int,
        target_pos: int,
        bonus: int = 0,
    ) -> int:
        """攻撃者×対象の組み合わせスコアを返す。サブクラスの _generate_plan_candidates から呼ぶ。"""
        score = self._score_opponent_pokemon_priority(op_pokemon)
        prize = prize_count(op_pokemon) if op_pokemon.hp <= damage else 0
        if op_pokemon.hp > damage:
            score = int(score * damage / op_pokemon.hp)
        score += bonus
        if len(op_state.prize) <= prize:
            score = self.TIERS.win
        if attacker_pos == 0:
            score += self.TIERS.active_attacker
        if target_pos == 0:
            score += self.TIERS.active_target
        return score

    def _score_opponent_pokemon_priority(self, pokemon: Pokemon) -> int:
        """相手ポケモンの優先度スコアを返す。"""
        data = card_table[pokemon.id]
        score = prize_count(pokemon) * self.WEIGHTS.prize_score_weight
        score += len(pokemon.energies) * self.WEIGHTS.energy_score_weight
        score += len(pokemon.tools) * self.WEIGHTS.tool_score_weight
        if data.stage2:
            score += self.WEIGHTS.stage2_bonus
        elif data.stage1:
            score += self.WEIGHTS.stage1_bonus
        score += pokemon.hp
        return score

    # 4b. スコア実装（abstract、サブクラスで定義必須）

    @abstractmethod
    def _score_card_switch_own(
        self, card: Pokemon | Card, o: Option, ctx: GameContext
    ) -> int: ...

    @abstractmethod
    def _score_card_setup(
        self, card: Pokemon | Card, obs: Observation, ctx: GameContext
    ) -> int: ...

    @abstractmethod
    def _score_card_to_hand(
        self, card: Pokemon | Card, obs: Observation, ctx: GameContext
    ) -> int: ...

    @abstractmethod
    def _score_energy(
        self, pokemon: Pokemon, active: bool, ctx: GameContext
    ) -> int: ...

    @abstractmethod
    def _score_play(self, obs: Observation, o: Option, ctx: GameContext) -> int: ...

    @final
    def _score_attach(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        score = self._score_attach_raw(obs, o, ctx)
        if score < 0:
            return score
        return self._apply_energy_attach_bonus(score, o)

    @abstractmethod
    def _score_attach_raw(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        """ATTACH オプションのベーススコアを返す。エネルギーボーナス加算前の値。"""
        ...

    @abstractmethod
    def _score_evolve(self, obs: Observation, o: Option, ctx: GameContext) -> int: ...

    @abstractmethod
    def _score_ability(self, obs: Observation, o: Option, ctx: GameContext) -> int: ...

    @abstractmethod
    def _score_retreat(self, obs: Observation, o: Option, ctx: GameContext) -> int: ...

    @abstractmethod
    def _score_attack(self, obs: Observation, o: Option, ctx: GameContext) -> int: ...

    # 4c. フック（デフォルト: return 0、必要に応じて override）

    def _score_no(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        return 0

    def _score_tool_card(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        return 0

    def _score_energy_card(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        return 0

    def _score_energy_option(
        self, obs: Observation, o: Option, ctx: GameContext
    ) -> int:
        return 0

    def _score_discard(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        return 0

    def _score_end(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        return 0

    def _score_skill(self, obs: Observation, o: Option, ctx: GameContext) -> int:
        return 0

    def _score_special_condition(
        self, obs: Observation, o: Option, ctx: GameContext
    ) -> int:
        return 0

    # --- 5. アクション選択後の状態更新 ---

    @abstractmethod
    def post_pick(self, obs: Observation, top_option: Option) -> None: ...
