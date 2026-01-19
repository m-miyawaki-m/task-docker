# コンテナ設計方針

## 1コンテナ vs 複数コンテナ

### 1つのコンテナにまとめる場合

**メリット**
| 項目 | 内容 |
|------|------|
| シンプル | コンテナ間通信の設定不要 |
| オフライン構築が容易 | 1つのイメージをsave/loadするだけ |
| リソース効率 | コンテナのオーバーヘッドが少ない |
| デバッグしやすい | 全てが1つの環境内で完結 |
| 開発環境向き | ローカル開発では十分な構成 |

**デメリット**
| 項目 | 内容 |
|------|------|
| イメージサイズ大 | 全ツールが1イメージに含まれる |
| 更新が大変 | 1つ変更で全体を再commit |
| スケール不可 | 特定コンポーネントだけ増やせない |
| 障害の影響範囲 | 1つの問題で全体が止まる可能性 |

---

### 複数コンテナに分ける場合

**メリット**
| 項目 | 内容 |
|------|------|
| 独立性 | 各サービスを個別に更新・再起動可能 |
| 再利用性 | JDKコンテナを複数プロジェクトで共有 |
| スケーラビリティ | 必要なコンテナだけ増やせる |
| 本番環境に近い | マイクロサービス構成の練習になる |
| 障害分離 | 1つ落ちても他は継続 |

**デメリット**
| 項目 | 内容 |
|------|------|
| 複雑性 | docker-compose必須、ネットワーク設定が必要 |
| オフライン構築が面倒 | 複数イメージのsave/load |
| リソース消費増 | コンテナごとのオーバーヘッド |
| デバッグ難易度 | コンテナ間の問題切り分けが必要 |

---

### 構成例の比較

**1コンテナ構成**
```
my-dev-environment:v1
├── JDK 11
├── Gradle
├── Node.js
└── WebLogic
```

**複数コンテナ構成**
```yaml
services:
  app:        # JDK + Gradle
  weblogic:   # WebLogic Server
  frontend:   # Node.js
  db:         # Oracle DB（必要なら）
```

---

### 推奨構成

| ユースケース | 推奨構成 |
|--------------|----------|
| オフライン開発環境 | **1コンテナ** |
| 個人開発・学習 | **1コンテナ** |
| チーム開発 | 複数コンテナ |
| 本番想定の検証 | 複数コンテナ |
| CI/CD環境 | 複数コンテナ |

---

## 1コンテナ構成での修正・更新

### docker commit方式の課題

| 課題 | 内容 |
|------|------|
| 差分更新不可 | 小さな変更でも全体を再配布（数GB） |
| 変更履歴が不明瞭 | `docker commit`では何を変えたか追跡困難 |
| 複数人での管理 | 誰がいつ何を変えたかわからなくなる |
| ロールバック困難 | 問題発生時に前の状態に戻しにくい |

---

### 解決策: Dockerfileベースの管理

**手動commit方式**
```
手動インストール → docker commit → tar配布
```

**Dockerfile方式（推奨）**
```
Dockerfile管理 → docker build → tar配布
```

### Dockerfile例

```dockerfile
FROM ubuntu:22.04

# 基本ツール
RUN apt-get update && apt-get install -y \
    curl wget vim unzip sudo \
    && rm -rf /var/lib/apt/lists/*

# JDK 11
COPY packages/OpenJDK11U-jdk_x64_linux_hotspot_11.0.21_9.tar.gz /tmp/
RUN mkdir -p /opt/java && \
    tar -xzf /tmp/OpenJDK11U-*.tar.gz -C /opt/java --strip-components=1 && \
    rm /tmp/OpenJDK11U-*.tar.gz

# Gradle
COPY packages/gradle-7.6.1-bin.zip /tmp/
RUN unzip /tmp/gradle-*.zip -d /opt && \
    mv /opt/gradle-* /opt/gradle && \
    rm /tmp/gradle-*.zip

# Node.js
COPY packages/node-v18.*.tar.xz /tmp/
RUN tar -xJf /tmp/node-*.tar.xz -C /opt && \
    mv /opt/node-* /opt/node && \
    rm /tmp/node-*.tar.xz

# 環境変数
ENV JAVA_HOME=/opt/java
ENV GRADLE_HOME=/opt/gradle
ENV NODE_HOME=/opt/node
ENV PATH=$JAVA_HOME/bin:$GRADLE_HOME/bin:$NODE_HOME/bin:$PATH

WORKDIR /workspace
```

### Dockerfileのメリット

| 項目 | 内容 |
|------|------|
| 変更履歴 | Gitで管理可能、差分が明確 |
| 再現性 | 同じDockerfileから同じイメージを再構築 |
| レビュー可能 | 変更内容をチームで確認できる |
| 部分更新 | レイヤーキャッシュで変更部分のみ再ビルド |

---

### オフライン環境でのDockerfile運用

```
配布物:
offline-bundle/
├── Dockerfile
├── packages/           # インストーラー類
│   ├── OpenJDK11U-jdk_x64_linux_hotspot_11.0.21_9.tar.gz
│   ├── gradle-7.6.1-bin.zip
│   └── node-v18.19.0-linux-x64.tar.xz
└── images/
    └── my-dev-environment-v1.tar.gz  # ビルド済みイメージ
```

**通常運用**: ビルド済みイメージを`docker load`

**修正時**: Dockerfile編集 → `docker build` → 新イメージ配布

---

### 推奨フロー

```
【初回構築】
1. Dockerfileを作成
2. オンライン環境でdocker build
3. docker save → tar配布

【修正時】
1. Dockerfileを編集（Git管理）
2. オンライン環境で再ビルド
3. 新tarを配布（または差分パッチ）

【緊急修正（オフライン現地）】
1. コンテナ内で手動修正
2. docker commit（一時対応）
3. 後でDockerfileに反映
```

---

### 方式比較

| 方式 | 配布 | 管理 | 推奨度 |
|------|------|------|--------|
| docker commit | 簡単 | 困難 | △ 初回のみ |
| Dockerfile | 同等 | 容易 | ◎ 継続運用向け |

**結論**: 1コンテナ構成のまま、Dockerfileで管理すれば、配布の簡単さと保守性を両立できる。
