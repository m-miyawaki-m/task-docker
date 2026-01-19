# WebLogic Docker イメージ構築ガイド

## 概要

WebLogicをDockerイメージに含める方法と、ドメイン設定の管理方針について説明します。

---

## WebLogicの構成要素

| 要素 | 内容 | パス例 |
|------|------|--------|
| インストールバイナリ | WebLogic本体 | `/u01/oracle/wlserver` |
| ミドルウェアホーム | Oracle製品群 | `/u01/oracle` |
| ドメイン | サーバー設定一式 | `/u01/oracle/user_projects/domains/base_domain` |
| アプリケーション | デプロイ対象 | ドメイン内 or 外部マウント |

---

## 方針: ドメインの配置場所

### 選択肢の比較

| 方式 | ドメイン配置 | メリット | デメリット |
|------|--------------|----------|------------|
| A. イメージ内 | コンテナ内 | 起動即使用可能、配布が簡単 | 設定変更時は再ビルド |
| B. ボリューム | Docker Volume | 設定が永続化 | 初回セットアップ必要 |
| C. Windowsマウント | `/mnt/c/...` | Windows側で設定管理 | パーミッション問題あり |

### 推奨: 方式A（イメージ内）+ アプリのみマウント

```
Dockerイメージ
├── WebLogicバイナリ
├── ドメイン設定（固定）
└── /workspace ← ソースコード（マウント）
        ↑
   C:\projects\my-app
```

**理由**:
- 開発環境の配布が目的なら、ドメイン設定は固定で問題ない
- アプリケーション（war/ear）はマウント経由でデプロイ
- 設定変更が必要なら再ビルドで対応

---

## Windowsにドメインを配置する場合の問題

### なぜ推奨しないか

| 問題 | 内容 |
|------|------|
| パーミッション | Linuxのファイル権限がWindows側で正しく扱えない |
| シンボリックリンク | WebLogicが使用するシンボリックリンクが動作しない |
| パス形式 | Unix形式パスとWindows形式の変換問題 |
| パフォーマンス | WSL2マウント経由は遅い |
| スクリプト互換性 | シェルスクリプトがWindows側で動作しない |

### やるなら必要な対応

```bash
# Windowsにドメインを配置する場合
docker run -it \
  -v /mnt/c/weblogic-domains/base_domain:/u01/oracle/user_projects/domains/base_domain \
  my-dev-environment:v1

# 問題:
# - startWebLogic.shが動作しない可能性
# - ログ出力でエラー
# - セキュリティファイルの権限問題
```

**結論**: Windowsにドメインを配置するのは非推奨

---

## 推奨構成: イメージにドメインを含める

### 必要なファイル

```
weblogic-image/
├── Dockerfile
├── packages/
│   └── fmw_14.1.1.0.0_wls_lite_generic.jar   # WebLogicインストーラー
├── config/
│   ├── oraInst.loc              # インベントリ設定
│   ├── wls-install.rsp          # サイレントインストール応答ファイル
│   └── create-domain.py         # ドメイン作成WLSTスクリプト
└── scripts/
    ├── entrypoint.sh
    └── start-weblogic.sh
```

---

### 設定ファイル

#### oraInst.loc

```
inventory_loc=/u01/oracle/oraInventory
inst_group=root
```

#### wls-install.rsp（サイレントインストール応答ファイル）

```
[ENGINE]
Response File Version=1.0.0.0.0

[GENERIC]
ORACLE_HOME=/u01/oracle
INSTALL_TYPE=WebLogic Server
DECLINE_SECURITY_UPDATES=true
SECURITY_UPDATES_VIA_MYORACLESUPPORT=false
```

#### create-domain.py（WLSTスクリプト）

```python
# ドメイン作成スクリプト

# テンプレート読み込み
readTemplate('/u01/oracle/wlserver/common/templates/wls/wls.jar')

# 管理者パスワード設定
cd('/')
cd('Security/base_domain/User/weblogic')
cmo.setPassword('welcome1')  # 開発用パスワード

# サーバー設定
cd('/Server/AdminServer')
cmo.setListenPort(7001)
cmo.setListenAddress('')

# 開発モード
setOption('ServerStartMode', 'dev')
setOption('OverwriteDomain', 'true')

# ドメイン書き出し
writeDomain('/u01/oracle/user_projects/domains/base_domain')
closeTemplate()

print('Domain created successfully')
exit()
```

---

### Dockerfile

