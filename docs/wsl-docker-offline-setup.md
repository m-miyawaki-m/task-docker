# WSL2 + Docker オフライン環境構築ガイド

## 概要

Windows上でWSL2 + Dockerを使った開発環境をオフライン構築する手順書です。

### 構成

```
Windows (ローカル)
├── C:\projects\my-app\        ← ソースコード
│   ├── src/
│   ├── build.gradle
│   └── ...
│
└── WSL2 + Docker
    └── コンテナ (my-dev-environment:v1)
        ├── /opt/java          ← JDK 11
        ├── /opt/gradle        ← Gradle
        ├── /u01/oracle        ← WebLogic
        └── /workspace         ← マウントポイント
              ↑
              │ マウント
        C:\projects\my-app\
```

### 方針

- **コンテナ** = 開発ツール（JDK, Gradle, Node, WebLogic等）
- **ローカル** = ソースコード（マウントして共有）
- **構築方法** = コンテナ内で手動構築 → `docker commit` でイメージ化

---

## 全体フロー

```
【準備フェーズ：オンライン環境】
  1. WSL2 + Docker Engine 構築
  2. コンテナ内で開発ツールを手動インストール
  3. docker commit でイメージ化
  4. docker save でtar化
  5. VSCode拡張機能をvsixで取得

【展開フェーズ：オフライン環境】
  6. WSL2環境を構築
  7. Docker Engineをdebパッケージからインストール
  8. docker load でイメージ読み込み
  9. ソースをマウントして起動
```

---

## Phase 1: オンライン環境での準備

### 1-1. 転送用ファイルの取得

#### WSL2用Ubuntuディストリビューション

```powershell
# PowerShellで実行

# Ubuntu 22.04 ダウンロード
Invoke-WebRequest -Uri "https://aka.ms/wslubuntu2204" -OutFile "Ubuntu2204.appx"

# 展開
Rename-Item "Ubuntu2204.appx" "Ubuntu2204.zip"
Expand-Archive "Ubuntu2204.zip" -DestinationPath ".\Ubuntu2204"

# 中の install.tar.gz が本体
```

#### Docker Engine用debパッケージ

Docker公式リポジトリから直接ダウンロード：

```
パッケージ一覧ページ（ブラウザで確認可能）:
https://download.docker.com/linux/ubuntu/dists/jammy/pool/stable/amd64/
```

**Dockerパッケージ（5ファイル）**

```bash
# Ubuntu 22.04 (jammy) 用
mkdir -p docker-debs && cd docker-debs

# containerd（コンテナランタイム）
wget https://download.docker.com/linux/ubuntu/dists/jammy/pool/stable/amd64/containerd.io_1.7.27-1_amd64.deb

# docker-ce-cli（CLIツール）
wget https://download.docker.com/linux/ubuntu/dists/jammy/pool/stable/amd64/docker-ce-cli_27.5.1-1~ubuntu.22.04~jammy_amd64.deb

# docker-ce（本体）
wget https://download.docker.com/linux/ubuntu/dists/jammy/pool/stable/amd64/docker-ce_27.5.1-1~ubuntu.22.04~jammy_amd64.deb

# docker-buildx-plugin（ビルド拡張）
wget https://download.docker.com/linux/ubuntu/dists/jammy/pool/stable/amd64/docker-buildx-plugin_0.21.2-1~ubuntu.22.04~jammy_amd64.deb

# docker-compose-plugin（Compose V2）
wget https://download.docker.com/linux/ubuntu/dists/jammy/pool/stable/amd64/docker-compose-plugin_2.32.4-1~ubuntu.22.04~jammy_amd64.deb
```

**依存パッケージ（Ubuntu公式リポジトリから）**

```bash
BASE="http://archive.ubuntu.com/ubuntu/pool"

# iptables関連
wget ${BASE}/main/i/iptables/iptables_1.8.7-1ubuntu5.2_amd64.deb
wget ${BASE}/main/i/iptables/libip4tc2_1.8.7-1ubuntu5.2_amd64.deb
wget ${BASE}/main/i/iptables/libip6tc2_1.8.7-1ubuntu5.2_amd64.deb
wget ${BASE}/main/libn/libnetfilter-conntrack/libnetfilter-conntrack3_1.0.9-1_amd64.deb
wget ${BASE}/main/libn/libnfnetlink/libnfnetlink0_1.0.1-3build3_amd64.deb
wget ${BASE}/main/libn/libnftnl/libnftnl11_1.2.1-1build1_amd64.deb

# その他
wget ${BASE}/universe/p/pigz/pigz_2.6-1_amd64.deb
```

---

### 1-2. オンライン環境でWSL2 + Docker構築

```powershell
# PowerShell（管理者）で実行
wsl --install -d Ubuntu
```

