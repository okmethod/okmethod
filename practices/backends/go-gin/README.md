# go-gin

## ツールチェーン

- プログラム言語: go
- Web(バックエンド)フレームワーク: gin

## セットアップの流れ

### go

```bash
brew install go

# 環境変数の設定: zsh を使う場合（bash を使う場合は .bashrc に置き換える）
echo 'export GOPATH=$HOME/go' >> ~/.zshrc
echo 'export GOROOT=$(brew --prefix go)/libexec' >> ~/.zshrc
echo 'export PATH=$PATH:$GOPATH/bin:$GOROOT/bin' >> ~/.zshrc
echo 'export GOPROXY=https://proxy.golang.org,direct' >> ~/.zshrc
echo 'export GOSUMDB=sum.golang.org' >> ~/.zshrc
source ~/.zshrc

go version
```

- [公式ドキュメント](https://go.dev/doc/install)
  - (brew ではなく、インストーラで `/usr/local/go` に導入している)

### gin

```bash
go get -u github.com/gin-gonic/gin
# 以下略
```

- [公式ドキュメント](https://gin-gonic.com/docs/quickstart/)
