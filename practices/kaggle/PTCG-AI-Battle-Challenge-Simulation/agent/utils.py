"""共通ユーティリティ。

cg ライブラリが提供しない補完機能（card_table / get_card / prize_count）と、
Kaggle 実行環境への対応（read_deck_csv）をまとめる。
"""

import os
from collections import defaultdict

from cg.api import (
    AreaType,
    Card,
    EnergyType,
    Observation,
    OptionType,
    Pokemon,
    all_card_data,
)

# ゲームルールに関わるカードID定数
_LEGACY_ENERGY_ID = 12  # レガシーエネルギー
_LILLIE_PEARL_ID = 1172  # リーリエのしんじゅ

# グローバル変数: カードIDからカードデータへのマッピング
card_table = {c.cardId: c for c in all_card_data()}


def read_deck_csv(path: str = "deck_recipe.csv") -> list[int]:
    """deck.csv を読み込んでカードIDのリストを返す。

    Args:
        path: CSV ファイルのパス（デフォルト: deck_recipe.csv）。
              各デッキパッケージは自身の CSV パスを渡す。
    Returns:
        list[int]: デッキに含まれるカードIDのリスト（60枚）。
    """
    agent_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(agent_dir, path)
    if not os.path.exists(file_path):
        file_path = "/kaggle_simulations/agent/" + path
    with open(file_path, "r") as file:
        csv = file.read().split("\n")
    return [int(csv[i]) for i in range(60)]


def get_card(
    obs: Observation, area: AreaType, index: int | None, player_index: int
) -> Pokemon | Card | None:
    """指定ゾーンからカードまたはポケモンを取得する。

    Args:
        obs: 現在の観測オブジェクト
        area: 取得対象のゾーン
        index: ゾーン内のインデックス
        player_index: プレイヤーのインデックス（0 or 1）
    Returns:
        Pokemon | Card | None: 該当するカード（対応するゾーンがない場合は None）
    """
    if index is None:
        return None
    assert obs.current is not None
    ps = obs.current.players[player_index]
    match area:
        case AreaType.DECK:
            assert obs.select is not None and obs.select.deck is not None
            return obs.select.deck[index]
        case AreaType.HAND:
            assert ps.hand is not None
            return ps.hand[index]
        case AreaType.DISCARD:
            return ps.discard[index]
        case AreaType.ACTIVE:
            return ps.active[index]
        case AreaType.BENCH:
            return ps.bench[index]
        case AreaType.PRIZE:
            return ps.prize[index]
        case AreaType.STADIUM:
            assert obs.current.stadium is not None
            return obs.current.stadium[index]
        case AreaType.LOOKING:
            assert obs.current.looking is not None
            return obs.current.looking[index]
        case _:
            return None


def calc_damage(
    base_damage: int, op_pokemon: Pokemon, attacker_type: EnergyType
) -> int:
    """弱点・抵抗力を適用した実ダメージを返す。"""
    data = card_table[op_pokemon.id]
    if data.weakness == attacker_type:
        return base_damage * 2
    if data.resistance == attacker_type:
        return base_damage - 30
    return base_damage


def collect_zone_counts(
    obs: Observation, own_index: int
) -> tuple[
    defaultdict[int, int], defaultdict[int, int], defaultdict[int, int], int, bool
]:
    """フィールド・手札・捨て札のカード枚数、スタジアムID、攻撃可否を返す。"""
    assert obs.current is not None
    game_state = obs.current
    own_state = game_state.players[own_index]

    field_counts: defaultdict[int, int] = defaultdict(int)
    hand_counts: defaultdict[int, int] = defaultdict(int)
    discard_counts: defaultdict[int, int] = defaultdict(int)

    for field_card in own_state.active + own_state.bench:
        if field_card is not None:
            field_counts[field_card.id] += 1

    assert own_state.hand is not None
    for hand_card in own_state.hand:
        hand_counts[hand_card.id] += 1

    for discard_card in own_state.discard:
        discard_counts[discard_card.id] += 1

    stadium_id = 0
    for stadium_card in game_state.stadium:
        stadium_id = stadium_card.id

    can_attack = obs.select is not None and any(
        o.type == OptionType.ATTACK for o in obs.select.option
    )

    return field_counts, hand_counts, discard_counts, stadium_id, can_attack


def prize_count(pokemon: Pokemon) -> int:
    """ポケモンが倒された時に相手が取るサイドの枚数を返す。"""
    data = card_table[pokemon.id]
    count = 3 if data.megaEx else 2 if data.ex else 1
    for card in pokemon.energyCards:
        if card.id == _LEGACY_ENERGY_ID:
            count -= 1
    for card in pokemon.tools:
        if card.id == _LILLIE_PEARL_ID and "Lillie" in data.name:
            count -= 1
    return max(0, count)
