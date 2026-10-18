---
description: Python の開発規約（型アノテ・import・ignore 理由明記）。全PJ共通の核
globs:
  - "practices/**/*.py"
---

# Python

> このファイルは全PJ共通の核。言語非依存の規約は `coding-guide.md` が SSoT。
> 各PJでは言語/FW バージョン・パッケージ管理・タスクランナー・よく使うコマンドを別途追記する。

## 開発規約

- 型アノテーションは全関数・全変数に必須（mypy strict 相当）
- import 文はファイル先頭にまとめる（処理内のローカルインポート禁止）
- lint ルールを除外（ignore）する場合は必ずコメントで理由を記載する

## よく使うコマンド

PJ 固有。各PJはこの位置に、対象ディレクトリと実コマンドを追記する（下記は一例）。

```bash
uv run poe lint          # ruff format + ruff check + mypy
uv run poe fix           # ruff format + ruff check --fix
uv run poe test          # pytest tests/
```
