from types import SimpleNamespace
from unittest.mock import patch

from cg.api import AreaType, Card, EnergyType, OptionType, Pokemon
from utils import calc_damage, collect_zone_counts, get_card, prize_count, read_deck_csv

_LEGACY_ENERGY_ID = 12
_LILLIE_PEARL_ID = 1172


# --- Helper functions for tests ---


def _make_pokemon(
    pokemon_id: int = 999,
    hp: int = 100,
    energy_cards: list[Card] | None = None,
    tools: list[Card] | None = None,
) -> Pokemon:
    return Pokemon(
        id=pokemon_id,
        serial=0,
        hp=hp,
        maxHp=hp,
        appearThisTurn=False,
        energies=[],
        energyCards=energy_cards or [],
        tools=tools or [],
        preEvolution=[],
    )


def _make_card(card_id: int) -> Card:
    return Card(id=card_id, serial=0, playerIndex=0)


def _make_card_data(
    card_id: int = 999,
    name: str = "TestPokemon",
    weakness: EnergyType | None = None,
    resistance: EnergyType | None = None,
    ex: bool = False,
    mega_ex: bool = False,
) -> SimpleNamespace:
    return SimpleNamespace(
        cardId=card_id,
        name=name,
        weakness=weakness,
        resistance=resistance,
        ex=ex,
        megaEx=mega_ex,
    )


def _make_player_state(
    active: list | None = None,
    bench: list | None = None,
    hand: list | None = None,
    discard: list | None = None,
    prize: list | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        active=active if active is not None else [None],
        bench=bench or [],
        hand=hand or [],
        discard=discard or [],
        prize=prize or [],
    )


def _make_obs(
    players: list | None = None,
    stadium: list | None = None,
    looking: list | None = None,
    select: SimpleNamespace | None = None,
) -> SimpleNamespace:
    return SimpleNamespace(
        current=SimpleNamespace(
            players=players or [_make_player_state(), _make_player_state()],
            stadium=stadium or [],
            looking=looking,
        ),
        select=select,
    )


# --- Tests ---


class TestReadDeckCsv:
    """read_deck_csv() のテスト。CSV から正しくカードIDリストが読み込まれるかを確認する。"""

    def test_returns_60_card_ids(self):
        result = read_deck_csv("decks/mega_lucario/deck_recipe.csv")
        assert len(result) == 60

    def test_all_elements_are_int(self):
        result = read_deck_csv("decks/mega_lucario/deck_recipe.csv")
        assert all(isinstance(card_id, int) for card_id in result)


class TestCalcDamage:
    """calc_damage() のテスト。弱点・抵抗の補正が正しく適用されるかを確認する。"""

    def test_no_weakness_no_resistance(self):
        pokemon = _make_pokemon()
        data = _make_card_data()
        with patch.dict("utils.card_table", {999: data}):
            assert calc_damage(100, pokemon, EnergyType.FIGHTING) == 100

    def test_weakness_doubles_damage(self):
        pokemon = _make_pokemon()
        data = _make_card_data(weakness=EnergyType.FIGHTING)
        with patch.dict("utils.card_table", {999: data}):
            assert calc_damage(100, pokemon, EnergyType.FIGHTING) == 200

    def test_resistance_reduces_damage_by_30(self):
        pokemon = _make_pokemon()
        data = _make_card_data(resistance=EnergyType.FIGHTING)
        with patch.dict("utils.card_table", {999: data}):
            assert calc_damage(100, pokemon, EnergyType.FIGHTING) == 70

    def test_different_attacker_type_no_modifier(self):
        """弱点・抵抗が Fighting でも攻撃タイプが Water なら補正なし。"""
        pokemon = _make_pokemon()
        data = _make_card_data(
            weakness=EnergyType.FIGHTING, resistance=EnergyType.FIGHTING
        )
        with patch.dict("utils.card_table", {999: data}):
            assert calc_damage(100, pokemon, EnergyType.WATER) == 100


class TestPrizeCount:
    """prize_count() のテスト。Legacy Energy や Lillie & Pearl の補正が正しく適用されるかを確認する。"""

    def test_normal_pokemon_gives_1_prize(self):
        pokemon = _make_pokemon()
        data = _make_card_data()
        with patch.dict("utils.card_table", {999: data}):
            assert prize_count(pokemon) == 1

    def test_ex_pokemon_gives_2_prizes(self):
        pokemon = _make_pokemon()
        data = _make_card_data(ex=True)
        with patch.dict("utils.card_table", {999: data}):
            assert prize_count(pokemon) == 2

    def test_mega_ex_pokemon_gives_3_prizes(self):
        pokemon = _make_pokemon()
        data = _make_card_data(ex=True, mega_ex=True)
        with patch.dict("utils.card_table", {999: data}):
            assert prize_count(pokemon) == 3

    def test_legacy_energy_reduces_prize_by_1(self):
        pokemon = _make_pokemon(energy_cards=[_make_card(_LEGACY_ENERGY_ID)])
        data = _make_card_data(ex=True, mega_ex=True)
        with patch.dict("utils.card_table", {999: data}):
            assert prize_count(pokemon) == 2  # 3 - 1

    def test_lillie_pearl_reduces_prize_when_name_matches(self):
        pokemon = _make_pokemon(tools=[_make_card(_LILLIE_PEARL_ID)])
        data = _make_card_data(name="Lillie's Pokemon", ex=True)
        with patch.dict("utils.card_table", {999: data}):
            assert prize_count(pokemon) == 1  # 2 - 1

    def test_lillie_pearl_no_effect_when_name_not_lillie(self):
        pokemon = _make_pokemon(tools=[_make_card(_LILLIE_PEARL_ID)])
        data = _make_card_data(name="Pikachu", ex=True)
        with patch.dict("utils.card_table", {999: data}):
            assert prize_count(pokemon) == 2  # 補正なし

    def test_prize_count_floor_is_zero(self):
        """Legacy Energy 複数枚でもサイド枚数は 0 未満にならない。"""
        pokemon = _make_pokemon(
            energy_cards=[_make_card(_LEGACY_ENERGY_ID), _make_card(_LEGACY_ENERGY_ID)]
        )
        data = _make_card_data()  # 通常ポケモン (count=1) - 2 = -1 → max(0,-1)=0
        with patch.dict("utils.card_table", {999: data}):
            assert prize_count(pokemon) == 0


