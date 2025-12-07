# 凝集度と結合度チートシート

_コード設計の原則: **高凝集・低結合** を目指す！_

---

## 凝集度（Cohesion）: モジュール内の関連性の強さ

モジュール（関数、クラス、パッケージ）内の要素がどれだけ密接に関連しているかを示す指標。

### 凝集度のレベル（低い順 → 高い順）

| レベル         | 説明                                       | 例                                                                        | 評価   |
| :------------- | :----------------------------------------- | :------------------------------------------------------------------------ | :----- |
| **偶発的凝集** | 無関係な要素が偶然集まっている             | `Utils` クラスに、文字列処理、日付処理、ファイル I/O がごちゃ混ぜ         | 禁止   |
| **論理的凝集** | 論理的に似ているが、関係のない要素が集まる | `handleInput(type)` で type が 1 なら A 処理、2 なら B 処理と分岐         | 非推奨 |
| **時間的凝集** | 同じタイミングで実行される要素が集まる     | `initialize()` で、DB 接続、ログ設定、キャッシュ初期化を全部やる          | 非推奨 |
| **手順的凝集** | 順番に実行される要素が集まる               | `readAndValidateAndSave()` のように、複数のステップを一つの関数にまとめる | 許容   |
| **連絡的凝集** | 同じデータを扱う要素が集まる               | `getUserDataAndValidate()` のように、ユーザーデータを取得して検証する     | 許容   |
| **情報的凝集** | 同じデータ構造を操作する要素が集まる       | `UserRepository` クラスが、ユーザーの CRUD 操作をすべて提供               | 推奨   |
| **機能的凝集** | 単一の明確な目的を持つ要素が集まる         | `calculateTax(price)` のように、一つの機能だけを実行する                  | 推奨   |

### 良い凝集度の例

```python
# [Good] 機能的凝集: 単一の責任を持つ
def calculate_tax(price: float, tax_rate: float) -> float:
    """価格に対する税額を計算する"""
    return price * tax_rate

# [Good] 情報的凝集: ユーザーに関する操作をまとめる
class UserRepository:
    def find_by_id(self, user_id: int) -> User:
        ...

    def save(self, user: User) -> None:
        ...

    def delete(self, user_id: int) -> None:
        ...
```

### 悪い凝集度の例

```python
# [Bad] 偶発的凝集: 無関係な処理が一つのクラスに
class Utils:
    def format_date(self, date): ...
    def send_email(self, to, subject): ...
    def calculate_discount(self, price): ...
    def connect_to_db(self): ...

# [Bad] 論理的凝集: type による分岐で異なる処理
def process_data(data, type):
    if type == "user":
        # ユーザー処理
        ...
    elif type == "product":
        # 商品処理
        ...
    elif type == "order":
        # 注文処理
        ...
```

### 凝集度を高める改善方法

1. **単一責任の原則（SRP）を適用する**
   - 一つのモジュールは一つの責任だけを持つ
2. **無関係な要素は分離する**
   - `Utils` クラスを `DateUtils`, `EmailService`, `DiscountCalculator` に分ける
3. **関連する要素をまとめる**
   - ユーザーに関する操作は `UserService` にまとめる
4. **論理的凝集を避け、ポリモーフィズムや戦略パターンで対処する**
   - 例: `type` による分岐ではなく、`UserProcessor`, `ProductProcessor` のように型ごとにクラスを分ける
   - 新しい種類が追加されても、既存コードを変更せずに拡張できる（OCP: 開放閉鎖の原則）

---

## 結合度（Coupling）: モジュール間の依存性の強さ

モジュール間がどれだけ密接に関連しているかを示す指標。

### 結合度のレベル（強い順 → 弱い順）

| レベル             | 説明                                         | 例                                                        | 評価   |
| :----------------- | :------------------------------------------- | :-------------------------------------------------------- | :----- |
| **内容結合**       | 他のモジュールの内部データを直接参照・変更   | クラス A が クラス B の private 変数を直接変更            | 禁止   |
| **共通結合**       | グローバル変数を共有する                     | 複数のモジュールが同じグローバル変数を読み書き            | 禁止   |
| **外部結合**       | 外部定義されたデータ形式に依存               | 特定のファイルフォーマットや外部 API 仕様に強く依存       | 非推奨 |
| **制御結合**       | 他のモジュールの制御フロー（実行順序）に依存 | 関数 A が関数 B にフラグを渡して、B の振る舞いを制御      | 非推奨 |
| **スタンプ結合**   | データ構造全体を渡すが、一部しか使わない     | 関数が `User` オブジェクト全体を受け取るが、name だけ使う | 許容 ※ |
| **データ結合**     | 必要最小限のデータのみをやり取り             | 関数が必要なパラメータ（`user_id`, `name`）だけを受け取る | 推奨   |
| **メッセージ結合** | メッセージパッシングでやり取り               | オブジェクト間でメソッド呼び出し、マイクロサービス間通信  | 推奨   |

※ **スタンプ結合の注意点**: 許容されるが、渡されたオブジェクトの構造変更に影響を受けるリスクがある。引数が 1〜2 個なら、データ結合（プリミティブ渡し）の方が変更に強い。

