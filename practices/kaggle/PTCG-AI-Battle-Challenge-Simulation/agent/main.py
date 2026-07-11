"""エージェントのエントリポイント。

ターン管理とフロー制御のみを担い、デッキ固有ロジックは deck_strategy モジュールに委譲する。
"""

from cg.api import Observation, SelectContext, to_observation_class

from decks import DeckStrategy
from models import DeckStrategyProtocol

# グローバル変数: ターン変化の検出
_pre_turn: int = 0

# グローバル変数: デッキ固有戦略の実装クラス
_deck: DeckStrategyProtocol = DeckStrategy()


def agent(obs_dict: dict) -> list[int]:
    """ポケモンカードゲームエージェントのメイン関数。

    返すリストの各要素は 0 以上 len(obs.select.option) 未満であること。
    リストの長さは obs.select.minCount 以上 obs.select.maxCount 以下であること（重複不可）。
    """
    global _pre_turn, _deck

    obs: Observation = to_observation_class(obs_dict)

    # デッキ選択フェーズ: obs.select が None のときだけ呼ばれる
    if obs.select is None:
        return _deck.OWN_DECK

    # 初期化フェーズ: ターンが変わったらターン内状態をリセット
    assert obs.current is not None
    if _pre_turn != obs.current.turn:
        _pre_turn = obs.current.turn
        _deck.reset_turn()

    # 評価フェーズ: コンテキスト収集・攻撃計画立案・スコアリング（デッキ固有）
    ctx = _deck.collect_context(obs)
    _deck.plan_attack(obs, ctx)
    scores = [_deck.score_option(obs, o, ctx) for o in obs.select.option]

    # 行動選択フェーズ: スコア降順で上位 maxCount 件を返す
    select = obs.select
    desc_indices = [
        i for i, _ in sorted(enumerate(scores), key=lambda x: x[1], reverse=True)
    ]
    if select.context == SelectContext.MAIN:
        _deck.post_pick(obs, select.option[desc_indices[0]])
    return desc_indices[: select.maxCount]
