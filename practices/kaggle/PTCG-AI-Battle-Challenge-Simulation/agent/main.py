"""エージェントのエントリポイント。

ターン管理とフロー制御のみを担い、デッキ固有ロジックは deck モジュールに委譲する。
"""

from cg.api import Observation, SelectContext, to_observation_class

from deck_strategy import MegaLucarioDeckStrategy
from models import AgentState, AttackPlan, DeckStrategyProtocol

# グローバル変数: デッキ固有戦略の実装クラス
_deck: DeckStrategyProtocol = MegaLucarioDeckStrategy()

# グローバル変数: ターンをまたいで維持するセッション状態
_state = AgentState()


def agent(obs_dict: dict) -> list[int]:
    """ポケモンカードゲームエージェントのメイン関数。

    返すリストの各要素は 0 以上 len(obs.select.option) 未満であること。
    リストの長さは obs.select.minCount 以上 obs.select.maxCount 以下であること（重複不可）。
    """
    obs: Observation = to_observation_class(obs_dict)

    # デッキ選択フェーズ: obs.select が None のときだけ呼ばれる
    if obs.select is None:
        return _deck.OWN_DECK

    # 初期化フェーズ: ターンが変わったらターン内状態を初期化
    assert obs.current is not None
    if _state.pre_turn != obs.current.turn:
        _state.pre_turn = obs.current.turn
        _state.plan = AttackPlan()
        _state.ability_used = False

    # 評価フェーズ: コンテキスト収集・攻撃計画立案・スコアリング（デッキ固有）
    ctx = _deck.collect_context(obs)
    _deck.update_attack_plan(obs, ctx, _state)
    scores = [_deck.score_option(obs, o, ctx, _state) for o in obs.select.option]

    # 行動選択フェーズ: スコア降順で上位 maxCount 件を返す
    select = obs.select
    desc_indices = [
        i for i, _ in sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    ]
    if select.context == SelectContext.MAIN:
        _deck.post_pick(obs, select.option[desc_indices[0]], _state)
    return desc_indices[: select.maxCount]