### 良い結合度の例

```python
# [Good] データ結合: 必要最小限のデータだけを渡す
def send_welcome_email(user_email: str, user_name: str) -> None:
    """ユーザーのメールアドレスと名前だけを受け取る"""
    subject = f"Welcome, {user_name}!"
    send_email(to=user_email, subject=subject, body="...")

# [Good] メッセージ結合: メソッド呼び出しでやり取り
class OrderService:
    def __init__(self, payment_gateway: PaymentGateway):
        self.payment_gateway = payment_gateway  # インターフェース（抽象）に依存

    def process_order(self, order: Order) -> None:
        # メッセージ（メソッド呼び出し）でやり取り
        self.payment_gateway.charge(order.total)

# [Good] メッセージ結合: イベント駆動アーキテクチャ
class EventPublisher:
    def publish(self, event: Event) -> None:
        """イベントを発行（疎結合）"""
        event_bus.publish(event)

class OrderCreatedListener:
    def on_order_created(self, event: OrderCreatedEvent) -> None:
        """イベントを受信して処理（発行元を知らない）"""
        send_confirmation_email(event.user_email)
```

### 悪い結合度の例

```python
# [Bad] 内容結合: 他のクラスの内部状態を直接変更
class OrderProcessor:
    def process(self, user):
        user._internal_state = "processing"  # 危険！

# [Bad] 共通結合: グローバル変数を共有
global_config = {"max_retries": 3}

def process_payment():
    retries = global_config["max_retries"]  # グローバル変数に依存
    ...

def send_notification():
    retries = global_config["max_retries"]  # 同じグローバル変数に依存
    ...

# [Bad] 制御結合: フラグで振る舞いを制御
def save_user(user, send_email_flag):
    db.save(user)
    if send_email_flag:  # フラグで制御
        send_email(user.email)

# [Bad] スタンプ結合: オブジェクト全体を渡すが、一部しか使わない
def print_user_name(user: User) -> None:
    """User オブジェクト全体を受け取るが、name だけ使う"""
    print(user.name)  # user の他のフィールドは不要
    # 問題: User クラスの構造変更の影響を受ける。引数が少ない場合はデータ結合を検討
```

### 結合度を下げる改善方法

1. **依存性注入（DI）を使う**
   - 具体的なクラスではなく、インターフェース（抽象）に依存する
2. **必要最小限のデータだけを渡す**
   - オブジェクト全体ではなく、必要なフィールドだけを渡す
   - スタンプ結合を避け、引数が 1〜2 個ならデータ結合（プリミティブ渡し）を検討する
3. **グローバル変数を避ける**
   - グローバル変数の代わりに、設定オブジェクトを引数で渡す
4. **デメテルの法則を守る**
   - `a.b.c.d()` のようなメソッドチェーンを避ける
5. **外部システムとの境界にアダプター（Wrapper）を挟む**
   - 例: 外部 API や特定のファイルフォーマットへの依存は、アダプターパターン（腐敗防止層）で隔離する
   - 外部仕様の変更が内部コード全体に波及しないようにする

---

## 高凝集・低結合の実践例

### 悪い例: 低凝集・高結合

```python
# [Bad] グローバル変数を使用（高結合）
current_user = None

# [Bad] 複数の責任を持つクラス（低凝集）
class UserManager:
    def login(self, username, password):
        global current_user
        user = self.find_user(username)
        if user.password == password:
            current_user = user  # グローバル変数を変更
            self.send_email(user.email, "Login successful")  # メール送信も担当
            self.log_activity(user.id, "login")  # ログ記録も担当
            return True
        return False

    def find_user(self, username): ...
    def send_email(self, to, subject): ...
    def log_activity(self, user_id, action): ...
```

### 良い例: 高凝集・低結合

```python
# [Good] 各クラスが単一責任を持つ（高凝集）
class UserRepository:
    """ユーザーのデータアクセスのみ担当"""
    def find_by_username(self, username: str) -> Optional[User]:
        ...

class AuthenticationService:
    """認証のみ担当"""
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def authenticate(self, username: str, password: str) -> Optional[User]:
        user = self.user_repo.find_by_username(username)
        if user and user.verify_password(password):
            return user
        return None

class EmailService:
    """メール送信のみ担当"""
    def send_login_notification(self, user_email: str) -> None:
        ...

class ActivityLogger:
    """アクティビティログのみ担当"""
    def log_login(self, user_id: int) -> None:
        ...

# [Good] 各サービスを組み合わせて使う（低結合）
class LoginController:
    def __init__(
        self,
        auth_service: AuthenticationService,
        email_service: EmailService,
        logger: ActivityLogger
    ):
        self.auth_service = auth_service
        self.email_service = email_service
        self.logger = logger

    def login(self, username: str, password: str) -> bool:
        user = self.auth_service.authenticate(username, password)
        if user:
            self.email_service.send_login_notification(user.email)
            self.logger.log_login(user.id)
            return True
        return False
```

---

## 参考リンク

- [凝集度 - Wikipedia](https://ja.wikipedia.org/wiki/凝集度)
- [結合度 - Wikipedia](https://ja.wikipedia.org/wiki/結合度)
