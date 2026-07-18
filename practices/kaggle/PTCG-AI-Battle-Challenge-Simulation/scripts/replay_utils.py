"""Kaggle リプレイ JSON 分析用ユーティリティ。

caller が sys.path に agent/ を追加済みであること前提。
"""

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from cg.api import AreaType, OptionType, SelectContext


@dataclass
class Replay:
    my_idx: int
    op_idx: int
    my_name: str
    op_name: str
    winner: str
    steps: list
    ctx_map: dict[int, str]
    opt_map: dict[int, str]
    area_map: dict[int, str]


def load_replay(path: str | Path, my_name: str) -> Replay:
    """リプレイ JSON を読み込み、プレイヤー情報とステップを返す。"""
    with open(path) as f:
        d = json.load(f)
    names = [a["Name"] for a in d["info"]["Agents"]]
    my_idx = next(i for i, n in enumerate(names) if n == my_name)
    op_idx = 1 - my_idx
    rewards = d["rewards"]
    winner = names[rewards.index(max(rewards))]
    ctx_map, opt_map, area_map = build_enum_maps()
    return Replay(
        my_idx=my_idx,
        op_idx=op_idx,
        my_name=names[my_idx],
        op_name=names[op_idx],
        winner=winner,
        steps=d["steps"],
        ctx_map=ctx_map,
        opt_map=opt_map,
        area_map=area_map,
    )


def load_card_names(csv_path: str | Path) -> dict[int, str]:
    """JP_Card_Data.csv からカードID→日本語名マップを返す。"""
    result: dict[int, str] = {}
    with open(csv_path, encoding="utf-8") as f:
        for row in csv.DictReader(f):
            result[int(row["カード ID"])] = row["カード名"]
    return result


def build_enum_maps() -> tuple[dict[int, str], dict[int, str], dict[int, str]]:
    """SelectContext / OptionType / AreaType の int→名前マップを返す。"""
    ctx_map = {
        int(v): k
        for k, v in vars(SelectContext).items()
        if isinstance(v, SelectContext)
    }
    opt_map = {
        int(v): k for k, v in vars(OptionType).items() if isinstance(v, OptionType)
    }
    area_map = {int(v): k for k, v in vars(AreaType).items() if isinstance(v, AreaType)}
    return ctx_map, opt_map, area_map


def get_card_from_obs(
    obs: dict,
    area_int: int | None,
    index: int | None,
    player_index: int | None,
    area_map: dict[int, str],
) -> dict | None:
    if area_int is None or index is None or player_index is None:
        return None
    cur = obs.get("current", {})
    sel = obs.get("select", {})
    ps = cur.get("players") or []
    if player_index >= len(ps):
        return None
    p = ps[player_index]
    area_name = area_map.get(area_int, "")
    match area_name:
        case "HAND":
            cards = p.get("hand", []) or []
        case "ACTIVE":
            cards = p.get("active", []) or []
        case "BENCH":
            cards = p.get("bench", []) or []
        case "DISCARD":
            cards = p.get("discard", []) or []
        case "PRIZE":
            cards = p.get("prize", []) or []
        case "DECK":
            cards = (sel or {}).get("deck", []) or []
        case _:
            return None
    return cards[index] if index < len(cards) else None


def fmt_pokemon(p: dict | None, card_name: dict[int, str]) -> str:
    if not p:
        return "(なし)"
    pid = p.get("id")
    hp = p.get("hp", "?")
    dmg = p.get("damage", 0)
    nrg = len(p.get("energies", []))
    name = card_name.get(pid, f"ID:{pid}")
    return f"{name} HP{hp - dmg}/{hp} E×{nrg}"


def fmt_card(c: dict | None, card_name: dict[int, str]) -> str:
    if not c:
        return "(なし)"
    return card_name.get(c.get("id"), f"ID:{c.get('id')}")


def print_board(
    obs: dict,
    my_idx: int,
    op_idx: int,
    card_name: dict[int, str],
    area_map: dict[int, str],
) -> None:
    cur = obs.get("current", {})
    if not cur:
        return
    players = cur.get("players", [])
    if len(players) < 2:
        return
    my = players[my_idx]
    op = players[op_idx]

    my_active = (my.get("active") or [None])[0]
    my_bench = [p for p in (my.get("bench") or []) if p]
    my_hand = my.get("hand") or []
    my_prize = len(my.get("prize") or [])
    op_active = (op.get("active") or [None])[0]
    op_bench = [p for p in (op.get("bench") or []) if p]
    op_prize = len(op.get("prize") or [])

    print(f"  【相手】 サイド残{op_prize}枚")
    print(f"    バトル場: {fmt_pokemon(op_active, card_name)}")
    print(f"    ベンチ  : {[fmt_pokemon(p, card_name) for p in op_bench]}")
    print(f"  【自分】 サイド残{my_prize}枚  手札{len(my_hand)}枚")
    print(f"    バトル場: {fmt_pokemon(my_active, card_name)}")
    print(f"    ベンチ  : {[fmt_pokemon(p, card_name) for p in my_bench]}")
    print(f"    手札    : {[fmt_card(c, card_name) for c in my_hand]}")