```bash
# WSL Ubuntu内で実行
sudo apt update
sudo apt install docker.io
sudo usermod -aG docker $USER
sudo service docker start
```

---

### 1-3. コンテナ内で環境構築

```bash
# ベースコンテナ起動
docker run -it --name dev-setup ubuntu:22.04 /bin/bash
```

```bash
# コンテナ内で実行

# 基本ツール
apt update && apt install -y curl wget vim unzip sudo

# JDK 11 インストール
mkdir -p /opt/java
cd /tmp
wget https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.21%2B9/OpenJDK11U-jdk_x64_linux_hotspot_11.0.21_9.tar.gz
tar -xzf OpenJDK11U-jdk_x64_linux_hotspot_11.0.21_9.tar.gz -C /opt/java --strip-components=1

export JAVA_HOME=/opt/java
export PATH=$JAVA_HOME/bin:$PATH
echo 'export JAVA_HOME=/opt/java' >> ~/.bashrc
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> ~/.bashrc

# Gradle インストール
wget https://services.gradle.org/distributions/gradle-7.6.1-bin.zip
unzip gradle-7.6.1-bin.zip -d /opt
mv /opt/gradle-7.6.1 /opt/gradle

export GRADLE_HOME=/opt/gradle
export PATH=$GRADLE_HOME/bin:$PATH
echo 'export GRADLE_HOME=/opt/gradle' >> ~/.bashrc
echo 'export PATH=$GRADLE_HOME/bin:$PATH' >> ~/.bashrc

# Node.js インストール
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# WebLogic インストール（手動でインストーラー実行）
# ... 通常のインストール手順 ...

# 確認
java -version
gradle -v
node -v
```

---

### 1-4. イメージ化・tar化

```bash
# 別ターミナルで実行（コンテナは起動したまま）

# コンテナをイメージとして保存
docker commit dev-setup my-dev-environment:v1

# 確認
docker images | grep my-dev-environment

# tar化
docker save my-dev-environment:v1 | gzip > my-dev-environment-v1.tar.gz

# サイズ確認
ls -lh my-dev-environment-v1.tar.gz
```

---

### 1-5. VSCode拡張機能の取得

VS Marketplaceから以下の拡張機能を`.vsix`形式でダウンロード：

| 拡張機能 | ID |
|----------|-----|
| Remote - WSL | ms-vscode-remote.remote-wsl |
| Docker | ms-azuretools.vscode-docker |
| Java Extension Pack | vscjava.vscode-java-pack |
| Spring Boot Extension Pack | vmware.vscode-spring-boot |
| Gradle for Java | vscjava.vscode-gradle |

```
ダウンロード方法:
1. https://marketplace.visualstudio.com/ にアクセス
2. 各拡張機能ページで「Download Extension」リンクを探す
3. .vsix ファイルを保存
```

---

## 転送ファイル一覧

```
offline-bundle/
├── wsl/
│   └── install.tar.gz                    # WSL Ubuntuディストロ
│
├── docker-debs/
│   ├── containerd.io_1.7.27-1_amd64.deb
│   ├── docker-ce_27.5.1-1~ubuntu.22.04~jammy_amd64.deb
│   ├── docker-ce-cli_27.5.1-1~ubuntu.22.04~jammy_amd64.deb
│   ├── docker-buildx-plugin_0.21.2-1~ubuntu.22.04~jammy_amd64.deb
│   ├── docker-compose-plugin_2.32.4-1~ubuntu.22.04~jammy_amd64.deb
│   ├── iptables_1.8.7-1ubuntu5.2_amd64.deb
│   ├── libip4tc2_1.8.7-1ubuntu5.2_amd64.deb
│   ├── libip6tc2_1.8.7-1ubuntu5.2_amd64.deb
│   ├── libnetfilter-conntrack3_1.0.9-1_amd64.deb
│   ├── libnfnetlink0_1.0.1-3build3_amd64.deb
│   ├── libnftnl11_1.2.1-1build1_amd64.deb
│   └── pigz_2.6-1_amd64.deb
│
├── images/
│   └── my-dev-environment-v1.tar.gz      # 開発環境イメージ
│
└── vscode/
    ├── ms-vscode-remote.remote-wsl-x.x.x.vsix
    ├── ms-azuretools.vscode-docker-x.x.x.vsix
    ├── vscjava.vscode-java-pack-x.x.x.vsix
    └── ...
```

---

## Phase 2: オフライン環境への展開

### 2-1. WSL2インストール

```powershell
# 管理者PowerShellで実行

# WSL機能有効化（再起動必要）
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart

# 再起動後
wsl --set-default-version 2

# Ubuntuインポート
wsl --import Ubuntu C:\WSL\Ubuntu .\offline-bundle\wsl\install.tar.gz
```

---

### 2-2. Docker Engineインストール

