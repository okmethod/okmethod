# GoF デザインパターン チートシート

GoF（Gang of Four）による 23パターンの日本語インデックス。
各パターンの詳細・図解・コード例は [Refactoring.Guru](https://refactoring.guru/design-patterns) を参照。

---

## 生成パターン (Creational)

オブジェクトの**生成方法**を抽象化し、柔軟性と再利用性を高める。

| パターン             | 一言説明                                                         | 詳細                                                           |
| -------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------- |
| **Singleton**        | インスタンスを1つに限定し、グローバルアクセスを提供する          | [→](https://refactoring.guru/design-patterns/singleton)        |
| **Factory Method**   | サブクラスがどのクラスのインスタンスを生成するかを決定する       | [→](https://refactoring.guru/design-patterns/factory-method)   |
| **Abstract Factory** | 関連するオブジェクト群を、具体クラスに依存せず生成する           | [→](https://refactoring.guru/design-patterns/abstract-factory) |
| **Builder**          | 複雑なオブジェクトをステップごとに組み立てる                     | [→](https://refactoring.guru/design-patterns/builder)          |
| **Prototype**        | 既存オブジェクトをコピー（クローン）して新インスタンスを生成する | [→](https://refactoring.guru/design-patterns/prototype)        |

---

## 構造パターン (Structural)

クラス・オブジェクトを**組み合わせて大きな構造**を作る。

| パターン      | 一言説明                                                   | 詳細                                                    |
| ------------- | ---------------------------------------------------------- | ------------------------------------------------------- |
| **Adapter**   | 互換性のないインターフェースを変換して協調させる           | [→](https://refactoring.guru/design-patterns/adapter)   |
| **Bridge**    | 抽象と実装を分離し、それぞれ独立して変化できるようにする   | [→](https://refactoring.guru/design-patterns/bridge)    |
| **Composite** | 個別オブジェクトと複合オブジェクトを同一視して木構造を扱う | [→](https://refactoring.guru/design-patterns/composite) |
| **Decorator** | オブジェクトに動的に機能を追加する（ラップして拡張）       | [→](https://refactoring.guru/design-patterns/decorator) |
| **Facade**    | 複雑なサブシステムに対してシンプルな窓口を提供する         | [→](https://refactoring.guru/design-patterns/facade)    |
| **Flyweight** | 多数の細かいオブジェクトを共有してメモリ効率を上げる       | [→](https://refactoring.guru/design-patterns/flyweight) |
| **Proxy**     | 本体オブジェクトへのアクセスを代理オブジェクトで制御する   | [→](https://refactoring.guru/design-patterns/proxy)     |

---

## 振る舞いパターン (Behavioral)

オブジェクト間の**責任分担・通信・アルゴリズム**を整理する。

| パターン                    | 一言説明                                                         | 詳細                                                                  |
| --------------------------- | ---------------------------------------------------------------- | --------------------------------------------------------------------- |
| **Chain of Responsibility** | リクエストを処理できるまでハンドラーチェーンに渡し続ける         | [→](https://refactoring.guru/design-patterns/chain-of-responsibility) |
| **Command**                 | リクエストをオブジェクト化し、操作のキューや取り消しを可能にする | [→](https://refactoring.guru/design-patterns/command)                 |
| **Iterator**                | コレクションの実装を隠蔽しながら要素を順に巡回する               | [→](https://refactoring.guru/design-patterns/iterator)                |
| **Mediator**                | オブジェクト間の直接依存を排除し、仲介者を介して通信させる       | [→](https://refactoring.guru/design-patterns/mediator)                |
| **Memento**                 | オブジェクトの内部状態をスナップショットとして保存・復元する     | [→](https://refactoring.guru/design-patterns/memento)                 |
| **Observer**                | 状態変化を複数のオブザーバーに自動通知する（pub/sub）            | [→](https://refactoring.guru/design-patterns/observer)                |
| **State**                   | 内部状態に応じてオブジェクトの振る舞いを切り替える               | [→](https://refactoring.guru/design-patterns/state)                   |
| **Strategy**                | アルゴリズムをカプセル化し、実行時に差し替え可能にする           | [→](https://refactoring.guru/design-patterns/strategy)                |
| **Template Method**         | 処理の骨格をスーパークラスで定義し、詳細をサブクラスに委ねる     | [→](https://refactoring.guru/design-patterns/template-method)         |
| **Visitor**                 | データ構造を変えずに、操作だけを別クラスとして追加する           | [→](https://refactoring.guru/design-patterns/visitor)                 |
| **Interpreter**             | 文法規則をクラスで表現し、言語の文を解釈・評価する               | [→](https://refactoring.guru/design-patterns/interpreter)             |
