# PTCG AI Battle Challenge Simulation

- 公式サイト: https://ptcg-abc.pokemon.co.jp/
- Kaggleコンペ: https://www.kaggle.com/competitions/pokemon-tcg-ai-battle

## ディレクトリ構成

```
kaggle/PTCG-AI-Battle-Challenge-Simulation/
├── agent/
│   ├── cg/              # Python向けゲームエンジンライブラリ（ポケモン社提供）
│   ├── tests/           # pytestテスト
│   ├── main.py          # エージェント本体（提出物）
│   ├── utils.py         # ユーティリティ（提出物）
│   ├── deck.csv         # デッキレシピ（読み込み用・提出物）
│   ├── deck_recipe.md   # デッキレシピ（参照用）
│   ├── deck_strategy.md # デッキ戦略メモ（参照用）
│   └── pyproject.toml   # uvプロジェクト設定
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
