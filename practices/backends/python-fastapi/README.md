# python-fastapi

## ツールチェーン

- プログラム言語: Python
- パッケージ管理: Poetry
- linter/formatter: Ruff
- 型チェック: mypy
- テスト: pytest
- Web フレームワーク: FastAPI

## セットアップの流れ

### pyenv & python

```bash
brew install pyenv
pyenv -v

pyenv install --list
pyenv install 3.11
pyenv versions
pyenv global 3.11
python --version
```

### poetry プロジェクト

```bash
brew install poetry
poetry --version

poetry init
poetry add poethepoet -D
# 以下略
```

### fastAPI

```bash
poetry add fastapi uvicorn
# 以下略
```

- [公式ドキュメント](https://fastapi.tiangolo.com/ja/tutorial/)
