# WSL2 + Docker 概要・詳細ガイド

## WSL2とは

### 概要

**WSL2（Windows Subsystem for Linux 2）** は、Windows上でLinuxを実行するためのMicrosoft公式の仕組みです。

| 項目 | 内容 |
|------|------|
| 正式名称 | Windows Subsystem for Linux 2 |
| 提供元 | Microsoft |
| 目的 | Windows上でLinux環境を利用 |
| 対応OS | Windows 10 (version 2004以降) / Windows 11 |

### WSL1とWSL2の違い

| 項目 | WSL1 | WSL2 |
|------|------|------|
| アーキテクチャ | 変換レイヤー | 実際のLinuxカーネル |
| ファイルシステム | Windows NTFSを直接使用 | ext4（Linux専用） |
| システムコール | WindowsAPIに変換 | 完全なLinuxカーネル |
| Dockerサポート | 非対応 | **完全対応** |
| パフォーマンス | ファイルI/O速い（Windowsファイル） | Linux内ファイルI/O速い |
| メモリ使用 | 少ない | 多い（VM相当） |

### WSL2の仕組み

```
┌─────────────────────────────────────────────────┐
│ Windows 11 / 10                                 │
│                                                 │
│  ┌──────────────┐    ┌──────────────────────┐  │
│  │ Windows Apps │    │ WSL2                 │  │
│  │ (Chrome等)   │    │  ┌────────────────┐  │  │
│  │              │    │  │ Linux Kernel   │  │  │
│  │              │    │  │ (Microsoft製)  │  │  │
│  │              │    │  ├────────────────┤  │  │
│  │              │    │  │ Ubuntu 22.04   │  │  │
│  │              │    │  │ ファイルシステム│  │  │
│  │              │    │  │ プロセス       │  │  │
│  └──────────────┘    │  └────────────────┘  │  │
│         ↑            │          ↑           │  │
│         │            └──────────│───────────┘  │
│         │                       │              │
│         └───── localhost ───────┘              │
│              (自動ブリッジ)                    │
│                                                 │
│  ┌─────────────────────────────────────────┐   │
│  │ Hyper-V (軽量VM)                        │   │
│  └─────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
```

### WSL2の特徴

| 特徴 | 説明 |
|------|------|
| 完全なLinuxカーネル | Microsoftがメンテナンスする本物のLinuxカーネル |
| 高速起動 | 数秒でLinux環境が起動 |
| 低リソース | 従来のVMより軽量 |
| シームレス統合 | WindowsとLinux間でファイル共有・コマンド実行可能 |
| localhost共有 | Linux内のサーバーにWindowsからlocalhostでアクセス |

---

## Dockerとは

### 概要

**Docker** は、アプリケーションをコンテナとしてパッケージ化・実行するためのプラットフォームです。

| 項目 | 内容 |
|------|------|
| 種類 | コンテナ仮想化プラットフォーム |
| 目的 | 環境の統一・配布・再現性の確保 |
| 主要コンポーネント | Docker Engine, Docker CLI, Docker Compose |

### コンテナとVMの違い

```
【仮想マシン (VM)】                【コンテナ (Docker)】

┌─────────────────┐              ┌─────────────────┐
│ App A │ App B   │              │ App A │ App B   │
├───────┼─────────┤              ├───────┼─────────┤
│ Guest │ Guest   │              │Container│Container│
│  OS   │   OS    │              │ Runtime │ Runtime │
├───────┴─────────┤              ├─────────────────┤
│   Hypervisor    │              │  Docker Engine  │
├─────────────────┤              ├─────────────────┤
│    Host OS      │              │    Host OS      │
├─────────────────┤              ├─────────────────┤
│   Hardware      │              │   Hardware      │
└─────────────────┘              └─────────────────┘

・各VMにOS必要                    ・OSカーネル共有
・起動に分単位                    ・起動に秒単位
・GBサイズ                        ・MBサイズ
・リソース消費大                   ・リソース消費小
```

