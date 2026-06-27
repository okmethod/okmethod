# Okmethod Knowledge Index

このナレッジベースは以下の 4 つのセクションで構成されている。

- **開発の心得シリーズ** : 開発プロセス別に知識・ノウハウを集積し、自分なりに体系化したドキュメント
- **エンジニアリング自論** : 特定のテーマ・分野に関する、自論・私見中心のドキュメント
- **参考情報ダイジェスト** : 外部情報を咀嚼し、客観的に要約した上で所感・考察を付記したドキュメント
- **公式ベストプラクティス集** : 権威ある「決定版」への外部リンク集（要約は情報の欠落・歪曲リスクがあるため、原典を直接参照）

---

## 開発の心得シリーズ

- [要件定義の心得](./development-domains/planning-principles/README.md)
- [アーキテクチャ設計の心得](./development-domains/architecting-principles/README.md)
- [テスト設計の心得](./development-domains/testing-principles/README.md)
- [コーディングの心得](./development-domains/coding-principles/README.md)

**「心得」とは**:

先人の知恵・知識体系や断片的なノウハウを集積し、工程・分野ごとに分類・整理し、自分なりの「心得」として体系化することを目指す。  
実用レベルまで「心得」を確立できたら、カスタムスキル Ready な状態にして再利用しやすくする。  
（「守・破・離」の実践 -> 自分流の「型」の確立 -> コーディングエージェントへの「型」の継承）

**ディレクトリ構成**:

```
<principles>/   ← ディレクトリごと .claude/skills/ にコピーするだけで使える
|-- README.md  : 開発者向けインデックス
|-- SKILL.md   : エージェント向けカスタムスキル（/<principles> で発動）
|-- assets/    : ナレッジ本体（SKILL.md から相対パスで参照）
```

**導入方法**:

**方法 1: ローカルコピー（単体スキルを手動で使う）**

```sh
# 使いたいスキルディレクトリを .claude/skills/ にコピー
cp -r docs/development-domains/<principles>/ /path/to/.claude/skills/
```

**方法 2: マーケットプレイス経由（このリポジトリごと登録）**

```sh
# マーケットプレイスとして登録
claude plugin marketplace add git@github.com:okmethod/okmethod.git

# スキルをインストール
claude plugin install okmethod

# 最新版プラグインを再取得
claude plugin marketplace update
claude plugin update okmethod@okmethod-marketplace
```

**公式スキルとの使い分け**:

心得スキルは「**設計判断の議論・レビュー**」を目的としており、コードや差分を直接操作する公式スキルとはフェーズが異なる。

| やりたいこと                                     | 使うもの                   |
| ------------------------------------------------ | -------------------------- |
| PR・差分のバグ指摘・修正提案                     | `/code-review`（公式）     |
| コーディング原則・命名・制御フローの設計相談     | `/coding-principles`       |
| テスト戦略・テスト層構成・テストダブルの設計相談 | `/testing-principles`      |
| アーキテクチャ選定・レイヤー設計・ADR作成        | `/architecting-principles` |
| 要件定義・業務モデリング・スコープ設計           | `/planning-principles`     |

---

## エンジニアリング自論

- [弁証法的エンジニアリングのすすめ](./specialty-domains/dialectics-engineering.md)
- [ITプロジェクト ラグビーチーム理論](./specialty-domains/rugby-team-theory.md)

---

## 参考情報ダイジェスト

**技術・インフラ**:

- [パブリッククラウドサービスマップ](./references/public-cloud-map.md)
- [データ指向アプリケーションデザインまとめ](./references/ddia-overview.md)

**セキュリティ**:

- [ソフトウェアエンジニアのためのセキュリティ知識体系まとめ](./references/security-governance-overview.md)
- [Web セキュリティの勘所まとめ](./references/web-security-overview.md)

**法律・規制**:

- [OSS ライセンスまとめ](./references/oss-license-overview.md)
- [個人情報保護法まとめ](./references/ppl-overview.md)

**組織・理論**:

- [IPA デジタルスキル標準まとめ](./references/ipa-dss-overview.md)
- [SECIモデル（組織的知識創造プロセス）まとめ](./references/seci-model-overview.md)

---

## 公式ベストプラクティス集

**Google**:

- [Google Style Guides](https://google.github.io/styleguide/)
  - AngularJS Style Guide
  - Common Lisp Style Guide
  - C++ Style Guide
  - C# Style Guide
  - Go Style Guide
  - HTML/CSS Style Guide
  - JavaScript Style Guide
  - Java Style Guide
  - JSON Style Guide
  - Markdown Style Guide
  - Objective-C Style Guide
  - Python Style Guide
  - R Style Guide
  - Shell Style Guide
  - Swift Style Guide
  - TypeScript Style Guide
  - Vim script Style Guide
- [Google Engineering Practices Documentation (日本語訳)](https://fujiharuka.github.io/google-eng-practices-ja/)
  - コードレビュアーのガイド
  - 変更作成者のガイド

**GitHub**:

- [.gitignore templates](https://github.com/github/gitignore)

**Docker**:

- [Dockerfile ベストプラクティス](https://docs.docker.jp/develop/develop-images/dockerfile_best-practices.html)
- [docker build check のすすめ](https://www.docker.com/ja-jp/blog/introducing-docker-build-checks/)

**Terraform**:

- [Terraform ベストプラクティス](https://www.terraform-best-practices.com/ja)
