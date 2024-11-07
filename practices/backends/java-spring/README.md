# spring-app

## ツールチェーン

- プログラム言語: Java
- パッケージ管理: Maven

## セットアップの流れ

### JDK

```bash
brew install openjdk

# 環境変数の設定: zsh を使う場合（bash を使う場合は .bashrc に置き換える）
echo 'export JDKROOT=$(brew --prefix openjdk)' >> ~/.zshrc
echo 'export PATH=$JDKROOT/bin:$PATH' >> ~/.zshrc

source ~/.zshrc

java -version
```

### Maven

```bash
brew install maven
mvn -version

mvn -B archetype:generate -DgroupId=edu.self -DartifactId=spring-app -Dversion=0.1.0 -DarchetypeArtifactId=maven-archetype-quickstart

```

### Spring Boot
