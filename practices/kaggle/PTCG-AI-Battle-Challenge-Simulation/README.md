# PTCG AI Battle Challenge Simulation

- 公式サイト: https://ptcg-abc.pokemon.co.jp/
- Kaggleコンペ: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle

## モジュール設計

`models / utils / main` を共通フレームワーク層、`decks/` をデッキ層として分離。  
デッキ固有の実装が各デッキパッケージ内に閉じるよう設計している。

**デッキ切り替えは `decks/__init__.py` の import 1行を変更するだけ。**

## ディレクトリ構成

```
kaggle/PTCG-AI-Battle-Challenge-Simulation/
├── agent/
│   ├── cg/                  # Python向けゲームエンジンライブラリ（ポケモン社提供）
│   │
│   ├── decks/               # デッキパッケージ群
│   │   ├── __init__.py      # アクティブデッキのセレクタ（切り替え時はここを編集）
│   │   └── [package]/       # デッキパッケージ
│   │       ├── deck_strategy.py  # デッキ固有戦略メモ（提出物）
│   │       ├── deck_recipe.csv   # デッキレシピ（提出物）
│   │       ├── deck_strategy.md  # デッキ固有戦略メモ（参照用）
│   │       └── deck_recipe.md    # デッキレシピ（参照用）
│   │
│   ├── models.py            # 共通モデル（提出物）
│   ├── utils.py             # 共通ユーティリティ（提出物）
│   ├── main.py              # エントリポイント（提出物）
│   │
│   ├── tests/               # pytestテスト
│   └── pyproject.toml       # uvプロジェクト設定
│
├── notebooks/               # 実験用ノートブック
├── JP_Card_Data.csv         # 日本語カードリスト
└── README.md
```

## 開発コマンド

```bash
# 初回セットアップ
cd agent && uv sync

# テスト
uv run poe test

# Lint / Format
uv run poe lint
uv run poe fix

# 提出物ビルド → submission.tar.gz を Kaggle にアップロード
uv run poe build
```
