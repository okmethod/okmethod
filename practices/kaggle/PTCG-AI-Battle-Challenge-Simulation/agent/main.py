import random

from cg.api import Observation, to_observation_class

from utils import read_deck_csv


def agent(obs_dict: dict) -> list[int]:
    """ポケモンカードゲームエージェントのメイン関数。

    返すリストの各要素は 0 以上 len(obs.select.option) 未満であること。
    リストの長さは obs.select.minCount 以上 obs.select.maxCount 以下であること（重複不可）。

    Args:
        obs_dict: 現在のゲーム状態（盤面・選択肢・ログを含む辞書）
    Returns:
        list[int]: 選択するオプションのインデックスリスト
    """

    obs: Observation = to_observation_class(obs_dict)
    if obs.select is None:
        return read_deck_csv()

    return random.sample(list(range(len(obs.select.option))), obs.select.maxCount)
