from unittest.mock import MagicMock, patch

from decks import DeckStrategy
from main import agent


# --- デッキ選択フェーズ ---


def test_agent_returns_deck_on_deck_selection():
    """obs.select が None のとき、60枚の int リストを返す。"""
    mock_obs = MagicMock()
    mock_obs.select = None

    with patch("main.to_observation_class", return_value=mock_obs):
        result = agent({})

    assert isinstance(result, list)
    assert len(result) == 60
    assert all(isinstance(card_id, int) for card_id in result)


# --- ターンリセット ---


def test_reset_turn_clears_attack_plan():
    """reset_turn() でターン内の攻撃計画が初期値に戻る。"""
    strategy = DeckStrategy()
    strategy._state.plan.attacker = 2
    strategy._state.plan.target = 1
    strategy._state.plan.attack_index = 0
    strategy._state.plan.needs_energy_attach = True

    strategy.reset_turn()

    assert strategy._state.plan.attacker == -1
    assert strategy._state.plan.target == -1
    assert strategy._state.plan.attack_index == -1
    assert strategy._state.plan.needs_energy_attach is False
