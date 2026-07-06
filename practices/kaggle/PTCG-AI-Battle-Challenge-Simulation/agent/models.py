"""エージェント全体で共有するデータクラス定義。

デッキ非依存の汎用構造として設計し、deck モジュールが各フィールドを埋める。
"""

from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class AttackPlan:
    """
    1ターンの攻撃計画

    MAINコンテキストで立案し、スコアリングと行動選択に参照する。
    """

    attacker: int = -1  # 攻撃するポケモンの位置（0=バトル場, 1以降=ベンチ）
    target: int = -1  # 攻撃対象の位置（0=バトル場, 1以降=ベンチ）
    attack_index: int = -1  # 使うワザのインデックス（0 or 1）
    remain_hp: int = -1  # 攻撃後の相手残りHP（負なら倒せる）
    needs_energy_attach: bool = False  # そのターン手張りが必要かどうか


@dataclass
class GameContext:
    """1回の agent() 呼び出しで収集するターン内状態"""

    own_index: int
    own_prize: int
    field_counts: defaultdict[int, int]
    hand_counts: defaultdict[int, int]
    discard_counts: defaultdict[int, int]
    main_attacker_ready: bool  # メインアタッカーがエネルギー要件を満たしているか
    sub_attacker_ready: bool  # サブアタッカーがエネルギー要件を満たしているか
    stadium_id: int
    can_attack: bool = False


@dataclass
class AgentState:
    """ターンをまたいで維持するセッション状態"""

    plan: AttackPlan = field(default_factory=AttackPlan)
    pre_turn: int = 0
    ability_used: bool = False


class DeckStrategyProtocol(Protocol):
    """デッキ実装が満たすべきインターフェース。

    deck_strategy.py を別デッキに差し替える際はこのプロトコルを実装すること。
    """

    OWN_DECK: list[int]

    def collect_context(self, obs: Any) -> GameContext: ...
    def update_attack_plan(
        self, obs: Any, ctx: GameContext, state: AgentState
    ) -> None: ...
    def score_option(
        self, obs: Any, o: Any, ctx: GameContext, state: AgentState
    ) -> int: ...
    def post_pick(self, obs: Any, top_option: Any, state: AgentState) -> None: ...
