# Web セキュリティの勘所まとめ

Web アプリケーション開発時に意識すべきセキュリティ対策をまとめる。  
各対策の根拠となる考え方（リスク管理・フレームワーク・インシデント対応）は [security-governance-overview.md](./security-governance-overview.md) を参照。

**参考**:

- [安全な Web アプリケーションの作り方](https://wasbook.org/)
- [IPA 安全なウェブサイトの作り方](https://www.ipa.go.jp/security/vuln/websecurity/about.html)
- [IPA セキュア・プログラミング講座](https://www.ipa.go.jp/archive/security/vuln/programming/ps6vr70000012yp1-att/000059838.pdf)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)（定期改訂されるため、要件定義・コードレビューの起点として公式を参照）

---

## セキュリティ設計原則

実装の問題（バグ）ではなく設計段階の欠陥は後から修正するコストが高い。セキュリティは実装フェーズで後付けするのではなく、要件定義・設計フェーズから組み込む。

- **脅威モデリング**: 設計段階で「何を守るか」「どこから攻撃されるか」を洗い出す。代表的な手法は STRIDE（なりすまし・改ざん・否認・情報漏洩・DoS・権限昇格）。
- **セキュアデフォルト**: 機能の初期設定はセキュアな状態とし、ユーザーが明示的に緩和する設計とする（例：非公開をデフォルト、公開設定はオプトイン）。
- **フェイルセキュア（Fail Secure）**: エラーや例外が発生した場合、デフォルトで「拒否」の状態になるよう設計する（アクセス制御のデフォルト deny）。
- **多層防御（Defense in Depth）**: 単一の防御が突破されても被害が最小化されるよう、複数の防御層を重ねる。
- **最小権限の原則**: システム・アカウント・ユーザーそれぞれに、必要最小限の権限だけを付与する。
- **センシティブなビジネスフローへの制限**: 大量自動操作が想定される機能（チケット購入・クーポン利用等）にはレート制限・CAPTCHA・ステップ確認を設ける。

**参考**:

- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [OWASP Top 10 A04 Insecure Design](https://owasp.org/Top10/A04_2021-Insecure_Design/)

---

## 入力値の取り扱い（共通基盤）

インジェクション系・XSS 系の脆弱性は「信頼できない入力値をそのまま処理する」ことに起因する。各攻撃への個別対策の前提として、入力バリデーションの原則を共通基盤として押さえておく。

- **ホワイトリスト方式を優先する**: 許可する文字種・形式・範囲を明示的に定義し、それ以外を拒否する。ブラックリスト（危険な文字を除外）は漏れが生じやすい。
- **正規化してから検証する**: URL エンコード（`%2F` → `/`）・文字コード変換・Unicode 正規化（NFC 等）を行った後にバリデーションする。正規化前の検証はバイパスされやすい。
- **文字エンコーディングを統一する**: アプリ全体で UTF-8 に統一する。エンコーディングの混在は予期しない文字変換を引き起こし、エスケープが機能しなくなる場合がある。
- **バリデーションは信頼境界の入口で行う**: クライアントサイドのバリデーションは UX 向上のためのもの。サーバーサイドで必ず再検証する。

**参考**:

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)

---

## インジェクション

### SQL インジェクション

- **リスク**: ユーザー入力がそのまま SQL クエリに埋め込まれ、任意の SQL が実行される。データ漏洩・改ざん・削除に直結する。
- **対策**:
  - プレースホルダ（パラメータバインド）を必ず使用する。文字列連結による SQL 構築は禁止。
  - ORM を使う場合でも、生クエリ（raw query）のオプションには同様の注意を払う。
  - DB アカウントは最小権限とする（アプリ用アカウントに `DROP TABLE` 権限を与えない）。

**参考**:

- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

### OS コマンドインジェクション

- **リスク**: ユーザー入力を含むシェルコマンドが実行され、サーバー上で任意のコマンドが走る。
- **対策**:
  - シェルを介したコマンド実行（`system()`・`exec()`・`subprocess.call(shell=True)` 等）を避ける。
  - 外部コマンドが必要な場合は、引数を配列で渡してシェル展開を回避する（`shell=False`）。

**参考**:

- [OWASP OS Command Injection Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html)

### ディレクトリトラバーサル（パストラバーサル）

- **リスク**: ユーザー入力を含むファイルパスを構築する際に `../` 等を注入され、公開を意図しないサーバー上のファイル（設定ファイル・秘密鍵等）が読み取られる。
- **対策**:
  - ユーザー入力をファイルパスに直接使用しない。ファイル名はホワイトリストまたは内部 ID で管理する。
  - やむを得ず使用する場合は、正規化（`realpath` 等）後に許可ベースディレクトリ内に収まるかチェックする。
  - Web サーバーのドキュメントルート外へのアクセスを OS 権限・chroot・コンテナで制限する。

### HTTP ヘッダインジェクション

- **リスク**: ユーザー入力を HTTP レスポンスヘッダに含める際に CR（`\r`）・LF（`\n`）を注入され、任意のヘッダや偽のレスポンスボディを挿入される。`Set-Cookie` ヘッダの偽造によるセッションハイジャックや、リダイレクト先の改ざんに悪用される。
- **対策**:
  - レスポンスヘッダに出力するユーザー入力から CR / LF を必ず除去または拒否する。
  - リダイレクト先 URL はユーザー入力をそのまま使用せず、ホワイトリストまたはパスのみを受け取る設計にする（オープンリダイレクトと共通）。
  - モダンなフレームワーク（Express・Spring 等）はヘッダ値の CR/LF を自動的に除去するが、古いバージョンや素の HTTP ライブラリでは手動対処が必要。

### メールヘッダインジェクション

- **リスク**: メール送信機能で宛先・件名にユーザー入力を含める際に CR/LF を注入され、任意の To/Cc/Bcc ヘッダが追加される。スパムの踏み台にされる。
- **対策**:
  - メールの To・Cc・Bcc・Subject に含めるユーザー入力から CR / LF を除去または拒否する。
  - メール送信ライブラリ（Nodemailer・SendGrid SDK 等）が提供するヘッダ設定 API を使い、手動で RFC 形式の文字列を組み立てない。

### XXE（XML 外部実体参照）

- **リスク**: XML パーサーが外部実体（DOCTYPE / ENTITY）を解決する機能を悪用し、サーバー上のローカルファイル読み取りや SSRF に繋がる。
- **対策**:
  - XML パーサーの外部実体参照を無効化する（多くのモダンライブラリはデフォルト無効だが、設定を明示的に確認する）。
  - XML 入力が不要な API では JSON 等の代替フォーマットを採用し、XML パーサーを使わない設計にする。

**参考**:

- [OWASP XXE Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/XML_External_Entity_Prevention_Cheat_Sheet.html)
- [OWASP Top 10 A03 Injection](https://owasp.org/Top10/A03_2021-Injection/)

---

## XSS（クロスサイトスクリプティング）

- **リスク**: 攻撃者が挿入した JavaScript がユーザーのブラウザ上で実行される。セッション盗取・フィッシングに悪用される。
- **種類**:
  - **反射型（Reflected）**: URL パラメータ等の入力が即時レスポンスに含まれるもの
  - **蓄積型（Stored）**: DB に保存されたデータがレンダリング時に実行されるもの
  - **DOM ベース**: クライアントサイドの JS が DOM を操作する際に発生するもの
- **対策**:
  - 出力時に HTML エスケープを必ず行う（テンプレートエンジンの自動エスケープに頼りつつ、例外を把握する）。
  - `innerHTML`・`document.write` 等の危険な DOM 操作 API の使用を避ける。
  - `Content-Security-Policy` ヘッダーで信頼するスクリプトソースを制限する（後述）。

**参考**:

- [OWASP XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html)
- [OWASP DOM based XSS Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/DOM_based_XSS_Prevention_Cheat_Sheet.html)

---

## クリックジャッキング

- **リスク**: 攻撃者が透明な iframe で正規サイトを重ね、ユーザーを誘導して意図しないボタンクリックを誘発する。「いいね」の水増しや、設定変更・送金操作等に悪用される。
- **対策**:
  - `X-Frame-Options: DENY`（または `SAMEORIGIN`）ヘッダを設定し、iframe への埋め込みを禁止する。
  - モダンな代替として CSP の `frame-ancestors 'none'` ディレクティブを使用する（`X-Frame-Options` より柔軟で優先される）。
  - センシティブな操作（決済・設定変更等）には追加の確認ステップを設ける。

**参考**:

- [OWASP Clickjacking Defense Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Clickjacking_Defense_Cheat_Sheet.html)

---

## CSRF（クロスサイトリクエストフォージェリ）

- **リスク**: 被害者を罠サイトに誘導し、被害者が意図しない操作（送金・設定変更等）を被害者の認証セッションで実行させる。CSRF はインジェクション攻撃ではなく、正規セッションを悪用する攻撃である。
- **対策**:
  - **CSRF トークン**: フォームや状態変更 API に対して、セッションに紐付いたランダムトークンを要求する。
  - Cookie に `SameSite=Strict` または `SameSite=Lax` 属性を明示的に設定する。モダンブラウザ（Chrome 80 以降等）では未指定時のデフォルトが `Lax` になっているが、古いブラウザとの互換性と意図の明示のために省略しない。
  - 状態変更操作は POST / PUT / DELETE メソッドとし、GET では行わない。

**参考**:

- [OWASP CSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html)

---

## オープンリダイレクト

- **リスク**: リダイレクト先 URL をユーザー入力から構築している場合、攻撃者が任意の外部サイトへ誘導するリンクを生成できる。正規ドメインを踏み台にしたフィッシングに悪用される（例: `https://example.com/redirect?to=https://evil.com`）。
- **対策**:
  - リダイレクト先 URL を外部入力から受け取る設計を避ける。
  - やむを得ない場合はホワイトリスト（許可する URL またはパスの一覧）で検証する。
  - パスのみ（相対パス）を受け取る設計にして外部ドメインへのリダイレクトを構造上不可能にする。

---

## SSRF（サーバーサイドリクエストフォージェリ）

- **リスク**: ユーザー指定の URL にサーバーがリクエストを送出する機能を悪用し、外部からアクセスできない内部ネットワークやクラウドのメタデータエンドポイント（`http://169.254.169.254/` 等）への到達が可能になる。AWS/GCP 等のクラウド環境では IAM クレデンシャル取得に直結する。
- **対策**:
  - サーバーが外部 URL にリクエストする機能は設計段階から必要性を精査する。
  - リクエスト先 URL のスキーム（`http/https` のみ許可）・ホスト（許可リスト）を検証する。
  - 内部 IP アドレス帯（`10.x.x.x`・`172.16.x.x`・`192.168.x.x`・`169.254.x.x`）へのリクエストをブロックする。
  - IMDSv2（AWS）等のクラウドメタデータ保護機能を有効化する。

**参考**:

- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP Top 10 A10 Server-Side Request Forgery](https://owasp.org/Top10/A10_2021-Server-Side_Request_Forgery_%28SSRF%29/)

---

## ファイルアップロード

- **リスク**: アップロードされたファイルをそのままサーバー上で実行・公開すると、Web シェルの設置（サーバー乗っ取り）やマルウェア配布に悪用される。
- **対策**:
  - アップロード先ディレクトリを Web サーバーのドキュメントルート外に置き、直接 URL アクセスを不可にする。
  - ファイルの種別はコンテンツ（マジックバイト）で検証する。拡張子・MIME タイプだけの検証は回避されやすい。
  - ファイル名はユーザー指定のものをそのまま使わず、サーバー側で安全な名前（UUID 等）に付け替える。
  - 画像であれば再エンコード（リサイズ・フォーマット変換）することで埋め込みコードを除去できる。
  - ファイルサイズ上限を設定し、DoS（大量アップロード）を防ぐ。

**参考**:

- [OWASP File Upload Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)

---

## 認証・セッション管理

- **パスワード管理**:
  - bcrypt / scrypt / Argon2 等の計算コストの高いハッシュ関数でハッシュ化して保存する（MD5・SHA-1 は不可）。
  - ブルートフォース対策としてアカウントロックまたはレート制限を設ける。
  - 漏洩済みパスワードリスト（HaveIBeenPwned 等）との照合もベストプラクティスとして採用されている。

- **セッション管理**:
  - セッション ID は十分なエントロピーを持つランダム値を使用し、認証後には必ず再生成する（セッション固定攻撃対策）。
  - `HttpOnly` 属性を設定し、JavaScript からのアクセスを禁止する。
  - `Secure` 属性を設定し、HTTPS 以外では Cookie を送信しない。
  - セッションの有効期限と適切なアイドルタイムアウトを設定する。

- **多要素認証（MFA）**:
  - センシティブな操作や管理機能には MFA を必須とする。
  - TOTP（Google Authenticator 等）や WebAuthn（FIDO2）が現時点でのベストプラクティス。
  - SMS ベースの MFA は SIM スワッピング等のリスクがあるため、可能であれば避ける。

**参考**:

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Session Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Session_Management_Cheat_Sheet.html)
- [OWASP Top 10 A07 Identification and Authentication Failures](https://owasp.org/Top10/A07_2021-Identification_and_Authentication_Failures/)

---

## アクセス制御

- **認可チェックはサーバーサイドで行う**: クライアント側の非表示や無効化は対策にならない。
- **最小権限の原則**: ユーザーが必要な操作のみ許可する。水平的権限昇格（他ユーザーのリソースへのアクセス）と垂直的権限昇格（管理者権限への不正昇格）の両方を防ぐ。
- **IDOR（Insecure Direct Object References）**: リソース ID（`/api/users/123` 等）を直接受け取る場合、そのリソースが認証ユーザーのものかを毎リクエストでチェックする。
- **RBAC（ロールベースアクセス制御）**: ユーザーの役割（role）に基づいて操作可能なリソースを一元管理する。個々のユーザーに直接権限を付与する設計は避ける。

**参考**:

- [OWASP Access Control Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Access_Control_Cheat_Sheet.html)
- [OWASP Top 10 A01 Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)

---

## 暗号化・TLS

- **HTTPS の強制**: 全通信を TLS で保護する。HTTP アクセスは 301 リダイレクトで HTTPS に転送し、HSTS も設定する。
- **TLS バージョン**: TLS 1.2 以上を要求し、TLS 1.0 / 1.1 は無効化する。TLS 1.3 は 1.2 より高速・安全であり、サーバーが対応可能なら優先的に有効化する。
- **証明書管理**: Let's Encrypt 等を活用して証明書の自動更新を仕組み化する。手動管理は期限切れ障害の温床になる。
- **機密データの保存**: パスワード以外のセンシティブ情報（個人情報・認証トークン等）も暗号化して保存する。DB 透過的暗号化とアプリケーションレベル暗号化の違いと、それぞれが守るシナリオを意識する。
- **シークレット管理**: API キーや DB 接続情報は環境変数またはシークレット管理サービス（AWS Secrets Manager / GCP Secret Manager 等）で管理し、ソースコードに埋め込まない。`.env` ファイルは `.gitignore` に追加する。シークレットは定期的にローテーションし、漏洩が疑われる場合は即時失効・再発行する。

**参考**:

- [OWASP Transport Layer Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [OWASP Top 10 A02 Cryptographic Failures](https://owasp.org/Top10/A02_2021-Cryptographic_Failures/)

---

## セキュリティ設定

設定ミスは「コードのバグ」ではなく「構成の不備」によって生じる。フレームワーク・ミドルウェア・クラウドサービスのデフォルト設定が必ずしも安全とは限らない。

- **デフォルト設定の見直し**: デフォルトアカウント・デフォルトパスワードは必ず変更する。不要なサンプルページ・管理コンソール・デバッグエンドポイントは無効化または削除する。
- **本番環境でのデバッグ無効化**: スタックトレース・DB エラー・内部パス等をレスポンスに含めない。開発環境と本番環境でエラーハンドリングを分け、本番では汎用エラーメッセージのみ返す。
- **不要な HTTP メソッドの無効化**: `TRACE` 等の不要なメソッドを禁止する。

### セキュリティヘッダー

HTTP レスポンスヘッダーを適切に設定することで、ブラウザレベルの多くの攻撃を緩和できる。

| ヘッダー                    | 推奨値（例）                          | 目的                                               |
| --------------------------- | ------------------------------------- | -------------------------------------------------- |
| `Content-Security-Policy`   | `default-src 'self'`                  | 読み込み可能なリソースの origin を制限（XSS 緩和） |
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | HTTPS を強制（HSTS）                               |
| `X-Content-Type-Options`    | `nosniff`                             | MIME タイプスニッフィングを防止                    |
| `X-Frame-Options`           | `DENY` または `SAMEORIGIN`            | クリックジャッキング対策（後方互換）               |
| `Referrer-Policy`           | `strict-origin-when-cross-origin`     | リファラ情報の過剰漏洩を制限                       |
| `Permissions-Policy`        | `geolocation=(), camera=()`           | 不要なブラウザ API へのアクセスを制限              |

- 設定状況は [Security Headers](https://securityheaders.com/) でスキャンして確認できる。
- CSP は `Content-Security-Policy-Report-Only` モードで段階的に導入するとよい。
- `X-Frame-Options` は後方互換性のために設定するが、現代的な代替は CSP の `frame-ancestors` ディレクティブ（例: `frame-ancestors 'none'`）。

### CORS（Cross-Origin Resource Sharing）

- `Access-Control-Allow-Origin: *` は認証不要な公開 API 以外では設定しない。`withCredentials` の有無にかかわらず、認証が必要な API では許可する origin を明示的に指定する。
- `Access-Control-Allow-Origin` に動的に origin を反映する場合、`Vary: Origin` ヘッダーをセットしてキャッシュ汚染を防ぐ。
- プリフライトリクエスト（OPTIONS）を適切に処理する。不必要なメソッド・ヘッダーを許可しない。

**参考**:

- [OWASP HTTP Headers Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html)
- [OWASP Secure Headers Project](https://owasp.org/www-project-secure-headers/)
- [OWASP Top 10 A05 Security Misconfiguration](https://owasp.org/Top10/A05_2021-Security_Misconfiguration/)

---

## LLM 統合アプリ固有の脅威

LLM を組み込んだアプリケーション固有の攻撃。従来のインジェクション攻撃とは性質が異なり、「コードの処理ミス」ではなく「モデルの振る舞いの操作」を狙う。

### プロンプトインジェクション

- **直接型**: ユーザーが「以降の指示を無視して〜」等の入力でシステムプロンプトを上書きしようとする。
- **間接型**: LLM が処理する外部データ（Web ページ・PDF・メール等）に悪意ある指示を埋め込み、LLM を操作する。エージェント構成では特に影響が大きい（ツール呼び出し・外部送信等が誘発される）。
- **対策**:
  - システムプロンプトとユーザー入力を明確に区別する（API の `system` / `user` ロールを正しく使う）。
  - LLM に与えるツールや権限は必要最小限にする（最小権限の原則）。
  - 外部コンテンツ（RAG 取得結果等）をそのままプロンプトに連結しない。信頼できないコンテンツは明示的に「データ」として渡す。
  - LLM の出力をそのままコード実行・シェル実行・DB 操作に渡さない。

**参考**:

- [OWASP Top 10 for LLM](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

---

## ロギング・監視

- **ログに出力してはいけないもの**: パスワード・クレジットカード番号・セッション ID・個人情報等の機密情報。
- **記録すべきイベント**: 認証成功・失敗、権限エラー（403）、入力バリデーション失敗、管理操作。
- **アラート**: 短時間での認証失敗多発・異常なトラフィックパターン等を検知してアラートを飛ばす仕組みを作る。
- **ログの改ざん防止**: ログを外部のロギング基盤（CloudWatch Logs・Datadog 等）に即時転送し、アプリサーバー上のみに残さない。

**参考**:

- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [OWASP Top 10 A09 Security Logging and Monitoring Failures](https://owasp.org/Top10/A09_2021-Security_Logging_and_Monitoring_Failures/)

---

## 依存関係の脆弱性管理

- **ランタイム・フレームワークの EOL 管理**: 利用している言語ランタイム（Node.js・Python・JDK 等）とフレームワークの EOL（End of Life）日程を把握し、サポート終了前にバージョンアップする。EOL 後はセキュリティパッチが提供されなくなるため、ライブラリ単位の脆弱性対応より根本的なリスクになりえる。
  - 各ランタイムの EOL カレンダーを確認する（例: [endoflife.date](https://endoflife.date/)）
  - コンテナイメージのベースイメージ（`node:18` 等）も同様に EOL を管理する
- **既知脆弱性スキャンの自動化**: CI に組み込んで継続的にチェックする。これは CVE データベースとの照合による脆弱性情報モニタリングの自動化でもある。
  - `npm audit` / `pip-audit` / `trivy`（コンテナを含む）等
  - GitHub の Dependabot を有効化すると脆弱性のある依存ライブラリを PR で自動通知してくれる
  - ツールが検出できない脆弱性（0-day・設定ミス系等）の情報収集先・CVSS 評価の考え方は [security-governance-overview.md](./security-governance-overview.md) を参照
- **定期的なアップデート**: 古いライブラリは攻撃対象になりやすい。マイナー・パッチバージョンは積極的に上げる。
- **依存の最小化**: 不要な依存を減らすことで攻撃面（アタックサーフェス）を小さくする。
- **CI/CD パイプラインの保護**: ビルド・デプロイパイプラインへの不正なコード挿入（サプライチェーン攻撃）を防ぐ。
  - GitHub Actions 等のサードパーティアクションはコミットハッシュで固定し、タグ参照（`@v3` 等）は避ける（タグの上書きによる攻撃対策）。
  - シークレット（API キー等）は CI/CD のシークレット管理機能を使い、環境変数として注入する。ログ出力に含まれないよう注意する。
  - ソースコードリポジトリへのアクセス権を最小化し、不要なトークン・Deploy Key は削除する。

**参考**:

- [OWASP Top 10 A06 Vulnerable and Outdated Components](https://owasp.org/Top10/A06_2021-Vulnerable_and_Outdated_Components/)
- [OWASP Top 10 A08 Software and Data Integrity Failures](https://owasp.org/Top10/A08_2021-Software_and_Data_Integrity_Failures/)

---

## 定期的なセキュリティ診断

SAST・DAST・ペネトレーションテストはコストが高いため、闇雲に実施するのではなく、リスクと規模に応じて取捨選択する。

### 診断の種類

| 種別                       | 概要                                                                                                                      | コスト感                   |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------- | -------------------------- |
| **SAST（静的解析）**       | ソースコードをスキャンし、脆弱なコードパターンを検出する（Semgrep・CodeQL 等）。CI に組み込めるため継続的に実施しやすい。 | 低（ツール導入コストのみ） |
| **DAST（動的解析）**       | 稼働中のアプリに対してリクエストを送り、脆弱性を検出する（OWASP ZAP 等）。実環境に近い検証が可能。                        | 中                         |
| **ペネトレーションテスト** | 専門家が擬似的に攻撃し、実際に侵入できるかを検証する。ビジネスロジックの欠陥や複合的な攻撃経路を発見できる。              | 高（外部委託が一般的）     |

### いつやるべきか

コストが高い診断（特にペネトレーションテスト）は以下の判断基準で実施を検討する。

- **必須に近いケース**: 個人情報・金融・医療等のセンシティブデータを扱うシステム、外部公開 API の新規リリース、認証・認可・決済フローの大規模変更後、PCI DSS・ISMS 認証等のコンプライアンス要件がある場合
- **費用対効果が高いケース**: ユーザー数・データ量が一定規模を超えた段階、長期間診断を実施していないシステム（目安：1〜2 年以上）
- **SAST は常時**: CI に組み込むコストが低いため、プロジェクト規模を問わず導入する価値がある

**参考**:

- [OWASP Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
