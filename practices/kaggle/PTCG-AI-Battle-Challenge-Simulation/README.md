# PTCG AI Battle Challenge Simulation

- 公式サイト: https://ptcg-abc.pokemon.co.jp/
- Kaggleコンペ: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle

## モジュール設計

`models / utils / main` を共通フレームワーク層、`deck_strategy / deck_recipe` をデッキ層として分離。  
デッキ固有の実装が `deck_strategy.py` と `deck_recipe.csv` に閉じるよう設計している。

## ディレクトリ構成

```
kaggle/PTCG-AI-Battle-Challenge-Simulation/
├── agent/
│   ├── cg/              # Python向けゲームエンジンライブラリ（ポケモン社提供）
│   │
│   ├── models.py             # 共通モデル（提出物）
│   ├── utils.py              # 共通ユーティリティ（提出物）
│   ├── deck_recipe.csv       # デッキレシピ（提出物）
│   ├── deck_strategy.py      # デッキ固有戦略ロジック（提出物）
│   ├── main.py               # エントリポイント（提出物）
│   │
│   ├── deck_recipe.md        # デッキレシピ（参照用）
│   ├── deck_strategy.md      # デッキ固有戦略メモ（参照用）
│   │
│   ├── tests/           # pytestテスト
│   │
│   └── pyproject.toml   # uvプロジェクト設定
│
├── notebooks/           # 実験用ノートブック
├── JP_Card_Data.csv     # 日本語カードリスト
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
