# ruby-on-rails

## ツールチェーン

- プログラム言語: Ruby
- パッケージ管理: gem
- DB: SQLite3
- Web フレームワーク: Rails

## セットアップの流れ

### Ruby

```bash
brew install ruby

# 環境変数の設定: zsh を使う場合（bash を使う場合は .bashrc に置き換える）
echo 'export RUBYROOT=$(brew --prefix ruby)' >> ~/.zshrc
echo 'export PATH=$RUBYROOT/bin:$PATH' >> ~/.zshrc
echo 'export PATH=/opt/homebrew/lib/ruby/gems/3.3.0/bin:$PATH' >> ~/.zshrc
source ~/.zshrc

ruby --version
gem --version
```

### SQLite3

```bash
brew install sqlite3

# 環境変数の設定: zsh を使う場合（bash を使う場合は .bashrc に置き換える）
echo 'export SQLITEROOT=$(brew --prefix sqlite3)' >> ~/.zshrc
echo 'export PATH=$SQLITEROOT/bin:$PATH' >> ~/.zshrc
echo 'export LDFLAGS=$SQLITEROOT/lib' >> ~/.zshrc
echo 'export CPPFLAGS=$SQLITEROOT/include' >> ~/.zshrc
echo 'export PKG_CONFIG_PATH=$SQLITEROOT/lib/pkgconfig' >> ~/.zshrc

source ~/.zshrc

sqlite3 --version
```

### Rails

```bash
gem install rails
rails --version

rails new . --minimal
```

- [公式ドキュメント](https://guides.rubyonrails.org/getting_started.html#creating-a-new-rails-project)

以下、自動生成された README

# README

This README would normally document whatever steps are necessary to get the
application up and running.

Things you may want to cover:

- Ruby version

- System dependencies

- Configuration

- Database creation

- Database initialization

- How to run the test suite

- Services (job queues, cache servers, search engines, etc.)

- Deployment instructions

- ...
