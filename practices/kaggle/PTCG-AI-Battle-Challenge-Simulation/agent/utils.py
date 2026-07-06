"""共通ユーティリティ。

cg ライブラリが提供しない補完機能（card_table / get_card / prize_count）と、
Kaggle 実行環境への対応（read_deck_csv）をまとめる。
"""

import os

from cg.api import AreaType, Card, Observation, Pokemon, all_card_data

# ゲームルールに関わるカードID定数
_LEGACY_ENERGY_ID = 12  # レガシーエネルギー
_LILLIE_PEARL_ID = 1172  # リーリエのしんじゅ

# グローバル変数: カードIDからカードデータへのマッピング
card_table = {c.cardId: c for c in all_card_data()}


def read_deck_csv() -> list[int]:
    """deck.csv を読み込んでカードIDのリストを返す。

    Returns:
        list[int]: デッキに含まれるカードIDのリスト（60枚）。
    """
    file_path = "deck_recipe.csv"
    if not os.path.exists(file_path):
        file_path = "/kaggle_simulations/agent/" + file_path
    with open(file_path, "r") as file:
        csv = file.read().split("\n")
    return [int(csv[i]) for i in range(60)]


def get_card(
    obs: Observation, area: AreaType, index: int, player_index: int
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
    ps = obs.current.players[player_index]
    match area:
        case AreaType.DECK:
            return obs.select.deck[index]
        case AreaType.HAND:
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
            return obs.current.stadium[index]
        case AreaType.LOOKING:
            return obs.current.looking[index]
        case _:
            return None


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
