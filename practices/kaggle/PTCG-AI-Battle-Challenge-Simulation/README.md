# PTCG AI Battle Challenge Simulation

- 公式サイト: https://ptcg-abc.pokemon.co.jp/
- Kaggleコンペ: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle

## モジュール設計

`models / utils / main` を共通フレームワーク層、`decks/` をデッキ層として分離。  
デッキ固有の実装が各デッキパッケージ内に閉じるよう設計している。

**デッキ切り替えは `agent/decks/active_deck` の内容を書き換えるだけ。**

## ディレクトリ構成

```
kaggle/PTCG-AI-Battle-Challenge-Simulation/
├── pyproject.toml  # uvプロジェクト設定
├── uv.lock
│
├── agent/         # 提出物ソース
│   ├── cg/        # Python向けゲームエンジンライブラリ（ポケモン社提供）
│   ├── models.py  # 共通モデル
│   ├── utils.py   # 共通ユーティリティ
│   │
│   ├── decks/     # デッキパッケージ群（Strategy Pattern）
│   │   ├── active_deck      # アクティブデッキ名（切り替え時はここを編集）
│   │   ├── __init__.py      # active_deck を読み込むセレクタ
│   │   └── [deck_package]/  # デッキパッケージ
│   │
│   └── main.py    # エントリポイント
│
├── tests/         # pytestテスト
│
├── docs/          # ドキュメント
│   ├── JP_Card_Data.csv            # 日本語カードリスト
│   └── strategy_[deck_package].md  # デッキパッケージ向け戦略ドキュメント
│
├── notebooks/     # 実験用ノートブック
└── README.md
```

## 開発コマンド

```bash
# 初回セットアップ
uv sync

# テスト
uv run poe test

# Lint / Format
uv run poe lint
uv run poe fix

# 提出物ビルド → submission.tar.gz を Kaggle にアップロード
uv run poe build
```
