# C4モデル チートシート

Simon Brown が提唱した、ソフトウェアアーキテクチャを段階的に可視化するための図解フレームワーク。  
4 つの抽象レベル（Context / Container / Component / Code）で「ズームイン・アウト」しながら、対象読者と目的に応じた図を描く。

**参考**: [The C4 model for visualising software architecture](https://c4model.com/)

> 前半は C4 モデルそのものの解説。本ガイド独自の層構造（Organization / Layout / Mechanics）との対応関係は、後半の対応表にまとめている。

---

## 4 つの抽象レベル

![C4 Static Structure Diagrams](https://c4model.com/images/c4-static.png)
_© Simon Brown, [c4model.com](https://c4model.com/) — [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)_

### C1: Context

システム全体を 1 つのボックスとして扱い、**外部アクター（ユーザー・外部システム）との関係**を示す

- 対象読者: ステークホルダー・非技術者を含む全員
- 描く内容: システム境界、外部ユーザー、外部システム、それらの関係（矢印）
- 描かない内容: 内部の技術構成・実装詳細
- 実践のポイント: まずここから始める。1 枚描くだけでシステムの責務と境界が明確になる

### C2: Container

システム内部を**デプロイ単位（Container）**に分解し、技術構成を示す

- 対象読者: 開発者・アーキテクト・運用者
- 描く内容: Web アプリ・API サーバー・DB・メッセージブローカー等のデプロイ単位、それらの通信
- 描かない内容: 各 Container の内部構造
- 実践のポイント: 「Container = プロセスまたはデプロイ単位」。Docker コンテナと混同しないよう注意

### C3: Component

各 Container の内部を**主要なコンポーネント（モジュール・サービスクラス）**に分解する

- 対象読者: 開発者
- 描く内容: Container 内の責務単位（Controller / UseCase / Repository 等）とその依存関係
- 描かない内容: クラスの詳細・メソッド
- 実践のポイント: 必要な Container のみ描けばよい。全 Container を描く必要はない

### C4: Code

各 Component の内部を**クラス・インターフェース**レベルで示す

- 対象読者: 開発者
- 描く内容: クラス図・UML に相当する詳細
- 実践のポイント: **通常は省略してよい**。IDE やドキュメント生成ツールで代替できる場合がほとんど

---

## 本ガイド（アーキテクチャ設計の心得）との対応関係

C4 モデルは「**どう図に描いて伝えるか**」の枠組みであり、本ガイドは「**何をどう決めるか**」の設計原則を扱う。  
両者は目的が異なるが、扱う抽象レベルは共通している。

| C4 レベル     | 本ガイドの層                                                                   | 対応する設計判断の例                                                                     |
| ------------- | ------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------- |
| C1: Context   | [Organization](./01-organization.md)                                           | システム境界の定義、外部システムとの統合方針                                             |
| C2: Container | [Organization](./01-organization.md)                                           | アーキテクチャスタイル選定、技術スタック・データストア選定、サービス間通信プロトコル選定 |
| C3: Component | [Layout](./02-layout.md)                                                       | レイヤー設計、モジュール分割、依存の方向制御                                             |
| C4: Code      | [Layout](./02-layout.md) + [GoF パターン](./GoF-design-patterns-cheatsheet.md) | クラス設計、デザインパターン適用                                                         |
| （対応なし）  | [Mechanics](./03-mechanics.md)                                                 | 品質特性のトレードオフ、パフォーマンス・整合性・回復性の方針                             |

> **用語の注意**: C4 の **Container** という名称は、"process" / "application" / "server" / "deployable unit" といった既存の言葉がそれぞれ含意を持ちすぎるため、中立的な総称として選ばれた。しかし、 Docker 等のコンテナ技術が普及したことで、結果的に C4 の Container という語が直感に反すると感じる人も多い。その場合は、必要に応じて別の語を割り当ててもよい。  
> （参考: [FAQ: Why "container"?](https://c4model.com/faq)）
>
> 「コンポーネント」も同様に現場で幅広く使われる言葉であり、デプロイ単位（C4 の Container）を指すことが多い。
> C4 の **Component** は「Container の内部の責務単位」を指すより細かい粒度であるため、混同に注意。  
> **（本ガイドでも、多くの場合「コンポーネント」を C4 の Container 相当の意味で用いている）**

---

## 実践上のポイント

- **C1・C2 だけで十分なことが多い**: ステークホルダーとの認識合わせは C1、技術的な構成議論は C2 で完結する
- **ズームインは必要に応じて**: 特定の Container が複雑な場合のみ C3 に踏み込む
- **C4 はほぼ描かない**: IDE・ドキュメント生成ツールで代替できるため、手書きは費用対効果が低い
- **メンテコストを意識する**: 変化が少ない C1・C2 を優先して維持し、C3 以下は変化に追いつけない前提で管理する
- **Diagrams as Code を活用する**: テキスト形式の作図手段は生成 AI との相性が良く、図とコードを同期させやすい
  - [Mermaid](https://mermaid.js.org/): Markdown に埋め込める汎用作図ツール。GitHub はネイティブ対応、VSCode は拡張機能で対応。C4 図の記法（`C4Context` 等）も公式サポート
  - [PlantUML](https://plantuml.com/): Java ベースの老舗作図ツール。UML 全般をカバー
  - [Structurizr](https://structurizr.com/): C4 モデルに特化した Diagrams as Code ツール。C4 提唱者 Simon Brown 自身による