### Dockerの主要概念

| 概念 | 説明 |
|------|------|
| イメージ (Image) | コンテナの設計図。読み取り専用のテンプレート |
| コンテナ (Container) | イメージから作成された実行インスタンス |
| Dockerfile | イメージを作成するための設定ファイル |
| レジストリ (Registry) | イメージを保存・配布する場所（Docker Hub等） |
| ボリューム (Volume) | コンテナのデータを永続化する仕組み |

### Dockerの仕組み

```
┌────────────────────────────────────────────────────┐
│ Docker Host (WSL2 Ubuntu)                          │
│                                                    │
│  ┌──────────────────────────────────────────────┐ │
│  │ Docker Engine (dockerd)                      │ │
│  │                                              │ │
│  │  ┌────────────┐ ┌────────────┐              │ │
│  │  │ Container  │ │ Container  │              │ │
│  │  │ (WebLogic) │ │ (MySQL)    │              │ │
│  │  │            │ │            │              │ │
│  │  │ Port:7001  │ │ Port:3306  │              │ │
│  │  └─────┬──────┘ └─────┬──────┘              │ │
│  │        │              │                      │ │
│  │  ──────┴──────────────┴────── Docker Network│ │
│  │                                              │ │
│  └──────────────────────────────────────────────┘ │
│                      │                             │
│              -p 7001:7001                          │
│                      │                             │
└──────────────────────┼─────────────────────────────┘
                       │
                       ↓
              Windows localhost:7001
```

---

## WSL2 + Docker の組み合わせ

### なぜWSL2でDockerを使うのか

| 理由 | 説明 |
|------|------|
| ネイティブ性能 | WSL2はLinuxカーネルを持つため、Docker本来の性能を発揮 |
| Docker Desktop不要 | Docker Engineを直接インストール可能（ライセンス問題回避） |
| Linux互換性 | Linux用のDockerイメージがそのまま動作 |
| 開発効率 | Windows IDE + Linux実行環境の組み合わせ |

### Docker Desktop vs Docker Engine (WSL2直接)

| 項目 | Docker Desktop | Docker Engine (WSL2) |
|------|----------------|----------------------|
| インストール | 簡単（GUI） | コマンドライン |
| ライセンス | 大企業は有料 | 無料 |
| GUI | あり | なし |
| リソース | やや重い | 軽い |
| オフライン構築 | 困難 | **可能** |
| カスタマイズ | 制限あり | 自由 |

### 全体構成図

