# Dockerfile運用ガイド

## ディレクトリ構成

```
dev-environment/
├── Dockerfile
├── packages/                    # オフライン用パッケージ
│   ├── OpenJDK11U-jdk_x64_linux_hotspot_11.0.21_9.tar.gz
│   ├── gradle-7.6.1-bin.zip
│   └── node-v18.19.0-linux-x64.tar.xz
├── scripts/                     # セットアップスクリプト
│   └── entrypoint.sh
├── config/                      # 設定ファイル
│   └── .bashrc
└── README.md
```

---

## Dockerfile

```dockerfile
FROM ubuntu:22.04

LABEL maintainer="your-team@example.com"
LABEL version="1.0"
LABEL description="Development environment for Java/Node.js projects"

# 基本ツール
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    vim \
    unzip \
    sudo \
    git \
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
COPY packages/node-v18.19.0-linux-x64.tar.xz /tmp/
RUN tar -xJf /tmp/node-*.tar.xz -C /opt && \
    mv /opt/node-* /opt/node && \
    rm /tmp/node-*.tar.xz

# 環境変数
ENV JAVA_HOME=/opt/java
ENV GRADLE_HOME=/opt/gradle
ENV NODE_HOME=/opt/node
ENV PATH=$JAVA_HOME/bin:$GRADLE_HOME/bin:$NODE_HOME/bin:$PATH

# 作業ディレクトリ
WORKDIR /workspace

# エントリーポイント
COPY scripts/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh
ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/bin/bash"]
```

---

## ビルド・配布コマンド

### イメージビルド

```bash
# 通常ビルド
docker build -t my-dev-environment:v1 .

# バージョン指定ビルド
docker build -t my-dev-environment:v1.0.0 .
docker tag my-dev-environment:v1.0.0 my-dev-environment:latest

# キャッシュ無効でビルド（クリーンビルド）
docker build --no-cache -t my-dev-environment:v1 .
```

### イメージ配布（オフライン用）

```bash
# tar化
docker save my-dev-environment:v1 | gzip > my-dev-environment-v1.tar.gz

# サイズ確認
ls -lh my-dev-environment-v1.tar.gz
```

### イメージ読み込み（オフライン環境）

```bash
# 読み込み
gunzip -c my-dev-environment-v1.tar.gz | docker load

# 確認
docker images | grep my-dev-environment
```

---

## バージョン管理

### タグ命名規則

```
my-dev-environment:v{メジャー}.{マイナー}.{パッチ}

例:
  v1.0.0  初回リリース
  v1.0.1  バグ修正
  v1.1.0  ツール追加・マイナー変更
  v2.0.0  JDKバージョン変更など大きな変更
```

### 変更履歴管理（CHANGELOG.md）

```markdown
# Changelog

## [v1.1.0] - 2024-01-15
### Added
- Node.js 18.19.0 追加

### Changed
- Gradle 7.6.0 → 7.6.1 更新

## [v1.0.0] - 2024-01-01
### Added
- 初回リリース
- JDK 11.0.21
- Gradle 7.6.0
```

---

## 更新フロー

### 通常更新（オンライン環境あり）

```
1. Dockerfileを編集
2. docker build で新バージョン作成
3. テスト・検証
4. docker save でtar化
5. オフライン環境へ配布
6. docker load で読み込み
```

```bash
# 具体的なコマンド
vim Dockerfile                                    # 編集
docker build -t my-dev-environment:v1.1.0 .      # ビルド
docker run -it my-dev-environment:v1.1.0 bash    # テスト
docker save my-dev-environment:v1.1.0 | gzip > my-dev-environment-v1.1.0.tar.gz
```

### 緊急修正（オフライン現地）

```
1. 起動中のコンテナで手動修正
2. docker commit で一時イメージ作成
3. 動作確認
4. 後日、Dockerfileに変更を反映
```

```bash
# 具体的なコマンド
docker exec -it devbox bash                      # コンテナに入る
# ... 手動で修正 ...
exit
docker commit devbox my-dev-environment:v1.0.1-hotfix
docker tag my-dev-environment:v1.0.1-hotfix my-dev-environment:latest
```

---

## レイヤーキャッシュの活用

### 効率的なDockerfile構成

```dockerfile
# 変更頻度の低いものを上に
FROM ubuntu:22.04

# 1. 基本ツール（ほぼ変更なし）
RUN apt-get update && apt-get install -y \
    curl wget vim unzip sudo git \
    && rm -rf /var/lib/apt/lists/*

# 2. JDK（変更少ない）
COPY packages/OpenJDK*.tar.gz /tmp/
RUN mkdir -p /opt/java && \
    tar -xzf /tmp/OpenJDK*.tar.gz -C /opt/java --strip-components=1 && \
    rm /tmp/OpenJDK*.tar.gz

# 3. Gradle（変更やや多い）
COPY packages/gradle-*.zip /tmp/
RUN unzip /tmp/gradle-*.zip -d /opt && \
    mv /opt/gradle-* /opt/gradle && \
    rm /tmp/gradle-*.zip

# 4. Node.js（変更多い）
COPY packages/node-*.tar.xz /tmp/
RUN tar -xJf /tmp/node-*.tar.xz -C /opt && \
    mv /opt/node-* /opt/node && \
    rm /tmp/node-*.tar.xz

# 5. 設定ファイル（最も変更多い）
COPY config/ /root/
```

**ポイント**: 変更頻度の低いレイヤーを上に配置することで、再ビルド時間を短縮

---

## Git管理

### .gitignore

```gitignore
# パッケージファイル（サイズが大きいため）
packages/*.tar.gz
packages/*.zip
packages/*.tar.xz

# ビルド成果物
*.tar.gz
!packages/.gitkeep

# Docker
.docker/
```

### リポジトリ構成

```
dev-environment/
├── .git/
├── .gitignore
├── Dockerfile
├── CHANGELOG.md
├── README.md
├── packages/
│   └── .gitkeep              # 空ディレクトリ保持用
├── scripts/
│   └── entrypoint.sh
└── config/
    └── .bashrc
```

**パッケージファイルの管理**:
- Git LFS を使用
- または、別途ファイルサーバーで管理し、ダウンロードURLをREADMEに記載

---

## トラブルシューティング

### ビルドエラー時

```bash
# 途中のレイヤーからデバッグ
docker build -t debug-image .
# エラー発生レイヤーの直前のイメージIDを確認
docker run -it <image-id> bash
```

### イメージサイズ削減

```dockerfile
# マルチステージビルド（必要な場合）
FROM ubuntu:22.04 AS builder
# ... ビルド処理 ...

FROM ubuntu:22.04
COPY --from=builder /opt/java /opt/java
# 必要なファイルのみコピー
```

```bash
# 不要なイメージ削除
docker image prune -a

# ビルドキャッシュ削除
docker builder prune
```

---

## チェックリスト

### ビルド前

- [ ] Dockerfileの変更内容を確認
- [ ] 必要なパッケージがpackages/に配置済み
- [ ] バージョンタグを決定

### ビルド後

- [ ] イメージが正常に起動するか確認
- [ ] 各ツールのバージョン確認（java -v, gradle -v, node -v）
- [ ] CHANGELOG.mdを更新
- [ ] Gitにコミット

### 配布前

- [ ] tarファイルのサイズ確認
- [ ] 別環境でdocker loadテスト
- [ ] READMEの更新
