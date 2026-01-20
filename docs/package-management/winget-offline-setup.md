# winget オフラインセットアップガイド

## 概要

winget（Windows Package Manager）を使用してオフライン環境でパッケージを配布する方法を解説します。

**注意**: wingetはオフライン対応が限定的で、完全オフラインには向いていません。

---

## wingetの特徴

| 項目 | 内容 |
|------|------|
| 提供元 | Microsoft公式 |
| 管理者権限 | 不要（一部パッケージは必要） |
| Windows要件 | Windows 10 1809以降 / Windows 11 |
| オフライン対応 | △ 制限あり |

---

## オフライン対応の制限

| 機能 | オフライン対応 |
|------|----------------|
| パッケージ検索 | ✗ |
| 通常インストール | ✗ |
| マニフェスト指定インストール | ○ |
| ローカルインストーラー実行 | ○ |

---

## 共有フォルダ構成

```
\\fileserver\dev-tools\
├── winget\
│   ├── manifests\                    ← パッケージマニフェスト
│   │   └── m\
│   │       └── Microsoft\
│   │           └── OpenJDK\
│   │               └── 11\
│   │                   └── Microsoft.OpenJDK.11.yaml
│   └── installers\                   ← インストーラー本体
│       ├── OpenJDK11U-jdk_x64_windows_hotspot_11.0.21_9.msi
│       ├── gradle-7.6.1-bin.zip
│       └── node-v18.19.0-x64.msi
├── winget-packages.json
├── setup-winget.ps1
└── versions.json
```

---

## Phase 1: オンライン環境での準備

### 1-1. パッケージ情報のエクスポート

```powershell
# 現在インストール済みのパッケージをエクスポート
winget export -o packages.json
```

### 1-2. インストーラーのダウンロード

```powershell
# 各ツールの公式サイトからダウンロード

# OpenJDK 11
Invoke-WebRequest -Uri "https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.21%2B9/OpenJDK11U-jdk_x64_windows_hotspot_11.0.21_9.msi" `
    -OutFile "installers\OpenJDK11U-jdk_x64_windows_hotspot_11.0.21_9.msi"

# Node.js
Invoke-WebRequest -Uri "https://nodejs.org/dist/v18.19.0/node-v18.19.0-x64.msi" `
    -OutFile "installers\node-v18.19.0-x64.msi"

# Git
Invoke-WebRequest -Uri "https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/Git-2.43.0-64-bit.exe" `
    -OutFile "installers\Git-2.43.0-64-bit.exe"
```

### 1-3. カスタムマニフェストの作成

```yaml
# manifests/m/Microsoft/OpenJDK/11/Microsoft.OpenJDK.11.yaml

PackageIdentifier: Microsoft.OpenJDK.11
PackageVersion: 11.0.21
PackageName: Microsoft Build of OpenJDK 11
Publisher: Microsoft
License: GPLv2 with Classpath Exception
ShortDescription: Microsoft Build of OpenJDK
Installers:
  - Architecture: x64
    InstallerType: msi
    InstallerUrl: file:///\\fileserver\dev-tools\winget\installers\OpenJDK11U-jdk_x64_windows_hotspot_11.0.21_9.msi
    InstallerSha256: <SHA256ハッシュ>
ManifestType: singleton
ManifestVersion: 1.4.0
```

---

## Phase 2: オフライン環境でのセットアップ

### 2-1. wingetでローカルマニフェストからインストール

```powershell
# マニフェストを指定してインストール
winget install --manifest \\fileserver\dev-tools\winget\manifests\m\Microsoft\OpenJDK\11
```

### 2-2. 直接インストーラーを実行（推奨）

wingetのオフライン制限を回避するため、直接インストーラーを実行する方法：

```powershell
# setup-winget.ps1

param(
    [string]$Source = "\\fileserver\dev-tools\winget"
)

$ErrorActionPreference = "Stop"

Write-Host "=== Windows開発環境セットアップ ===" -ForegroundColor Cyan

