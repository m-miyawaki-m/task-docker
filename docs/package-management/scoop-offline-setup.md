# Scoop オフラインセットアップガイド

## 概要

Scoopを使用して、**管理者権限なし**でオフライン環境からパッケージを配布する方法を解説します。

---

## Scoopの特徴

| 項目 | 内容 |
|------|------|
| 管理者権限 | 不要 |
| インストール先 | `%USERPROFILE%\scoop` |
| パッケージ形式 | ZIP（ポータブル） |
| 設定 | JSON（bucket） |

---

## 共有フォルダ構成

```
\\fileserver\dev-tools\
├── scoop\
│   ├── install\
│   │   └── scoop-master.zip          ← Scoop本体
│   ├── buckets\
│   │   ├── main\                     ← main bucket
│   │   └── java\                     ← java bucket
│   └── cache\
│       ├── openjdk11-11.0.21.zip
│       ├── gradle-7.6.1.zip
│       ├── nodejs-lts-18.19.0.zip
│       └── git-2.43.0.zip
├── apps.json                          ← インストール対象定義
├── setup-scoop.ps1
└── versions.json
```

---

## Phase 1: オンライン環境での準備

### 1-1. Scoop本体のダウンロード

```powershell
# Scoop本体
Invoke-WebRequest -Uri "https://github.com/ScoopInstaller/Scoop/archive/master.zip" `
    -OutFile "scoop-master.zip"

# main bucket
Invoke-WebRequest -Uri "https://github.com/ScoopInstaller/Main/archive/master.zip" `
    -OutFile "main-bucket.zip"

# java bucket
Invoke-WebRequest -Uri "https://github.com/ScoopInstaller/Java/archive/master.zip" `
    -OutFile "java-bucket.zip"
```

### 1-2. パッケージキャッシュの取得

```powershell
# オンライン環境でScoopインストール後
scoop install openjdk11 gradle nodejs-lts git

# キャッシュをコピー
Copy-Item "$env:USERPROFILE\scoop\cache\*" "\\fileserver\dev-tools\scoop\cache\"
```

### 1-3. apps.json の作成

```json
{
  "apps": [
    {
      "name": "git",
      "bucket": "main"
    },
    {
      "name": "openjdk11",
      "bucket": "java"
    },
    {
      "name": "gradle",
      "bucket": "main"
    },
    {
      "name": "nodejs-lts",
      "bucket": "main"
    }
  ]
}
```

---

## Phase 2: オフライン環境でのセットアップ

### 2-1. セットアップスクリプト

```powershell
# setup-scoop.ps1（管理者権限不要）

param(
    [string]$Source = "\\fileserver\dev-tools"
)

$ErrorActionPreference = "Stop"
$scoopDir = "$env:USERPROFILE\scoop"

Write-Host "=== Scoop オフラインセットアップ ===" -ForegroundColor Cyan

# 1. Scoop本体のインストール
Write-Host "[1/5] Scoop本体をインストール中..." -ForegroundColor Yellow

if (!(Test-Path $scoopDir)) {
    New-Item -ItemType Directory -Path $scoopDir -Force | Out-Null
}

# Scoop本体を展開
$scoopZip = Get-ChildItem "$Source\scoop\install\scoop-master.zip" | Select-Object -First 1
Expand-Archive $scoopZip.FullName -DestinationPath "$scoopDir\temp" -Force
Move-Item "$scoopDir\temp\Scoop-master\*" "$scoopDir\apps\scoop\current" -Force
Remove-Item "$scoopDir\temp" -Recurse -Force

# 2. 環境変数設定
Write-Host "[2/5] 環境変数を設定中..." -ForegroundColor Yellow

$scoopShims = "$scoopDir\shims"
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($currentPath -notlike "*$scoopShims*") {
    [Environment]::SetEnvironmentVariable("PATH", "$scoopShims;$currentPath", "User")
}
[Environment]::SetEnvironmentVariable("SCOOP", $scoopDir, "User")

$env:PATH = "$scoopShims;$env:PATH"
$env:SCOOP = $scoopDir

# 3. Bucketの設定
Write-Host "[3/5] Bucketを設定中..." -ForegroundColor Yellow

$bucketsDir = "$scoopDir\buckets"
New-Item -ItemType Directory -Path $bucketsDir -Force | Out-Null

# main bucket
Expand-Archive "$Source\scoop\buckets\main-bucket.zip" -DestinationPath "$bucketsDir\temp" -Force
Move-Item "$bucketsDir\temp\Main-master" "$bucketsDir\main" -Force

# java bucket
Expand-Archive "$Source\scoop\buckets\java-bucket.zip" -DestinationPath "$bucketsDir\temp" -Force
Move-Item "$bucketsDir\temp\Java-master" "$bucketsDir\java" -Force

Remove-Item "$bucketsDir\temp" -Recurse -Force -ErrorAction SilentlyContinue

# 4. キャッシュのコピー
Write-Host "[4/5] キャッシュをコピー中..." -ForegroundColor Yellow

$cacheDir = "$scoopDir\cache"
New-Item -ItemType Directory -Path $cacheDir -Force | Out-Null
Copy-Item "$Source\scoop\cache\*" $cacheDir -Force

# 5. アプリのインストール
Write-Host "[5/5] アプリをインストール中..." -ForegroundColor Yellow

$apps = Get-Content "$Source\apps.json" | ConvertFrom-Json

foreach ($app in $apps.apps) {
    Write-Host "  Installing $($app.name)..." -ForegroundColor Gray

    # キャッシュからインストール（オフライン）
    scoop install $app.name --skip
}

# 確認
Write-Host ""
Write-Host "=== セットアップ完了 ===" -ForegroundColor Green
scoop list

Write-Host ""
Write-Host "ターミナルを再起動してください"
```

### 2-2. 実行方法

```powershell
# 通常ユーザー権限で実行可能
\\fileserver\dev-tools\setup-scoop.ps1

# または引数指定
.\setup-scoop.ps1 -Source "D:\offline-tools"
```

---

## パッケージ定義

### apps.json

```json
{
  "apps": [
    { "name": "git", "bucket": "main" },
    { "name": "openjdk11", "bucket": "java" },
    { "name": "gradle", "bucket": "main" },
    { "name": "nodejs-lts", "bucket": "main" },
    { "name": "vscode", "bucket": "extras" }
  ],
  "options": {
    "skip_hash_check": true
  }
}
```

---

## 運用コマンド

### インストール済みアプリの確認

```powershell
scoop list
```

### アプリの更新

```powershell
# オフライン：キャッシュに新バージョンを配置後
scoop update *

# 特定アプリのみ
scoop update gradle
```

### アンインストール

```powershell
scoop uninstall gradle
```

### 環境のリセット

```powershell
# Scoop完全削除
Remove-Item "$env:USERPROFILE\scoop" -Recurse -Force
```

---

## 環境変数

Scoopはインストール時に自動で環境変数を設定しますが、手動確認：

```powershell
# 確認
$env:JAVA_HOME
$env:GRADLE_HOME

# Scoopのアプリは shims 経由でPATHに追加される
# 例: %USERPROFILE%\scoop\shims\java.exe
```

---

## Chocolatey vs Scoop

| 項目 | Chocolatey | Scoop |
|------|------------|-------|
| 管理者権限 | **必要** | 不要 |
| インストール先 | システム全体 | ユーザーフォルダ |
| 適用範囲 | 全ユーザー | 実行ユーザーのみ |
| アンインストール | 残留ファイルあり | クリーン |
| 企業利用 | ◎ | ○ |

**管理者権限がない場合はScoopを推奨**