```dockerfile
FROM ubuntu:22.04

LABEL maintainer="your-team@example.com"
LABEL description="WebLogic Development Environment"

# 必要なパッケージ
RUN apt-get update && apt-get install -y \
    curl \
    wget \
    vim \
    unzip \
    sudo \
    libaio1 \
    && rm -rf /var/lib/apt/lists/*

# JDK 11
COPY packages/OpenJDK11U-jdk_x64_linux_hotspot_11.0.21_9.tar.gz /tmp/
RUN mkdir -p /opt/java && \
    tar -xzf /tmp/OpenJDK11U-*.tar.gz -C /opt/java --strip-components=1 && \
    rm /tmp/OpenJDK11U-*.tar.gz

ENV JAVA_HOME=/opt/java
ENV PATH=$JAVA_HOME/bin:$PATH

# Oracle用ディレクトリ作成
RUN mkdir -p /u01/oracle && \
    chmod -R 755 /u01

# インベントリ設定
COPY config/oraInst.loc /etc/

# WebLogicインストール
COPY packages/fmw_14.1.1.0.0_wls_lite_generic.jar /tmp/
COPY config/wls-install.rsp /tmp/

RUN java -jar /tmp/fmw_14.1.1.0.0_wls_lite_generic.jar \
    -silent \
    -responseFile /tmp/wls-install.rsp \
    -invPtrLoc /etc/oraInst.loc && \
    rm /tmp/fmw_*.jar /tmp/wls-install.rsp

# 環境変数
ENV MW_HOME=/u01/oracle
ENV WL_HOME=/u01/oracle/wlserver
ENV ORACLE_HOME=/u01/oracle

# ドメイン作成
COPY config/create-domain.py /tmp/
RUN /u01/oracle/oracle_common/common/bin/wlst.sh /tmp/create-domain.py && \
    rm /tmp/create-domain.py

ENV DOMAIN_HOME=/u01/oracle/user_projects/domains/base_domain

# Gradle（オプション）
COPY packages/gradle-7.6.1-bin.zip /tmp/
RUN unzip /tmp/gradle-*.zip -d /opt && \
    mv /opt/gradle-* /opt/gradle && \
    rm /tmp/gradle-*.zip

ENV GRADLE_HOME=/opt/gradle
ENV PATH=$GRADLE_HOME/bin:$PATH

# 起動スクリプト
COPY scripts/start-weblogic.sh /usr/local/bin/
COPY scripts/entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/*.sh

WORKDIR /workspace

EXPOSE 7001 7002 5005

ENTRYPOINT ["/usr/local/bin/entrypoint.sh"]
CMD ["/bin/bash"]
```

---

### スクリプト

#### scripts/entrypoint.sh

```bash
#!/bin/bash

# 環境変数設定
export JAVA_HOME=/opt/java
export MW_HOME=/u01/oracle
export WL_HOME=/u01/oracle/wlserver
export DOMAIN_HOME=/u01/oracle/user_projects/domains/base_domain
export PATH=$JAVA_HOME/bin:$WL_HOME/server/bin:$PATH

# WebLogic環境スクリプト読み込み
if [ -f "$DOMAIN_HOME/bin/setDomainEnv.sh" ]; then
    source $DOMAIN_HOME/bin/setDomainEnv.sh
fi

exec "$@"
```

#### scripts/start-weblogic.sh

```bash
#!/bin/bash

DOMAIN_HOME=/u01/oracle/user_projects/domains/base_domain

echo "Starting WebLogic Server..."
cd $DOMAIN_HOME
./startWebLogic.sh
```

---

## ビルド・配布手順

### 1. パッケージ準備（オンライン環境）

```bash
mkdir -p packages config scripts

# 以下を手動でダウンロード
# - Oracle公式からWebLogicインストーラー
# - AdoptiumからJDK
# - GradleからGradle
```

### 2. イメージビルド

```bash
docker build -t my-weblogic-dev:v1 .

# 確認
docker images | grep my-weblogic-dev
```

### 3. 動作確認

```bash
# コンテナ起動
docker run -it --name wls-test -p 7001:7001 my-weblogic-dev:v1 bash

# コンテナ内でWebLogic起動
start-weblogic.sh

# 別ターミナルでアクセス確認
curl http://localhost:7001/console
```

### 4. tar化・配布

```bash
docker save my-weblogic-dev:v1 | gzip > my-weblogic-dev-v1.tar.gz
ls -lh my-weblogic-dev-v1.tar.gz
```

---

## 運用時の起動方法

### 基本起動

