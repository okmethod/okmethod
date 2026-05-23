# パブリッククラウドサービスマップ

（注意：正式名称は Google Cloud だが、長いので旧称の GCP で書いている）

各クラウドの主要サービスを横断的に俯瞰するためのインデックス資料。  
網羅・詳細説明は目的としておらず、サービス名・分類の記憶想起と他社比較の起点として使う。  
公式ドキュメントは膨大かつ頻繁に更新されるため、詳細は各自で検索すること。

---

## 共通する重要概念

- **責任共有モデル** : 「どこまでがクラウド側の責任で、どこからがユーザー側か」を定義するモデル。IaaS/PaaS/SaaS でユーザー負担の範囲が変わる（VM は自分で OS パッチ、マネージド DB はクラウドがやる、など）
- **Well-Architected Framework** : 信頼性・セキュリティ・コスト最適化・パフォーマンス・運用性などの観点でシステムを評価・改善するベストプラクティス集。3社とも独自版を持っている
- **リージョン / ゾーン** : 地理的な冗長化の単位。リージョン（国・地域レベル）の中に複数のゾーン（データセンターレベル）がある。マルチ AZ・マルチリージョン設計の基礎
- **IaC (Infrastructure as Code)** : Terraform / CloudFormation 等でインフラをコードとして管理する考え方。再現性・レビュー可能性・自動化の観点で現在は標準的なアプローチ

---

## サービス分類

各社のサービス・用語は多岐にわたるが、似た特徴を持つものがある。  
横串の分類を理解しておくことで、キャッチアップしやすくなる。

- **基本** : リソースの作成、運用、課金の管理
- **権限管理** : ユーザー、グループ、サービスへのアクセス権限（認証・認可）の管理
- **コンピューティング** : アプリケーションコードを実行するための計算環境
- **ストレージ** : 非構造化データやバックアップなど、大容量データを保管
- **データベース(OLTP)** : トランザクション処理を行うリレーショナルデータベース
- **データベース(OLAP)** : 大量のデータを分析するためのデータウェアハウス（DWH）
- **ネットワーキング** : プライベートネットワーク、ロードバランシング、CDN、等
- **メッセージング** : サービス間の非同期通信・イベント駆動アーキテクチャの基盤
- **ロギング・モニタリング** : システムの動作状況とセキュリティイベントの監視・記録
- **セキュリティ** : クラウド環境全体のセキュリティ体制と脆弱性を管理
- **AI/ML** : ML モデルの構築・学習・デプロイ基盤と、マネージドな LLM API

---

## サービス・用語マッピング

### 基本

|     概念     |        AWS        |         GCP         |          Azure           |
| :----------: | :---------------: | :-----------------: | :----------------------: |
| 1 環境の単位 |  AWS アカウント   |  GCP プロジェクト   | Azure サブスクリプション |
| 複数環境管理 | AWS Organizations | 組織 (Organization) | Azure Management Groups  |

### 権限管理

|           概念            |            AWS            |         GCP          |              Azure               |
| :-----------------------: | :-----------------------: | :------------------: | :------------------------------: |
|    ユーザー・グループ     |       AWS IAM User        |    Cloud Identity    | Microsoft Entra ID (旧 Azure AD) |
| サービスアカウント/ロール |         IAM Role          |   Service Account    |         Managed Identity         |
|  ポリシー・権限バインド   |        IAM Policy         |     IAM Binding      |            Azure RBAC            |
|   SSO・フェデレーション   | IAM Identity Center (SSO) | Cloud Identity / GWS |        Microsoft Entra ID        |
|       秘密情報管理        |    AWS Secrets Manager    |    Secret Manager    |         Azure Key Vault          |

### コンピューティング

|         概念          |        AWS        |        GCP        |         Azure          |
| :-------------------: | :---------------: | :---------------: | :--------------------: |
|      仮想マシン       |        EC2        |  Compute Engine   | Azure Virtual Machines |
|         PaaS          | Elastic Beanstalk |    App Engine     |   Azure App Service    |
|   サーバーレス関数    |      Lambda       |  Cloud Functions  |    Azure Functions     |
| コンテナ (マネージド) |   ECS / Fargate   |     Cloud Run     |  Azure Container Apps  |
|      Kubernetes       |        EKS        |        GKE        |          AKS           |
|  コンテナレジストリ   |        ECR        | Artifact Registry |          ACR           |
|      バッチ処理       |     AWS Batch     |    Cloud Batch    |      Azure Batch       |

### ストレージ

|          概念          |    AWS     |          GCP          |         Azure         |
| :--------------------: | :--------: | :-------------------: | :-------------------: |
| オブジェクトストレージ |     S3     |     Cloud Storage     |  Azure Blob Storage   |
|   ファイルストレージ   | EFS / FSx  |       Filestore       |      Azure Files      |
|   ブロックストレージ   |    EBS     |    Persistent Disk    |  Azure Managed Disks  |
|  アーカイブストレージ  | S3 Glacier | Cloud Storage Archive | Azure Archive Storage |

### データベース(OLTP)

