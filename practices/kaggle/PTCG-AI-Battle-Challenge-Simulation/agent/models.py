"""エージェント全体で共有するデータクラス定義。

デッキ非依存の汎用構造として設計し、deck_strategy モジュールが各フィールドを埋める。
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Protocol

from cg.api import Observation, Option


@dataclass
class GameContext:
    """agent() 呼び出しごとに obs から収集する盤面スナップショット。

    フィールドの概念はどのデッキにも共通だが、
    「何をもって main_attacker_ready とするか」などの判定は
    collect_context() 内のデッキ固有ロジックで行う。使わないフィールドは無視してよい。
    """

    own_index: int
    own_prize: int
    field_counts: defaultdict[int, int]
    hand_counts: defaultdict[int, int]
    discard_counts: defaultdict[int, int]
    stadium_id: int
    main_attacker_ready: bool  # メインアタッカーがエネルギー要件を満たしているか
    sub_attacker_ready: bool  # サブアタッカーがエネルギー要件を満たしているか
    conserve_energy: bool = False  # エネルギー付与を抑制するか（エネルギー充足済み等）
    can_attack: bool = False


@dataclass
class ScoreTiers:
    """アクション種別間の優先度ティア。DeckStrategyBase.TIERS として設定する。"""

    win: int = 50_000
    ability: int = 30_000
    play_pokemon: int = 20_000
    play_trainer: int = 10_000
    evolve_base: int = 9_000
    energy_base: int = 8_000
    retreat_base: int = 2_000
    attack: int = 1_000
    active_attacker: int = 220
    active_target: int = 300


@dataclass
class DeckWeights:
    """デッキスコア計算の重みパラメータ。DeckStrategyBase.WEIGHTS として設定する。"""

    energy_attach_bonus: int = 200
    prize_score_weight: int = 1_000
    energy_score_weight: int = 150
    tool_score_weight: int = 100
    stage2_bonus: int = 250
    stage1_bonus: int = 130


@dataclass
class AttackPlan:
    """1ターンの攻撃計画。

    update_attack_plan() で立案し score_option() で参照する。
    """

    attacker: int = -1  # 攻撃するポケモンの位置（0=バトル場, 1以降=ベンチ）
    target: int = -1  # 攻撃対象の位置（0=バトル場, 1以降=ベンチ）
    attack_index: int = -1  # 使うワザのインデックス（0 or 1）
    remain_hp: int = -1  # 攻撃後の相手残りHP（負なら倒せる）
    needs_energy_attach: bool = False  # そのターン手張りが必要かどうか


@dataclass
class AttackCandidate(AttackPlan):
    """AttackPlan に評価スコアを付加した候補。_generate_plan_candidates が yield する。"""

    score: int = field(kw_only=True)


@dataclass(frozen=True)
class PlanFlags:
    """MAINコンテキストで実行可能な行動フラグ"""

    can_switch: bool  # 自側ベンチ切替が可能か
    can_op_switch: bool  # 相手側ベンチ切替が可能か


class DeckStrategyProtocol(Protocol):
    """デッキ実装が満たすべきインターフェース。

    deck_strategy.py を別デッキに差し替える際はこのプロトコルを実装すること。
    """

    OWN_DECK: list[int]

    def reset_turn(self) -> None: ...
    def collect_context(self, obs: Observation) -> GameContext: ...
    def plan_attack(self, obs: Observation, ctx: GameContext) -> None: ...
    def score_option(self, obs: Observation, o: Option, ctx: GameContext) -> int: ...
    def post_pick(self, obs: Observation, top_option: Option) -> None: ...