```bash
docker run -it \
  --name devbox \
  -p 7001:7001 \
  -p 5005:5005 \
  -v /mnt/c/projects/my-app:/workspace \
  my-weblogic-dev:v1 \
  bash
```

### WebLogic起動

```bash
# コンテナ内で
start-weblogic.sh

# バックグラウンド起動
nohup start-weblogic.sh > /tmp/wls.log 2>&1 &
```

### アプリケーションデプロイ

```bash
# 方法1: 自動デプロイディレクトリに配置
cp /workspace/build/libs/myapp.war $DOMAIN_HOME/autodeploy/

# 方法2: WLSTでデプロイ
$WL_HOME/../oracle_common/common/bin/wlst.sh
# WLST内で
connect('weblogic', 'welcome1', 't3://localhost:7001')
deploy('myapp', '/workspace/build/libs/myapp.war', targets='AdminServer')
```

---

## ドメイン設定を変更したい場合

### 方法1: WLSTスクリプトを修正して再ビルド

```bash
# create-domain.pyを編集
vim config/create-domain.py

# 再ビルド
docker build -t my-weblogic-dev:v1.1 .
```

### 方法2: 稼働中のコンテナで設定変更後commit

```bash
# コンテナ内で管理コンソールから設定変更
# http://localhost:7001/console

# 変更後、別ターミナルで
docker commit devbox my-weblogic-dev:v1.1-custom
```

---

## 推奨構成: ソースWindows + ビルド成果物をコンテナにデプロイ

### 構成図

```
Windows (ローカル)
├── C:\projects\my-app\          ← ソースコード
│   ├── src/
│   ├── build.gradle
│   └── build/libs/myapp.war     ← ビルド成果物
│
└── WSL2 + Docker
    └── コンテナ (my-weblogic-dev:v1)
        ├── /opt/java
        ├── /opt/gradle
        ├── /u01/oracle           ← WebLogic + ドメイン
        │   └── user_projects/domains/base_domain/
        │       └── autodeploy/   ← ここにwarをコピー
        └── /workspace            ← マウントポイント
              ↑
         C:\projects\my-app
```

### ワークフロー

```
1. VSCodeでソース編集（Windows側）
2. コンテナ内でビルド（gradle build）
3. warをautodeployにコピー
4. WebLogicが自動検知してデプロイ
```

---

### コンテナ起動

```bash
docker run -it \
  --name devbox \
  -p 7001:7001 \
  -p 5005:5005 \
  -v /mnt/c/projects/my-app:/workspace \
  my-weblogic-dev:v1 \
  bash
```

### ビルド＆デプロイ

```bash
# コンテナ内で実行

# 1. ビルド
cd /workspace
gradle build

# 2. デプロイ（autodeploy）
cp build/libs/myapp.war $DOMAIN_HOME/autodeploy/

# WebLogicが自動でデプロイ（開発モード時）
```

### 自動化スクリプト例

```bash
#!/bin/bash
# scripts/build-and-deploy.sh

cd /workspace
gradle build

if [ $? -eq 0 ]; then
    cp build/libs/*.war $DOMAIN_HOME/autodeploy/
    echo "Deployed successfully"
else
    echo "Build failed"
    exit 1
fi
```

---

### デプロイ方法の比較

| 方式 | コマンド | 特徴 |
|------|----------|------|
| autodeploy | `cp *.war $DOMAIN_HOME/autodeploy/` | 最も簡単、開発モード専用 |
| WLST | `deploy()` | 本番に近い、細かい制御可能 |
| 管理コンソール | ブラウザ操作 | GUI、手動 |

### autodeployの注意点

```bash
# 開発モードでのみ有効
# 本番モードでは無効化されている

# 再デプロイ時は一度削除
rm $DOMAIN_HOME/autodeploy/myapp.war
cp build/libs/myapp.war $DOMAIN_HOME/autodeploy/
```

---

### Gradle + WebLogicの連携

#### build.gradle に deploy タスク追加

```groovy
plugins {
    id 'war'
}

// デプロイタスク
task deploy(dependsOn: war) {
    doLast {
        def deployDir = System.getenv('DOMAIN_HOME') + '/autodeploy'
        copy {
            from war.archiveFile
            into deployDir
        }
        println "Deployed to ${deployDir}"
    }
}

// ビルド＆デプロイ
task buildAndDeploy(dependsOn: [clean, deploy])
```

```bash
# 使用方法
gradle deploy          # ビルド＆デプロイ
gradle buildAndDeploy  # クリーンビルド＆デプロイ
```

