"""自己対戦スクリプト。

指定した2デッキで N 試合を回し、結果を JSONL ファイルに保存する。

使い方:
  uv run python scripts/run_selfplay.py          # デフォルト設定で実行
  uv run python scripts/run_selfplay.py -n 200   # 200試合
  uv run python scripts/run_selfplay.py --d0 mega_lucario --d1 fuudin
  uv run python scripts/run_selfplay.py --d0 fuudin --d1 fuudin -n 100
  uv run python scripts/run_selfplay.py --out notebooks/logs/selfplay.jsonl
"""

import argparse
import importlib.util
import json
import sys
import time
import warnings
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "agent"))
warnings.filterwarnings("ignore")

from cg.game import battle_finish, battle_select, battle_start  # noqa: E402


def load_deck(deck_name: str) -> list[int]:
    path = ROOT / "agent" / "decks" / deck_name / "deck_recipe.csv"
    with open(path) as f:
        return [int(line.strip()) for line in f if line.strip()]


def load_agent():
    spec = importlib.util.spec_from_file_location(
        "agent_main", ROOT / "agent" / "main.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def is_game_over(obs_dict: dict) -> bool:
    return any(log.get("type") == 23 for log in obs_dict.get("logs", []))


def get_result(obs_dict: dict) -> tuple[int | None, int | None]:
    """(winner_player_index, reason) を返す。"""
    for log in obs_dict.get("logs", []):
        if log.get("type") == 23:
            return log.get("result"), log.get("reason")
    return None, None


def run_one_game(mod, deck0: list[int], deck1: list[int], max_steps: int = 600) -> dict:
    obs_dict, _ = battle_start(deck0, deck1)
    step = 0

    while not is_game_over(obs_dict):
        sel = obs_dict.get("select")
        if not sel and step > 0:
            break
        action = mod.agent(obs_dict)
        obs_dict = battle_select(action)
        step += 1
        if step >= max_steps:
            break

    winner, reason = get_result(obs_dict)
    cur = obs_dict.get("current") or {}
    turn = cur.get("turn")
    players = cur.get("players", [])
    prizes = [len(p.get("prize", [])) for p in players]

    battle_finish()

    return {
        "winner": winner,
        "reason": reason,
        "turn": turn,
        "steps": step,
        "prizes": prizes,
        "timeout": step >= max_steps,
    }


def main():
    parser = argparse.ArgumentParser(description="PTCG 自己対戦スクリプト")
    parser.add_argument("--d0", default="mega_lucario", help="P0のデッキ名")
    parser.add_argument("--d1", default="fuudin", help="P1のデッキ名")
    parser.add_argument("-n", "--num-games", type=int, default=100, help="試合数")
    parser.add_argument(
        "--out",
        default=None,
        help="出力 JSONL ファイルパス（省略時は notebooks/logs/selfplay_<日時>.jsonl）",
    )
    parser.add_argument(
        "--swap", action="store_true", help="先攻/後攻を交互に入れ替える"
    )
    args = parser.parse_args()

    deck0 = load_deck(args.d0)
    deck1 = load_deck(args.d1)
    mod = load_agent()

    out_path = (
        Path(args.out)
        if args.out
        else (
            ROOT
            / "notebooks"
            / "logs"
            / f"selfplay_{datetime.now():%Y%m%d_%H%M%S}.jsonl"
        )
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"P0: {args.d0}  vs  P1: {args.d1}")
    print(f"試合数: {args.num_games}  出力: {out_path}")
    print()

    wins = [0, 0]
    t0 = time.time()

    with open(out_path, "w") as f:
        for i in range(args.num_games):
            # swap オプション時は先攻/後攻を交互に入れ替え
            if args.swap and i % 2 == 1:
                d0, d1, swapped = deck1, deck0, True
            else:
                d0, d1, swapped = deck0, deck1, False

            result = run_one_game(mod, d0, d1)

            # swap していた場合は winner を反転
            winner = result["winner"]
            if swapped and winner is not None:
                winner = 1 - winner

            if winner == 0:
                wins[0] += 1
            elif winner == 1:
                wins[1] += 1

            record = {
                "game_id": i,
                "d0": args.d0,
                "d1": args.d1,
                "swapped": swapped,
                **result,
                "winner_deck": args.d0
                if winner == 0
                else (args.d1 if winner == 1 else None),
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

            # 進捗表示（10試合ごと）
            if (i + 1) % 10 == 0:
                elapsed = time.time() - t0
                total = wins[0] + wins[1]
                w0_pct = wins[0] / total * 100 if total > 0 else 0
                print(
                    f"  {i + 1:4d}試合 | {args.d0}: {wins[0]}勝 ({w0_pct:.0f}%)"
                    f" | {args.d1}: {wins[1]}勝 ({100 - w0_pct:.0f}%)"
                    f" | {elapsed:.1f}秒"
                )

    elapsed = time.time() - t0
    total = wins[0] + wins[1]
    print()
    print(f"=== 結果 ({args.num_games}試合, {elapsed:.1f}秒) ===")
    print(f"  {args.d0}: {wins[0]}勝 ({wins[0] / total * 100:.1f}%)")
    print(f"  {args.d1}: {wins[1]}勝 ({wins[1] / total * 100:.1f}%)")
    print(f"  保存先: {out_path}")


if __name__ == "__main__":
    main()
