# CLAUDE.md

## 行動原則

- **回答は日本語で簡潔に行う**
- **永続化する文書（ドキュメント・コードコメント）では曖昧語の単独使用を避け、具体的な操作・対象を表現する**
  - 曖昧な動詞の例: 畳む・食う・拾う・効かせる・噛ませる 等
  - 曖昧な名詞の例: 背骨・継ぎ目・器・棚・足場・堀・芽・軸 等
  - 例外: 具体的な説明と明確に結びつけられる場合であれば、比喩表現を許容する
- **ドキュメント・コード（コメント含む）・メモリを使い分け、同じ事実は1箇所に置く（重複・ドリフトを避ける）**
  - 定義されていない一時ラベル（案A・step1 等）は使用せず、リポジトリ内で自己完結させる
  - メモリは一時情報として扱い、リポジトリはメモリに依存させない
- **コミット前に必ず lint/format を実行する**
- **サブエージェントを積極活用しトークン節約する**
  - 3ファイル以上の調査・コード検索 → Explore
  - 実装計画の策定 → Plan
  - テスト/Lint/ビルド実行 → Bash (background可)

## プロジェクト概要

個人的な学習・ハンズオン用リポジトリ

- **開発哲学 (`docs/`)**: 開発原則・技術Tips・参考資料のドキュメント集（メインコンテンツ）
- **ハンズオン (`practices/`)**: 技術スタックごとの構成例・入門履歴（基本メンテ不要）

## docs ディレクトリ

このナレッジベースは以下の 4 つのセクションで構成されている。

- `docs/development-domains/`: 開発プロセス別に知識・ノウハウを集積し、自分なりに体系化したドキュメント（開発の心得シリーズ）
  - `docs/development-domains/planning-principles/`: 要件定義の心得
  - `docs/development-domains/architecting-principles/`: アーキテクチャ設計の心得
  - `docs/development-domains/testing-principles/`: テスト設計の心得
  - `docs/development-domains/coding-principles/`: コーディングの心得
- `docs/specialty-domains/`: 特定のテーマ・分野に関する、自論・私見中心のドキュメント（エンジニアリング自論）
- `docs/references/`: 外部情報を咀嚼し、客観的に要約した上で所感・考察を付記したドキュメント（参考情報ダイジェスト）
- `docs/README.md` の「公式ベストプラクティス集」セクション: 権威ある「決定版」への外部リンク集（要約は情報の欠落・歪曲リスクがあるため、原典を直接参照）

## practices ディレクトリ

- `practices/backends/`: FastAPI / Express / Gin / Spring Boot の構成例
- `practices/frontends/`: Svelte + TailwindCSS (Skeleton UI) の構成例
- `practices/fullstacks/`: T3 Stack (Next.js + tRPC) / Ruby on Rails の構成例

## .claude/rules ディレクトリ

言語横断で共通利用するコーディング規約の原典（SSoT）。他プロジェクトへ流用する雛形も兼ねる。

- `coding-guide.md`: 言語非依存の規約（命名・粒度・明確さ・Why コメント・YAGNI・負債明示）。言語非依存の事項はここに集約する
- `typescript-guide.md` / `svelte-guide.md` / `python-guide.md`: 各言語でしか成立しない事項のみ。バージョン・コマンド等のPJ固有差分は各PJ側で上書きする