class TestGetCard:
    """get_card() のテスト。各エリアから正しいカードを取得できるかを確認する。"""

    def test_returns_none_when_index_is_none(self):
        obs = _make_obs()
        assert get_card(obs, AreaType.HAND, None, 0) is None

    def test_hand(self):
        card = _make_card(100)
        obs = _make_obs(players=[_make_player_state(hand=[card]), _make_player_state()])
        assert get_card(obs, AreaType.HAND, 0, 0) is card

    def test_active(self):
        pokemon = _make_pokemon(111)
        obs = _make_obs(
            players=[_make_player_state(active=[pokemon]), _make_player_state()]
        )
        assert get_card(obs, AreaType.ACTIVE, 0, 0) is pokemon

    def test_bench(self):
        pokemon = _make_pokemon(222)
        obs = _make_obs(
            players=[_make_player_state(bench=[pokemon]), _make_player_state()]
        )
        assert get_card(obs, AreaType.BENCH, 0, 0) is pokemon

    def test_discard(self):
        card = _make_card(333)
        obs = _make_obs(
            players=[_make_player_state(discard=[card]), _make_player_state()]
        )
        assert get_card(obs, AreaType.DISCARD, 0, 0) is card

    def test_stadium(self):
        card = _make_card(400)
        obs = _make_obs(stadium=[card])
        assert get_card(obs, AreaType.STADIUM, 0, 0) is card

    def test_deck(self):
        card = _make_card(500)
        obs = _make_obs(select=SimpleNamespace(deck=[card]))
        assert get_card(obs, AreaType.DECK, 0, 0) is card


class TestCollectZoneCounts:
    """collect_zone_counts() のテスト。各エリアのカード枚数が正しく集計されるかを確認する。"""

    def test_field_counts_aggregates_active_and_bench(self):
        p1 = _make_pokemon(100)
        p2 = _make_pokemon(100)  # 同一ID
        p3 = _make_pokemon(200)
        obs = _make_obs(
            players=[
                _make_player_state(active=[p1], bench=[p2, p3]),
                _make_player_state(),
            ]
        )
        field_counts, _, _, _, _ = collect_zone_counts(obs, 0)
        assert field_counts[100] == 2
        assert field_counts[200] == 1

    def test_none_in_active_is_skipped(self):
        obs = _make_obs(
            players=[_make_player_state(active=[None]), _make_player_state()]
        )
        field_counts, _, _, _, _ = collect_zone_counts(obs, 0)
        assert len(field_counts) == 0

    def test_hand_counts(self):
        cards = [_make_card(10), _make_card(10), _make_card(20)]
        obs = _make_obs(players=[_make_player_state(hand=cards), _make_player_state()])
        _, hand_counts, _, _, _ = collect_zone_counts(obs, 0)
        assert hand_counts[10] == 2
        assert hand_counts[20] == 1

    def test_discard_counts(self):
        cards = [_make_card(30), _make_card(40)]
        obs = _make_obs(
            players=[_make_player_state(discard=cards), _make_player_state()]
        )
        _, _, discard_counts, _, _ = collect_zone_counts(obs, 0)
        assert discard_counts[30] == 1
        assert discard_counts[40] == 1

    def test_stadium_id_is_extracted(self):
        obs = _make_obs(stadium=[_make_card(999)])
        _, _, _, stadium_id, _ = collect_zone_counts(obs, 0)
        assert stadium_id == 999

    def test_stadium_id_is_zero_when_empty(self):
        obs = _make_obs()
        _, _, _, stadium_id, _ = collect_zone_counts(obs, 0)
        assert stadium_id == 0

    def test_can_attack_true_when_attack_option_exists(self):
        option = SimpleNamespace(type=OptionType.ATTACK)
        obs = _make_obs(select=SimpleNamespace(option=[option]))
        _, _, _, _, can_attack = collect_zone_counts(obs, 0)
        assert can_attack is True

    def test_can_attack_false_when_select_is_none(self):
        obs = _make_obs(select=None)
        _, _, _, _, can_attack = collect_zone_counts(obs, 0)
        assert can_attack is False
