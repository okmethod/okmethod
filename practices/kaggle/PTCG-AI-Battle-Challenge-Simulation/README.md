# PTCG AI Battle Challenge Simulation

https://ptcg-abc.pokemon.co.jp/

https://www.kaggle.com/competitions/pokemon-tcg-ai-battle

## ディレクトリ構成

```
kaggle/PTCG-AI-Battle-Challenge-Simulation/
├── agent/
│   ├── cg/              # Python向けゲームエンジンライブラリ
│   ├── main.py          # エージェント本体
│   ├── deck.csv         # デッキレシピ（読み込み用）
│   ├── deck_recipe.md   # デッキレシピ（参照用）
│   └── deck_strategy.md # デッキ戦略（参照用）
├── notebooks/           # 実験用ノートブック
├── JP_Card_Data.csv     # 日本語カードリスト
└── README.md
```

## 提出方法

```bash
./build.sh
# → submission.tar.gz を Kaggle にアップロード
```