```
┌─────────────────────────────────────────────────────────────┐
│ Windows PC                                                  │
│                                                             │
│  ┌─────────────────┐      ┌─────────────────────────────┐  │
│  │ Windows側       │      │ WSL2 (Ubuntu)               │  │
│  │                 │      │                             │  │
│  │ ・VSCode        │ ←──→ │  ┌─────────────────────┐   │  │
│  │ ・Chrome        │      │  │ Docker Engine       │   │  │
│  │ ・ソースコード  │      │  │                     │   │  │
│  │   C:\projects\  │      │  │ ┌─────────────────┐ │   │  │
│  │                 │      │  │ │ Container       │ │   │  │
│  │                 │      │  │ │ ・JDK           │ │   │  │
│  │                 │      │  │ │ ・Gradle        │ │   │  │
│  │                 │      │  │ │ ・WebLogic      │ │   │  │
│  │                 │      │  │ │ ・Node.js       │ │   │  │
│  │                 │      │  │ └────────┬────────┘ │   │  │
│  │                 │      │  │          │          │   │  │
│  │                 │      │  └──────────│──────────┘   │  │
│  │                 │      │             │              │  │
│  │                 │      │   /mnt/c/projects/         │  │
│  │                 │      │        ↑                   │  │
│  └────────┬────────┘      └────────│───────────────────┘  │
│           │                        │                       │
│           └────── マウント ────────┘                       │
│                                                             │
│  localhost:7001 ──→ WSL2 ──→ Container:7001               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ファイルシステムの理解

### パスの対応関係

| Windows側 | WSL2側 | 用途 |
|-----------|--------|------|
| `C:\` | `/mnt/c/` | Windowsドライブへのアクセス |
| `C:\projects\my-app` | `/mnt/c/projects/my-app` | プロジェクトフォルダ |
| `C:\Users\<user>` | `/mnt/c/Users/<user>` | ユーザーフォルダ |
| - | `~/` (`/home/<user>/`) | WSL2のホームディレクトリ |
| `\\wsl$\Ubuntu\home\<user>` | `/home/<user>/` | WindowsからWSL2にアクセス |

### ファイルアクセスのパフォーマンス

| アクセスパターン | パフォーマンス | 推奨用途 |
|------------------|----------------|----------|
| WSL2 → WSL2内ファイル | ◎ 最速 | Dockerイメージ、ビルドキャッシュ |
| WSL2 → Windowsファイル (`/mnt/c/`) | △ 遅い | ソースコード（編集用） |
| Windows → WSL2ファイル (`\\wsl$\`) | △ 遅い | ファイル確認程度 |
| Windows → Windowsファイル | ◎ 速い | 通常のWindows作業 |

### 推奨配置

```
【推奨】
C:\projects\my-app\          ← ソースコード（VSCodeで編集）
    ├── src/
    ├── build.gradle
    └── ...

WSL2内
    └── Docker
        └── コンテナ内       ← ビルドツール、実行環境
            ├── /opt/java
            ├── /opt/gradle
            └── /workspace   ← /mnt/c/projects/my-app をマウント

【非推奨】
WSL2の /home/user/ にソースを置く
→ Windows IDEからのアクセスが遅い
→ Gitの改行コード問題が発生しやすい
```

---

## ネットワークの理解

### localhostの仕組み

```
Windows アプリ (Chrome)
       │
       │ http://localhost:7001
       ↓
┌──────────────────┐
│ WSL2 ネットワーク │ ← Windows と WSL2 は localhost を共有
│                  │    (WSL2 が自動でブリッジ)
└────────┬─────────┘
         │
         │ -p 7001:7001 (ポートフォワード)
         ↓
┌──────────────────┐
│ Docker コンテナ   │
│ WebLogic :7001   │
└──────────────────┘
```

### ポートフォワードの設定

```bash
docker run -p <ホスト側>:<コンテナ側> イメージ名

# 例
docker run -p 7001:7001 my-weblogic-dev:v1
#           ↑     ↑
#    Windows側   コンテナ側
#    からアクセス で動作
```

### 複数ポートの公開

```bash
docker run -it \
  -p 7001:7001 \    # WebLogic
  -p 5005:5005 \    # デバッグ
  -p 3000:3000 \    # フロントエンド
  -p 8080:8080 \    # その他
  my-dev-env:v1
```

---

## ボリュームマウントの理解

### マウントの種類

| 種類 | 書式 | 用途 |
|------|------|------|
| バインドマウント | `-v /host/path:/container/path` | ホストのフォルダを共有 |
| 名前付きボリューム | `-v volume-name:/container/path` | データ永続化 |
| 匿名ボリューム | `-v /container/path` | 一時データ |

### バインドマウント（ソースコード共有）

```bash
# WSL2からの場合
docker run -v /mnt/c/projects/my-app:/workspace ...

# PowerShellからの場合
docker run -v C:\projects\my-app:/workspace ...
```

```
Windows                     コンテナ
C:\projects\my-app\    ←→   /workspace/
    └── src/                    └── src/
    └── build.gradle            └── build.gradle
```

### 名前付きボリューム（データ永続化）

```bash
# Gradleキャッシュを永続化
docker run -v gradle-cache:/root/.gradle ...