---

### ホットデプロイ（ファイル監視）

#### 方法1: Gradle continuous build

```bash
gradle build --continuous

# 別ターミナルで
watch -n 5 'cp /workspace/build/libs/*.war $DOMAIN_HOME/autodeploy/'
```

#### 方法2: スクリプトで監視

```bash
#!/bin/bash
# scripts/watch-deploy.sh

WATCH_DIR="/workspace/build/libs"
DEPLOY_DIR="$DOMAIN_HOME/autodeploy"

inotifywait -m -e close_write "$WATCH_DIR" |
while read path action file; do
    if [[ "$file" == *.war ]]; then
        echo "Detected change: $file"
        cp "$WATCH_DIR/$file" "$DEPLOY_DIR/"
        echo "Deployed: $file"
    fi
done
```

---

### この構成のメリット

| 項目 | 内容 |
|------|------|
| ソース管理 | Windows側でGit/IDE操作が快適 |
| ビルド環境 | コンテナ内で統一（チーム全員同じ環境） |
| デプロイ | コンテナ内で完結、パーミッション問題なし |
| パフォーマンス | warコピーのみなので高速 |
| 再現性 | イメージ配布で環境統一 |

---

## まとめ

| 項目 | 推奨 |
|------|------|
| ドメイン配置 | Dockerイメージ内 |
| ソースコード | Windowsからマウント |
| ビルド | コンテナ内でGradle実行 |
| デプロイ | autodeploy にwarコピー |
| 設定変更 | WLSTスクリプト修正 → 再ビルド |

**Windowsにドメインを配置するのは非推奨**。パーミッション問題やスクリプト互換性の問題が発生するため、ドメインはイメージ内に含めるのがベストです。

**ソースコードのみWindows、ビルド成果物をコンテナ内WebLogicにデプロイ**が最も効率的な構成です。

---

## Windows Chrome → コンテナ上のWebLogicにアクセス

### 構成

```
Windows
├── Chrome ブラウザ
│   └── http://localhost:7001/console  ← アクセス
│
└── WSL2 + Docker
    └── コンテナ
        └── WebLogic (7001番ポート)
              ↑
         -p 7001:7001 でポート公開
```

### ポイント

| 項目 | 内容 |
|------|------|
| ポートフォワード | `-p 7001:7001` でコンテナのポートをホストに公開 |
| アクセスURL | `http://localhost:7001` でWindows側からアクセス可能 |
| WSL2の仕組み | WSL2がlocalhostを自動的にブリッジ |

---

### コンテナ起動コマンド

```bash
docker run -it \
  --name devbox \
  -p 7001:7001 \
  -p 7002:7002 \
  -p 5005:5005 \
  -p 8080:8080 \
  -v /mnt/c/projects/my-app:/workspace \
  my-weblogic-dev:v1 \
  bash
```

### WebLogic起動後のアクセス

```bash
# コンテナ内でWebLogic起動
start-weblogic.sh
```

```
Windows Chromeで開く:

管理コンソール: http://localhost:7001/console
アプリケーション: http://localhost:7001/myapp
```

---

### よくあるポート構成

| ポート | 用途 |
|--------|------|
| 7001 | WebLogic 管理コンソール / アプリ |
| 7002 | WebLogic SSL |
| 5005 | Javaリモートデバッグ |
| 8080 | 別のWebサーバー（Node等） |
| 3000 | フロントエンド開発サーバー |

---

### デバッグ接続（VSCode / IntelliJ）

```bash
# WebLogicをデバッグモードで起動
export JAVA_OPTIONS="-agentlib:jdwp=transport=dt_socket,server=y,suspend=n,address=*:5005"
start-weblogic.sh
```

**VSCode launch.json**
```json
{
  "type": "java",
  "name": "Attach to WebLogic",
  "request": "attach",
  "hostName": "localhost",
  "port": 5005
}
```

---

### 接続できない場合のトラブルシューティング

| 問題 | 確認・対処 |
|------|------------|
| ポート公開忘れ | `docker run -p 7001:7001` を確認 |
| WebLogic未起動 | コンテナ内で `ps aux \| grep java` |
| ListenAddress設定 | WebLogicが`0.0.0.0`でリッスンしているか |
| ファイアウォール | Windows Defenderで許可されているか |

```bash
# コンテナ内でポート確認
netstat -tlnp | grep 7001

# WSL2側でポート確認
ss -tlnp | grep 7001
```