|             概念              |     AWS      |       GCP       |                 Azure                 |
| :---------------------------: | :----------: | :-------------: | :-----------------------------------: |
|     マネージド RDB (単一)     |     RDS      |    Cloud SQL    | Azure Database for MySQL / PostgreSQL |
| フルマネージド RDB (水平分散) | Aurora (\*1) |  Cloud Spanner  |         Azure Cosmos DB (\*2)         |
|             NoSQL             |   DynamoDB   | Cloud Firestore |            Azure Cosmos DB            |
|         インメモリ DB         | ElastiCache  |   Memorystore   |         Azure Cache for Redis         |

- (\*1) Aurora は RDS とは別アーキテクチャ（ストレージ分離型）。Spanner のような真の水平分散ではなく、高速レプリケーションが主な差別化点
- (\*2) Cosmos DB は主に NoSQL のマルチモデル DB。分散 RDB としての利用は限定的で Spanner とは設計思想が異なる

### データベース(OLAP)

|        概念        |         AWS         |      GCP       |          Azure          |
| :----------------: | :-----------------: | :------------: | :---------------------: |
| データウェアハウス |      Redshift       |    BigQuery    | Azure Synapse Analytics |
|      ETL/ELT       |      AWS Glue       |    Dataflow    |   Azure Data Factory    |
|  データレイク基盤  | S3 + Lake Formation | GCS + Dataproc | Azure Data Lake Storage |

### ネットワーキング

|           概念           |       AWS       |           GCP            |            Azure             |
| :----------------------: | :-------------: | :----------------------: | :--------------------------: |
| プライベートネットワーク |       VPC       |           VPC            | Azure Virtual Network (VNet) |
|     ロードバランサー     | ELB (ALB / NLB) |   Cloud Load Balancing   | Azure Load Balancer / App GW |
|           DNS            |    Route 53     |        Cloud DNS         |          Azure DNS           |
|           CDN            |   CloudFront    |        Cloud CDN         |    Azure CDN / Front Door    |
|        専用線接続        | Direct Connect  |    Cloud Interconnect    |      Azure ExpressRoute      |
|           VPN            |     AWS VPN     |        Cloud VPN         |      Azure VPN Gateway       |
|       API Gateway        |   API Gateway   | Cloud Endpoints / Apigee |     Azure API Management     |

### メッセージング

|       概念       |     AWS     |               GCP                |          Azure           |
| :--------------: | :---------: | :------------------------------: | :----------------------: |
|      キュー      |     SQS     | Cloud Tasks / Cloud PubSub (\*3) |       Service Bus        |
| ファンアウト通知 |     SNS     |        Cloud PubSub (\*3)        | Service Bus / Event Grid |
|   イベントバス   | EventBridge |             Eventarc             |        Event Grid        |
|  ストリーミング  |   Kinesis   |        Cloud PubSub (\*3)        |        Event Hubs        |

- (\*3) Cloud Pub/Sub は1つのサービスでキュー・Pub/Sub・ストリーミングをカバーする。AWS/Azure が用途ごとに別サービスに分かれているのと対照的

### ロギング・モニタリング

|       概念       |       AWS       |       GCP        |           Azure            |
| :--------------: | :-------------: | :--------------: | :------------------------: |
|     ログ管理     | CloudWatch Logs |  Cloud Logging   |     Azure Monitor Logs     |
|  メトリクス監視  |   CloudWatch    | Cloud Monitoring |       Azure Monitor        |
| 分散トレーシング |      X-Ray      |   Cloud Trace    | Azure Application Insights |
|     監査ログ     |   CloudTrail    | Cloud Audit Logs |     Azure Activity Log     |

### セキュリティ

|            概念            |       AWS        |             GCP             |            Azure             |
| :------------------------: | :--------------: | :-------------------------: | :--------------------------: |
|   セキュリティ管理・統合   | AWS Security Hub |   Security Command Center   | Microsoft Defender for Cloud |
|          脅威検出          | Amazon GuardDuty |   Event Threat Detection    | Microsoft Defender for Cloud |
|            WAF             |     AWS WAF      |      Cloud Armor (\*4)      |          Azure WAF           |
|       暗号化キー管理       |     AWS KMS      |          Cloud KMS          |       Azure Key Vault        |
|         DDoS 対策          |    AWS Shield    |      Cloud Armor (\*4)      |    Azure DDoS Protection     |
| ポリシー・コンプライアンス |    AWS Config    | Organization Policy Service |         Azure Policy         |

- (\*4) Cloud Armor は WAF と DDoS 対策を1サービスで兼ねる。Azure は WAF と DDoS Protection が別サービスに分かれている

### AI/ML

|          概念          |      AWS       |          GCP           |         Azure          |
| :--------------------: | :------------: | :--------------------: | :--------------------: |
| AI/ML プラットフォーム |   SageMaker    |       Vertex AI        | Azure Machine Learning |
|   LLM エンドポイント   | Amazon Bedrock | Vertex AI (Gemini API) |  Azure OpenAI Service  |

---

## 各サービスのおすすめ情報源

- AWS
  - [AWS Black Belt](https://aws.amazon.com/jp/events/aws-event-resource/archive/)
- Google Cloud
  - [G-gen Tech Blog](https://blog.g-gen.co.jp/)
- Azure
  - [Japan Azure User Group の資料](https://jazug.connpass.com/presentation/)
