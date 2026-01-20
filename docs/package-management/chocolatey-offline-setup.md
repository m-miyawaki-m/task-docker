# Chocolatey オフラインセットアップガイド

## 概要

Chocolateyを使用して、オフライン環境で共有フォルダからパッケージを配布する方法を解説します。

---

## 共有フォルダ構成

```
\\fileserver\dev-tools\
├── chocolatey\
│   ├── install\
│   │   └── chocolatey.0.12.1.nupkg     ← Chocolatey本体
│   └── packages\
│       ├── openjdk11.11.0.21.nupkg
│       ├── gradle.7.6.1.nupkg
│       ├── nodejs-lts.18.19.0.nupkg
│       ├── git.2.43.0.nupkg
│       └── vscode.1.85.0.nupkg
├── packages.config                      ← パッケージ定義
├── setup-chocolatey.ps1                 ← セットアップスクリプト
└── versions.json                        ← バージョン管理
```

---

## Phase 1: オンライン環境での準備

### 1-1. Chocolateyパッケージのダウンロード

```powershell
# オンライン環境で実行

# 出力先
$outputDir = "C:\temp\chocolatey-offline"
New-Item -ItemType Directory -Path "$outputDir\install" -Force
New-Item -ItemType Directory -Path "$outputDir\packages" -Force

# Chocolatey本体のダウンロード
Invoke-WebRequest -Uri "https://community.chocolatey.org/api/v2/package/chocolatey" `
    -OutFile "$outputDir\install\chocolatey.nupkg"

# パッケージのダウンロード（internalize = オフライン用に変換）
choco download openjdk11 gradle nodejs-lts git vscode `
    --internalize `
    --internalize-all-urls `
    --output-directory "$outputDir\packages"
```

### 1-2. packages.config の作成

```xml
<?xml version="1.0" encoding="utf-8"?>
<packages>
  <package id="openjdk11" version="11.0.21" />
  <package id="gradle" version="7.6.1" />
  <package id="nodejs-lts" version="18.19.0" />
  <package id="git" version="2.43.0" />
  <package id="vscode" version="1.85.0" />
</packages>
```

### 1-3. versions.json の作成

```json
{
  "version": "1.0",
  "updated": "2024-01-15",
  "packages": {
    "openjdk11": "11.0.21",
    "gradle": "7.6.1",
    "nodejs-lts": "18.19.0",
    "git": "2.43.0",
    "vscode": "1.85.0"
  }
}
```

---

## Phase 2: オフライン環境でのセットアップ

### 2-1. Chocolatey本体のインストール

```powershell
# setup-chocolatey.ps1（管理者権限で実行）

param(
    [string]$Source = "\\fileserver\dev-tools"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Chocolatey オフラインセットアップ ===" -ForegroundColor Cyan

# 1. Chocolatey本体のインストール
Write-Host "[1/4] Chocolatey本体をインストール中..." -ForegroundColor Yellow

$chocoInstallPath = "$env:ProgramData\chocolatey"
$chocoNupkg = Get-ChildItem "$Source\chocolatey\install\chocolatey*.nupkg" | Select-Object -First 1

if (!(Test-Path $chocoInstallPath)) {
    # nupkgを展開してインストール
    $tempDir = "$env:TEMP\choco-install"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

    Copy-Item $chocoNupkg.FullName "$tempDir\chocolatey.zip"
    Expand-Archive "$tempDir\chocolatey.zip" -DestinationPath "$tempDir\chocolatey" -Force

    # インストールスクリプト実行
    & "$tempDir\chocolatey\tools\chocolateyInstall.ps1"

    Remove-Item $tempDir -Recurse -Force
}

# 2. ローカルソースの設定
Write-Host "[2/4] ローカルリポジトリを設定中..." -ForegroundColor Yellow

$env:Path = "$chocoInstallPath\bin;$env:Path"

# 既存のソースを無効化（オフライン環境では不要）
choco source disable -n=chocolatey

# ローカルソースを追加
choco source add -n=local -s="$Source\chocolatey\packages" --priority=1

# 3. パッケージのインストール
Write-Host "[3/4] パッケージをインストール中..." -ForegroundColor Yellow

choco install "$Source\packages.config" -y --source=local

# 4. 確認
Write-Host "[4/4] インストール確認中..." -ForegroundColor Yellow

choco list --local-only

Write-Host ""
Write-Host "=== セットアップ完了 ===" -ForegroundColor Green
Write-Host "ターミナルを再起動してください"
```

### 2-2. 実行方法

```powershell
# 管理者PowerShellで実行
\\fileserver\dev-tools\setup-chocolatey.ps1

# または引数指定
.\setup-chocolatey.ps1 -Source "D:\offline-tools"
```

---

## パッケージ定義ファイル形式

### packages.config（XML形式 - 標準）

```xml
<?xml version="1.0" encoding="utf-8"?>
<packages>
  <package id="openjdk11" version="11.0.21" />
  <package id="gradle" version="7.6.1" />
  <package id="nodejs-lts" version="18.19.0" />
  <package id="git" />
  <package id="vscode" />
</packages>
```

```powershell
# インストール
choco install packages.config -y --source=local
```

### packages.yaml（YAML形式 - カスタムスクリプト使用）

```yaml
packages:
  - id: openjdk11
    version: "11.0.21"
  - id: gradle
    version: "7.6.1"
  - id: nodejs-lts
    version: "18.19.0"
  - id: git
  - id: vscode
```

```powershell
# install-from-yaml.ps1
Import-Module powershell-yaml

$config = Get-Content "packages.yaml" -Raw | ConvertFrom-Yaml

foreach ($pkg in $config.packages) {
    $args = @($pkg.id, "-y", "--source=local")
    if ($pkg.version) { $args += "--version=$($pkg.version)" }
    choco install @args
}
```

---

## 運用フロー

### パッケージ更新（管理者）

```powershell
# オンライン環境で実行

# 1. 新バージョンをダウンロード
choco download gradle --version=8.0 `
    --internalize `
    --output-directory \\fileserver\dev-tools\chocolatey\packages

# 2. packages.config更新
# <package id="gradle" version="8.0" />

# 3. versions.json更新
```

### 開発者の更新

```powershell
# オフライン環境で実行

# 最新のpackages.configでアップグレード
choco upgrade all -y --source=local

# または特定パッケージのみ
choco upgrade gradle -y --source=local
```

---

## トラブルシューティング

### インストールエラー

```powershell
# ログ確認
Get-Content $env:ChocolateyInstall\logs\chocolatey.log -Tail 50

# キャッシュクリア
choco cache remove

# 再インストール
choco uninstall <package> -y
choco install <package> -y --source=local --force
```

### ソースの確認

```powershell
# 登録済みソース一覧
choco source list

# ソース追加
choco source add -n=local -s="\\fileserver\path" --priority=1

# ソース削除
choco source remove -n=chocolatey
```

---

## 環境変数の自動設定

Chocolateyはパッケージインストール時に環境変数を自動設定しますが、確認が必要な場合：

```powershell
# 確認
[Environment]::GetEnvironmentVariable("JAVA_HOME", "Machine")
[Environment]::GetEnvironmentVariable("PATH", "Machine")

# 手動設定（必要な場合）
[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Eclipse Adoptium\jdk-11", "Machine")
```