# コンテナを削除しても gradle-cache は残る
docker rm devbox
docker volume ls  # gradle-cache が残っている
```

---

## WSL2 + Docker のメリット・デメリット

### メリット

| メリット | 説明 |
|----------|------|
| Linux互換 | Linux用ツール・コマンドがそのまま使える |
| Docker正式サポート | Docker公式がWSL2を推奨 |
| IDE統合 | VSCode Remote - WSL で快適な開発 |
| 環境分離 | ホストOSを汚さずに開発環境構築 |
| 再現性 | Dockerイメージで環境を完全に再現 |
| オフライン対応 | イメージをtar化して配布可能 |

### デメリット

| デメリット | 対策 |
|------------|------|
| メモリ使用量 | `.wslconfig` でメモリ上限設定 |
| ファイルI/O遅い（Windows↔WSL2） | ソースはWindows、ビルドはコンテナ内 |
| 学習コスト | 本ドキュメントで対応 |
| Windows再起動時 | WSL2・Dockerの自動起動設定 |

### .wslconfig でリソース制限

```ini
# C:\Users\<username>\.wslconfig

[wsl2]
memory=8GB        # メモリ上限
processors=4      # CPU数
swap=2GB          # スワップサイズ
```

---

## コマンド早見表

### WSL2コマンド（PowerShell）

```powershell
# ディストリビューション一覧
wsl --list --verbose

# WSL2をデフォルトに
wsl --set-default-version 2

# Ubuntuにログイン
wsl -d Ubuntu

# WSL2シャットダウン
wsl --shutdown

# ディストリビューションインポート
wsl --import Ubuntu C:\WSL\Ubuntu .\install.tar.gz

# ディストリビューションエクスポート
wsl --export Ubuntu .\ubuntu-backup.tar
```

### Dockerコマンド（WSL2内）

```bash
# サービス起動
sudo service docker start

# イメージ一覧
docker images

# コンテナ一覧
docker ps -a

# コンテナ起動
docker run -it --name devbox -p 7001:7001 -v /mnt/c/projects:/workspace my-dev:v1 bash

# コンテナに入る
docker exec -it devbox bash

# コンテナ停止・起動
docker stop devbox
docker start -ai devbox

# イメージ保存・読み込み
docker save my-dev:v1 | gzip > my-dev-v1.tar.gz
gunzip -c my-dev-v1.tar.gz | docker load

# コンテナからイメージ作成
docker commit devbox my-dev:v2

# 不要なリソース削除
docker system prune -a
```

---

## トラブルシューティング

### WSL2が起動しない

```powershell
# 機能の有効化確認
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all

# 再起動後
wsl --set-default-version 2
```

### Dockerが起動しない

```bash
# サービス状態確認
sudo service docker status

# 手動起動
sudo service docker start

# ソケット権限確認
ls -la /var/run/docker.sock

# ユーザーをdockerグループに追加
sudo usermod -aG docker $USER
# ログアウト・ログインで反映
```

### localhostに接続できない

```bash
# コンテナのポート確認
docker port devbox

# コンテナ内でサービス稼働確認
docker exec devbox netstat -tlnp

# WSL2のIPアドレス確認
ip addr show eth0
```

### ファイルが見えない・権限エラー

```bash
# Windowsファイルの権限確認
ls -la /mnt/c/projects/

# マウントオプション確認
mount | grep /mnt/c

# /etc/wsl.conf で権限設定
[automount]
options = "metadata,umask=22,fmask=11"
```

---

## 参考リンク

| リソース | URL |
|----------|-----|
| WSL公式ドキュメント | https://docs.microsoft.com/ja-jp/windows/wsl/ |
| Docker公式ドキュメント | https://docs.docker.com/ |
| Docker Hub | https://hub.docker.com/ |
| VSCode Remote - WSL | https://code.visualstudio.com/docs/remote/wsl |
