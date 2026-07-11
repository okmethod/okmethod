from unittest.mock import MagicMock, patch

from deck_strategy_base import DeckStrategyBase, _best_plan_from
from models import AttackCandidate, AttackPlan, DeckWeights

CARD_ID = 1


class _Stub(DeckStrategyBase):
    """DeckStrategyBase のテスト用最小具象クラス。"""

    DECK_RECIPE_PATH = ""

    def __init__(self, weights: DeckWeights | None = None) -> None:
        self._plan = AttackPlan()
        self.OWN_DECK = []
        if weights is not None:
            self.WEIGHTS = weights  # type: ignore[assignment]

    def collect_context(self, obs):  # type: ignore[override]
        return MagicMock()

    def plan_attack(self, obs, ctx) -> None:
        pass

    def _score_card_switch_own(self, card, o, ctx) -> int:
        return 0

    def _score_card_setup(self, card, obs, ctx) -> int:
        return 0

    def _score_card_to_hand(self, card, obs, ctx) -> int:
        return 0

    def _score_energy(self, pokemon, active, ctx) -> int:
        return 0

    def _score_play(self, obs, o, ctx) -> int:
        return 0

    def _score_attach_raw(self, obs, o, ctx) -> int:
        return 0

    def _score_evolve(self, obs, o, ctx) -> int:
        return 0

    def _score_ability(self, obs, o, ctx) -> int:
        return 0

    def _score_retreat(self, obs, o, ctx) -> int:
        return 0

    def _score_attack(self, obs, o, ctx) -> int:
        return 0

    def post_pick(self, obs, top_option) -> None:
        pass


# --- _best_plan_from ---


def test_best_plan_from_empty_returns_none():
    assert _best_plan_from(iter([])) is None


def test_best_plan_from_all_negative_returns_none():
    candidates = [
        AttackCandidate(score=-2),
        AttackCandidate(score=-1),
    ]
    assert _best_plan_from(iter(candidates)) is None


def test_best_plan_from_zero_score_is_returned():
    """スコア 0 は閾値 -1 を超えるので返される（境界値）。"""
    candidate = AttackCandidate(score=0)
    assert _best_plan_from(iter([candidate])) is candidate


def test_best_plan_from_returns_highest_score():
    low = AttackCandidate(score=10)
    high = AttackCandidate(score=50)
    mid = AttackCandidate(score=30)
    assert _best_plan_from(iter([low, high, mid])) is high


# --- _score_opponent_pokemon_priority ---


def _card_data(stage1: bool = False, stage2: bool = False) -> MagicMock:
    data = MagicMock()
    data.stage1 = stage1
    data.stage2 = stage2
    return data


def _pokemon(hp: int, num_energies: int = 0, num_tools: int = 0) -> MagicMock:
    p = MagicMock()
    p.id = CARD_ID
    p.hp = hp
    p.energies = [MagicMock()] * num_energies
    p.tools = [MagicMock()] * num_tools
    return p


def test_score_opponent_pokemon_priority_basic():
    """サイド1枚・エネルギー/ツールなし・進化なし の基本スコア。"""
    weights = DeckWeights()
    stub = _Stub(weights)
    with (
        patch("deck_strategy_base.card_table", {CARD_ID: _card_data()}),
        patch("deck_strategy_base.prize_count", return_value=1),
    ):
        score = stub._score_opponent_pokemon_priority(_pokemon(hp=100))
    assert score == 1 * weights.prize_score_weight + 100


def test_score_opponent_pokemon_priority_with_energies_and_tools():
    weights = DeckWeights()
    stub = _Stub(weights)
    with (
        patch("deck_strategy_base.card_table", {CARD_ID: _card_data()}),
        patch("deck_strategy_base.prize_count", return_value=1),
    ):
        score = stub._score_opponent_pokemon_priority(
            _pokemon(hp=80, num_energies=2, num_tools=1)
        )
    expected = (
        1 * weights.prize_score_weight
        + 2 * weights.energy_score_weight
        + 1 * weights.tool_score_weight
        + 80
    )
    assert score == expected


def test_score_opponent_pokemon_priority_stage1_bonus():
    weights = DeckWeights()
    stub = _Stub(weights)
    with (
        patch("deck_strategy_base.card_table", {CARD_ID: _card_data(stage1=True)}),
        patch("deck_strategy_base.prize_count", return_value=1),
    ):
        score = stub._score_opponent_pokemon_priority(_pokemon(hp=90))
    assert score == 1 * weights.prize_score_weight + weights.stage1_bonus + 90


def test_score_opponent_pokemon_priority_stage2_bonus():
    weights = DeckWeights()
    stub = _Stub(weights)
    with (
        patch("deck_strategy_base.card_table", {CARD_ID: _card_data(stage2=True)}),
        patch("deck_strategy_base.prize_count", return_value=1),
    ):
        score = stub._score_opponent_pokemon_priority(_pokemon(hp=120))
    assert score == 1 * weights.prize_score_weight + weights.stage2_bonus + 120


def test_score_opponent_pokemon_priority_stage2_beats_stage1():
    """stage1 と stage2 が同時に True の場合、stage2 ボーナスが優先される。"""
    weights = DeckWeights()
    stub = _Stub(weights)
    with (
        patch(
            "deck_strategy_base.card_table",
            {CARD_ID: _card_data(stage1=True, stage2=True)},
        ),
        patch("deck_strategy_base.prize_count", return_value=1),
    ):
        score = stub._score_opponent_pokemon_priority(_pokemon(hp=100))
    assert score == 1 * weights.prize_score_weight + weights.stage2_bonus + 100


def test_score_opponent_pokemon_priority_ex_two_prizes():
    """EX ポケモンはサイド2枚分でスコアが上がる。"""
    weights = DeckWeights()
    stub = _Stub(weights)
    with (
        patch("deck_strategy_base.card_table", {CARD_ID: _card_data()}),
        patch("deck_strategy_base.prize_count", return_value=2),
    ):
        score = stub._score_opponent_pokemon_priority(_pokemon(hp=200))
    assert score == 2 * weights.prize_score_weight + 200


def test_score_opponent_pokemon_priority_custom_weights():
    weights = DeckWeights(prize_score_weight=500, energy_score_weight=50)
    stub = _Stub(weights)
    with (
        patch("deck_strategy_base.card_table", {CARD_ID: _card_data()}),
        patch("deck_strategy_base.prize_count", return_value=2),
    ):
        score = stub._score_opponent_pokemon_priority(_pokemon(hp=150, num_energies=3))
    assert score == 2 * 500 + 3 * 50 + 150