```bash
# WSL Ubuntu内で実行

cd /mnt/c/offline-bundle/docker-debs

# 依存パッケージインストール
sudo dpkg -i libnfnetlink0_*.deb
sudo dpkg -i libnetfilter-conntrack3_*.deb
sudo dpkg -i libnftnl11_*.deb
sudo dpkg -i libip4tc2_*.deb
sudo dpkg -i libip6tc2_*.deb
sudo dpkg -i iptables_*.deb
sudo dpkg -i pigz_*.deb

# Dockerインストール
sudo dpkg -i containerd.io_*.deb
sudo dpkg -i docker-ce-cli_*.deb
sudo dpkg -i docker-ce_*.deb
sudo dpkg -i docker-buildx-plugin_*.deb
sudo dpkg -i docker-compose-plugin_*.deb

# Docker起動
sudo service docker start

# 確認
docker --version
docker compose version
```

---

### 2-3. 開発イメージロード

```bash
# WSL Ubuntu内で実行

gunzip -c /mnt/c/offline-bundle/images/my-dev-environment-v1.tar.gz | docker load

# 確認
docker images
```

---

### 2-4. VSCode拡張機能インストール

```powershell
# PowerShellで実行
Get-ChildItem .\offline-bundle\vscode\*.vsix | ForEach-Object {
    code --install-extension $_.FullName
}
```

---

### 2-5. 開発環境起動

```bash
# ソースをマウントして起動
docker run -it \
  --name devbox \
  -p 7001:7001 \
  -p 5005:5005 \
  -p 3000:3000 \
  -v /mnt/c/projects/my-app:/workspace \
  my-dev-environment:v1 \
  /bin/bash
```

```powershell
# PowerShellからの場合
docker run -it `
  --name devbox `
  -p 7001:7001 `
  -p 5005:5005 `
  -v C:\projects\my-app:/workspace `
  my-dev-environment:v1 `
  /bin/bash
```

---

## 運用

### イメージ更新

```bash
# 既存コンテナに入って更新作業
docker start -ai devbox

# 更新後、再度commit
docker commit devbox my-dev-environment:v2
docker save my-dev-environment:v2 | gzip > my-dev-environment-v2.tar.gz
```

### docker-compose.yml（オプション）

```yaml
version: '3.8'
services:
  devbox:
    image: my-dev-environment:v1
    container_name: devbox
    tty: true
    stdin_open: true
    ports:
      - "7001:7001"
      - "5005:5005"
      - "3000:3000"
    volumes:
      - C:\projects\my-app:/workspace
      - gradle-cache:/root/.gradle

volumes:
  gradle-cache:
```

### VSCode DevContainer設定（オプション）

`.devcontainer/devcontainer.json`:

```json
{
  "name": "Dev Environment",
  "image": "my-dev-environment:v1",
  "workspaceFolder": "/workspace",
  "mounts": [
    "source=${localWorkspaceFolder},target=/workspace,type=bind"
  ],
  "forwardPorts": [7001, 5005, 3000],
  "customizations": {
    "vscode": {
      "extensions": [
        "vscjava.vscode-java-pack",
        "vmware.vscode-spring-boot",
        "vscjava.vscode-gradle"
      ]
    }
  }
}
```

---

## 注意事項

| 項目 | 内容 |
|------|------|
| バージョン確認 | Docker公式ページで最新版を確認してからダウンロード |
| Ubuntu版 | jammy = 22.04用、他バージョンはdists名を変更 |
| 依存不足 | `dpkg -i`でエラーが出たら足りないパッケージを追加 |
| WebLogicライセンス | Oracle Container Registryへの登録とライセンス同意が必要 |

---

## ダウンロードURL一覧

### Docker公式リポジトリ

| Ubuntu版 | URL |
|----------|-----|
| 22.04 (jammy) | https://download.docker.com/linux/ubuntu/dists/jammy/pool/stable/amd64/ |
| 24.04 (noble) | https://download.docker.com/linux/ubuntu/dists/noble/pool/stable/amd64/ |
| 20.04 (focal) | https://download.docker.com/linux/ubuntu/dists/focal/pool/stable/amd64/ |

### Ubuntu公式リポジトリ

```
http://archive.ubuntu.com/ubuntu/pool/main/
http://archive.ubuntu.com/ubuntu/pool/universe/
```

### WSL Ubuntuディストロ

| バージョン | URL |
|------------|-----|
| Ubuntu 22.04 | https://aka.ms/wslubuntu2204 |
| Ubuntu 24.04 | https://aka.ms/wslubuntu2404 |

### 開発ツール

| ツール | URL |
|--------|-----|
| Temurin JDK 11 | https://github.com/adoptium/temurin11-binaries/releases |
| Gradle | https://services.gradle.org/distributions/ |
| Node.js | https://nodejs.org/dist/ |