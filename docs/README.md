# Okmethod Knowledge Index

このドキュメントは、以下の 2 つの役割を両立するように設計・構成している。

- **開発者向け**: 開発者がナレッジを整理・分類・参照するための、体系化されたドキュメントとして
- **コーディングエージェント向け**: Claude Code エージェントがコードレビューや生成を行う際に参照しやすいカスタムスキルとして

---

## ディレクトリ構成

### 全体

```
docs/
|-- README.md            : このファイル
|-- development-domains/ : 開発工程軸ナレッジ
|-- specialty-domains/   : 専門分野軸ナレッジ
|-- references/          : 参考情報
```

### 「心得」

```
coding-principles/
|-- README.md     : 開発者向けインデックス
|-- SKILL.md      : エージェント向けカスタムスキル
|-- manifest.json : エージェント向けメタデータ
|-- assets/       : ナレッジ本体(共通)
|  |-- 01-code.md
|  |-- 02-logic.md
|  |-- 03-system.md
|  |-- cohesion-coupling-cheatsheet.md
|  |-- naming-cheatsheet.md
```

**（補足:「心得」とは）**

先人の知恵・知識体系や断片的なノウハウを集積し、工程・分野ごとに分類・整理し、自分なりの「心得」として体系化することを目指す。  
実用レベルまで「心得」を確立できたら、カスタムスキル Ready な状態にして再利用しやすくする。  
（「守・破・離」の実践 -> 自分流の「型」の確立 -> コーディングエージェントへの「型」の継承）

---

## 開発プロセス軸ナレッジ

- [要件定義の心得](./development-domains/planning-principles/README.md)
- [アーキテクチャ設計の心得](./development-domains/architecting-principles/README.md)
- [コーディングの心得](./development-domains/coding-principles/README.md)

## 専門分野軸ナレッジ

- [Web セキュリティ Tips](./specialty-domains/web-security-tips.md)
- 技術スタック別
  - [Github Tips](./specialty-domains/github-tips.md)
  - [Docker Tips](./specialty-domains/docker-tips.md)
  - [Python Tips](./specialty-domains/python-tips.md)
  - [TypeScript Tips](./specialty-domains/typescript-tips.md)
  - [Terraform Tips](./specialty-domains/terraform-tips.md)

---

## 参考情報

- [IPA デジタルスキル標準まとめ](./references/ipa-dss-overview.md)
- [OSS ライセンスまとめ](./references/oss-license-overview.md)
- [個人情報保護法まとめ](./references/ppl-overview.md)
- [ISMS（情報セキュリティマネジメントシステム）まとめ](./references/isms-overview.md)
