# go-gin

## ツールチェーン

- プログラム言語: go
- Web フレームワーク: gin

## セットアップの流れ

### go をセットアップする

- インストール

  - 公式ドキュメント: [Download and install](https://go.dev/doc/install)
  - Mac の場合、 homebrew を使うことも可能
    ```bash
    brew install go
    ```

- 環境変数の設定

  - zsh を使う場合（bash を使う場合は .bashrc に置き換える）

    ```bash
    echo 'export GOPATH=$HOME/go' >> ~/.zshrc
    echo 'export GOROOT=$(brew --prefix go)/libexec' >> ~/.zshrc
    echo 'export PATH=$PATH:$GOPATH/bin:$GOROOT/bin' >> ~/.zshrc
    echo 'export GOPROXY=https://proxy.golang.org,direct' >> ~/.zshrc
    echo 'export GOSUMDB=sum.golang.org' >> ~/.zshrc
    source ~/.zshrc
    ```

  - インストール確認
    ```bash
    go version
    ```

### gin をセットアップする

- 公式ドキュメント: [Quickstart](https://gin-gonic.com/docs/quickstart/)