# OpenJDK 11
Write-Host "[1/4] OpenJDK 11 をインストール中..." -ForegroundColor Yellow
Start-Process msiexec.exe -ArgumentList "/i", "$Source\installers\OpenJDK11U-jdk_x64_windows_hotspot_11.0.21_9.msi", "/qn" -Wait

# Node.js
Write-Host "[2/4] Node.js をインストール中..." -ForegroundColor Yellow
Start-Process msiexec.exe -ArgumentList "/i", "$Source\installers\node-v18.19.0-x64.msi", "/qn" -Wait

# Git
Write-Host "[3/4] Git をインストール中..." -ForegroundColor Yellow
Start-Process "$Source\installers\Git-2.43.0-64-bit.exe" -ArgumentList "/VERYSILENT", "/NORESTART" -Wait

# Gradle（ZIP展開）
Write-Host "[4/4] Gradle をインストール中..." -ForegroundColor Yellow
$gradleDest = "C:\tools\gradle"
New-Item -ItemType Directory -Path $gradleDest -Force | Out-Null
Expand-Archive "$Source\installers\gradle-7.6.1-bin.zip" -DestinationPath $gradleDest -Force

# 環境変数設定
[Environment]::SetEnvironmentVariable("GRADLE_HOME", "$gradleDest\gradle-7.6.1", "Machine")
$path = [Environment]::GetEnvironmentVariable("PATH", "Machine")
[Environment]::SetEnvironmentVariable("PATH", "$path;$gradleDest\gradle-7.6.1\bin", "Machine")

Write-Host ""
Write-Host "=== セットアップ完了 ===" -ForegroundColor Green
Write-Host "ターミナルを再起動してください"
```

---

## winget configuration（YAML形式）

Windows 11 / winget 1.6以降で使用可能：

```yaml
# winget-config.yaml

properties:
  configurationVersion: 0.2.0
  resources:
    - resource: Microsoft.WinGet.DSC/WinGetPackage
      directives:
        description: Install OpenJDK 11
      settings:
        id: Microsoft.OpenJDK.11
        source: winget

    - resource: Microsoft.WinGet.DSC/WinGetPackage
      directives:
        description: Install Git
      settings:
        id: Git.Git
        source: winget

    - resource: Microsoft.WinGet.DSC/WinGetPackage
      directives:
        description: Install Node.js
      settings:
        id: OpenJS.NodeJS.LTS
        source: winget
```

```powershell
# オンライン環境でのみ使用可能
winget configure winget-config.yaml --accept-configuration-agreements
```

---

## winget export/import形式

### packages.json（エクスポート形式）

```json
{
  "$schema": "https://aka.ms/winget-packages.schema.2.0.json",
  "Sources": [
    {
      "Packages": [
        { "PackageIdentifier": "Microsoft.OpenJDK.11" },
        { "PackageIdentifier": "Gradle.Gradle" },
        { "PackageIdentifier": "OpenJS.NodeJS.LTS" },
        { "PackageIdentifier": "Git.Git" },
        { "PackageIdentifier": "Microsoft.VisualStudioCode" }
      ],
      "SourceDetails": {
        "Name": "winget",
        "Type": "Microsoft.PreIndexed.Package",
        "Argument": "https://cdn.winget.microsoft.com/cache"
      }
    }
  ]
}
```

```powershell
# オンライン環境でのみ
winget import -i packages.json --accept-package-agreements
```

---

## 推奨事項

### wingetのオフライン利用は非推奨

| 理由 | 説明 |
|------|------|
| 設計思想 | wingetはオンライン利用を前提に設計 |
| ローカルリポジトリ | 公式サポートなし |
| マニフェスト作成 | 手間がかかる |
| ハッシュ検証 | インストーラーのSHA256が必要 |

### オフライン環境では以下を推奨

1. **Chocolatey** - 完全なオフライン対応
2. **Scoop** - 管理者権限不要
3. **手動スクリプト** - 最もシンプル

---

## wingetが適している場合

- 社内ネットワークからインターネット接続可能
- Windows 11環境
- Microsoft製品中心の構成
- シンプルな定義ファイル管理（JSON/YAML）
