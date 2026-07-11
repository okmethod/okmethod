import pytest
from cg.game import battle_finish, battle_select, battle_start

from decks import DeckStrategy
from main import agent


@pytest.fixture(autouse=True)
def teardown_battle():
    yield
    battle_finish()


def test_battle_completes():
    """同一デッキ同士で1試合完走し、勝敗が確定することを確認する。"""
    deck = DeckStrategy().OWN_DECK
    obs, start_data = battle_start(deck, deck)
    assert obs is not None, f"Battle failed to start: errorType={start_data.errorType}"

    while obs["current"]["result"] == -1:
        action = agent(obs)
        obs = battle_select(action)

    assert obs["current"]["result"] in (0, 1, 2)
