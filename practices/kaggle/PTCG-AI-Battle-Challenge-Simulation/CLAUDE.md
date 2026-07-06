# CLAUDE.md

## プロジェクト概要

The Pokémon Company × Kaggle 主催のポケモンカードゲームAIコンペティション。
AIエージェントを実装して他参加者と自動対戦させ、レーティングを競う。

- 公式サイト: https://ptcg-abc.pokemon.co.jp/
- Kaggleコンペ: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle

## 開発コマンド（agent/ ディレクトリで実行）

```bash
uv run poe test  # テスト実行
uv run poe lint  # ruff + mypy
uv run poe fix   # ruff 自動修正
```

## モジュール設計

`models / utils / main` をフレームワーク層、`deck_strategy / deck_recipe` をデッキ層として分離。デッキ固有の実装が `deck_strategy.py` と `deck_recipe.csv` に閉じるよう設計している。

## 技術仕様

- `cg/`: ポケモン社提供のC++製TCGシミュレータ。編集不要。`api.py` に盤面データ構造とMCTS用APIが定義されている
- `agent()` は1ターンに複数回呼ばれるため、ターン間の状態保持にはグローバル変数またはインスタンス変数を使う
- `JP_Card_Data.csv`: カードID → 日本語カード名のマスターデータ（2103枚）
- `cg/api.py` の `all_card_data()`: 全カードのメタデータ（HP・ワザ・タイプ等）をAPIで取得可能

## 提出のルール

- `main.py` に `agent()` 関数が存在すること（エントリポイント固定）
- `agent/` 直下のファイルを `tar -czf submission.tar.gz` でまとめて提出
- 提出物に含めるファイル: `main.py` / `utils.py` / `models.py` / `deck_strategy.py` / `deck_recipe.csv` / `cg/`
- Kaggle実行環境はインターネット遮断（外部API・LLM呼び出し不可）
- `md` / `pyproject.toml` / `tests/` は提出物に含めない（`poe build` が自動除外）
