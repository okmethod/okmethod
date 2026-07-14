# CLAUDE.md

## プロジェクト概要

The Pokémon Company × Kaggle 主催のポケモンカードゲームAIコンペティション。
AIエージェントを実装して他参加者と自動対戦させ、レーティングを競う。

- 公式サイト: https://ptcg-abc.pokemon.co.jp/
- Kaggleコンペ: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle

## 開発コマンド（プロジェクトルートで実行）

```bash
uv run poe test     # テスト実行
uv run poe lint     # ruff + mypy
uv run poe fix      # ruff 自動修正
```

## モジュール設計

フレームワーク層とデッキ層を分離し、デッキを切り替え可能（Strategy Pattern）としている。

- フレームワーク層: `agent/` 直下の `models`, `utils`, `main`
- デッキ層: `agent/decks/` 配下のデッキパッケージ群
  - `active_deck`: アクティブデッキ名を1行で記載。**デッキを切り替える際はこのファイルを変更する**
  - `__init__.py`: `active_deck` を読み込んで対応するデッキをインポートするセレクタ
  - `mega_lucario/`: メガルカリオデッキパッケージ
  - `fuudin/`: フーディンデッキパッケージ

カードリストと各デッキの戦略については `docs/` ディレクトリ参照。

ローカル実験については `scripts/` と `notebooks/` ディレクトリ参照。

## 技術仕様

- `agent/cg/`: ポケモン社提供のC++製TCGシミュレータ。編集不要。`api.py` に盤面データ構造とMCTS用APIが定義されている
- `agent()` は1ターンに複数回呼ばれるため、ターン間の状態保持にはグローバル変数またはインスタンス変数を使う
- `docs/JP_Card_Data.csv`: カードID → 日本語カード名のマスターデータ（2103枚）
- `agent/cg/api.py` の `all_card_data()`: 全カードのメタデータ（HP・ワザ・タイプ等）をAPIで取得可能

## 提出のルール

- `main.py` に `agent()` 関数が存在すること（エントリポイント固定）
- `agent/` 配下のファイルを `tar -czf submission.tar.gz` でまとめて提出（`poe build`）
- 提出物に含めるファイル: `main.py` / `utils.py` / `models.py` / `cg/` / `decks/`（全デッキパッケージ含む）
- **デッキ切り替え時は `agent/decks/active_deck` の内容を変更する**（`__init__.py` と build コマンドが自動的にそのデッキを参照する）
- Kaggle実行環境はインターネット遮断（外部API・LLM呼び出し不可）
- `md` / `pyproject.toml` / `tests/` は提出物に含めない（`poe build` が自動除外）
