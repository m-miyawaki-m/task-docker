# 手動スクリプトによるセットアップガイド

## 概要

パッケージマネージャーを使用せず、PowerShellスクリプトで直接ツールを配布・インストールする方法です。

**最もシンプルで確実なオフライン対応方法**です。

---

## 特徴

| 項目 | 内容 |
|------|------|
| 依存関係 | なし（PowerShell標準機能のみ） |
| 管理者権限 | 設定による（ユーザー権限でも可） |
| カスタマイズ | 完全に自由 |
| オフライン対応 | ◎ 完全対応 |

---

## 共有フォルダ構成

```
\\fileserver\dev-tools\
├── packages\
│   ├── java\
│   │   └── OpenJDK11U-jdk_x64_windows_hotspot_11.0.21_9.zip
│   ├── gradle\
│   │   └── gradle-7.6.1-bin.zip
│   ├── node\
│   │   └── node-v18.19.0-win-x64.zip
│   ├── git\
│   │   └── PortableGit-2.43.0-64-bit.7z.exe
│   └── vscode\
│       └── VSCode-win32-x64-1.85.0.zip
├── scripts\
│   ├── setup-dev-env.ps1             ← メインスクリプト
│   ├── setup-dev-env-advanced.ps1    ← 高機能版
│   └── functions.ps1                  ← 共通関数
├── versions.json
└── README.md
```

---

## セットアップスクリプト

### シンプル版（setup-dev-env.ps1）

```powershell
# setup-dev-env.ps1
# 開発環境セットアップスクリプト

param(
    [string]$Source = "\\fileserver\dev-tools",
    [string]$Dest = "C:\dev-tools"
)

$ErrorActionPreference = "Stop"

Write-Host "=== 開発環境セットアップ ===" -ForegroundColor Cyan
Write-Host "Source: $Source"
Write-Host "Dest:   $Dest"
Write-Host ""

# インストール先作成
if (!(Test-Path $Dest)) {
    New-Item -ItemType Directory -Path $Dest -Force | Out-Null
}

# --- Java ---
Write-Host "[1/5] Java (OpenJDK 11) インストール中..." -ForegroundColor Yellow

$javaZip = Get-ChildItem "$Source\packages\java\*.zip" | Select-Object -First 1
if ($javaZip) {
    Expand-Archive $javaZip.FullName -DestinationPath "$Dest\java" -Force
    $javaHome = Get-ChildItem "$Dest\java" -Directory | Select-Object -First 1
    [Environment]::SetEnvironmentVariable("JAVA_HOME", $javaHome.FullName, "User")
    Write-Host "  JAVA_HOME = $($javaHome.FullName)" -ForegroundColor Gray
}

# --- Gradle ---
Write-Host "[2/5] Gradle インストール中..." -ForegroundColor Yellow

$gradleZip = Get-ChildItem "$Source\packages\gradle\*.zip" | Select-Object -First 1
if ($gradleZip) {
    Expand-Archive $gradleZip.FullName -DestinationPath "$Dest\gradle" -Force
    $gradleHome = Get-ChildItem "$Dest\gradle" -Directory | Select-Object -First 1
    [Environment]::SetEnvironmentVariable("GRADLE_HOME", $gradleHome.FullName, "User")
    Write-Host "  GRADLE_HOME = $($gradleHome.FullName)" -ForegroundColor Gray
}

# --- Node.js ---
Write-Host "[3/5] Node.js インストール中..." -ForegroundColor Yellow

$nodeZip = Get-ChildItem "$Source\packages\node\*.zip" | Select-Object -First 1
if ($nodeZip) {
    Expand-Archive $nodeZip.FullName -DestinationPath "$Dest\node" -Force
    $nodeHome = Get-ChildItem "$Dest\node" -Directory | Select-Object -First 1
    [Environment]::SetEnvironmentVariable("NODE_HOME", $nodeHome.FullName, "User")
    Write-Host "  NODE_HOME = $($nodeHome.FullName)" -ForegroundColor Gray
}

# --- Git ---
Write-Host "[4/5] Git インストール中..." -ForegroundColor Yellow

$gitExe = Get-ChildItem "$Source\packages\git\*.exe" | Select-Object -First 1
if ($gitExe) {
    # PortableGit の場合は自己展開
    $gitDest = "$Dest\git"
    Start-Process $gitExe.FullName -ArgumentList "-o`"$gitDest`"", "-y" -Wait
    Write-Host "  Git installed to $gitDest" -ForegroundColor Gray
}

# --- PATH設定 ---
Write-Host "[5/5] PATH設定中..." -ForegroundColor Yellow

$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$pathsToAdd = @()

if ($javaHome) { $pathsToAdd += "$($javaHome.FullName)\bin" }
if ($gradleHome) { $pathsToAdd += "$($gradleHome.FullName)\bin" }
if ($nodeHome) { $pathsToAdd += $nodeHome.FullName }
if (Test-Path "$Dest\git\bin") { $pathsToAdd += "$Dest\git\bin" }

foreach ($p in $pathsToAdd) {
    if ($currentPath -notlike "*$p*") {
        $currentPath = "$p;$currentPath"
    }
}
[Environment]::SetEnvironmentVariable("PATH", $currentPath, "User")

# --- 完了 ---
Write-Host ""
Write-Host "=== セットアップ完了 ===" -ForegroundColor Green
Write-Host ""
Write-Host "インストール済みツール:"
Write-Host "  JAVA_HOME  : $($javaHome.FullName)"
Write-Host "  GRADLE_HOME: $($gradleHome.FullName)"
Write-Host "  NODE_HOME  : $($nodeHome.FullName)"
Write-Host "  Git        : $Dest\git"
Write-Host ""
Write-Host "ターミナルを再起動して以下を確認してください:" -ForegroundColor Cyan
Write-Host "  java -version"
Write-Host "  gradle -v"
Write-Host "  node -v"
Write-Host "  git --version"
```

---

### 高機能版（setup-dev-env-advanced.ps1）

```powershell
# setup-dev-env-advanced.ps1
# バージョン管理・更新チェック対応版

param(
    [string]$Source = "\\fileserver\dev-tools",
    [string]$Dest = "C:\dev-tools",
    [switch]$Force,
    [switch]$CheckOnly
)

$ErrorActionPreference = "Stop"

# バージョン情報読み込み
$remoteVersions = Get-Content "$Source\versions.json" | ConvertFrom-Json
$localVersionFile = "$Dest\versions.json"

if (Test-Path $localVersionFile) {
    $localVersions = Get-Content $localVersionFile | ConvertFrom-Json
} else {
    $localVersions = @{ packages = @{} }
}

function Install-Tool {
    param(
        [string]$Name,
        [string]$ZipPattern,
        [string]$SubDir,
        [string]$EnvVarName
    )

    $remoteVer = $remoteVersions.packages.$Name
    $localVer = $localVersions.packages.$Name

    if (!$Force -and ($remoteVer -eq $localVer)) {
        Write-Host "[$Name] 最新版 (v$localVer) インストール済み - スキップ" -ForegroundColor Gray
        return $null
    }

    if ($CheckOnly) {
        if ($localVer) {
            Write-Host "[$Name] 更新あり: v$localVer → v$remoteVer" -ForegroundColor Yellow
        } else {
            Write-Host "[$Name] 新規インストール: v$remoteVer" -ForegroundColor Yellow
        }
        return $null
    }

    Write-Host "[$Name] インストール中... v$remoteVer" -ForegroundColor Yellow

    # 古いバージョン削除
    $destPath = "$Dest\$SubDir"
    if (Test-Path $destPath) {
        Remove-Item $destPath -Recurse -Force
    }

    # 展開
    $zip = Get-ChildItem "$Source\packages\$SubDir\$ZipPattern" | Select-Object -First 1
    if (!$zip) {
        Write-Host "  パッケージが見つかりません: $ZipPattern" -ForegroundColor Red
        return $null
    }

    Expand-Archive $zip.FullName -DestinationPath $destPath -Force

    $installDir = Get-ChildItem $destPath -Directory | Select-Object -First 1

    # 環境変数設定
    if ($EnvVarName -and $installDir) {
        [Environment]::SetEnvironmentVariable($EnvVarName, $installDir.FullName, "User")
    }

    # バージョン記録
    if (!$localVersions.packages) {
        $localVersions | Add-Member -NotePropertyName "packages" -NotePropertyValue @{} -Force
    }
    $localVersions.packages | Add-Member -NotePropertyName $Name -NotePropertyValue $remoteVer -Force

    return $installDir.FullName
}

Write-Host "=== 開発環境セットアップ (Advanced) ===" -ForegroundColor Cyan
Write-Host "Source: $Source"
Write-Host "Dest:   $Dest"
Write-Host "Remote Version: $($remoteVersions.version) (Updated: $($remoteVersions.updated))"
Write-Host ""

if ($CheckOnly) {
    Write-Host "--- 更新チェックモード ---" -ForegroundColor Cyan
}

# インストール先作成
if (!(Test-Path $Dest)) {
    New-Item -ItemType Directory -Path $Dest -Force | Out-Null
}

# 各ツールのインストール
$javaHome = Install-Tool -Name "java" -ZipPattern "*.zip" -SubDir "java" -EnvVarName "JAVA_HOME"
$gradleHome = Install-Tool -Name "gradle" -ZipPattern "*.zip" -SubDir "gradle" -EnvVarName "GRADLE_HOME"
$nodeHome = Install-Tool -Name "node" -ZipPattern "*.zip" -SubDir "node" -EnvVarName "NODE_HOME"

if ($CheckOnly) {
    Write-Host ""
    Write-Host "更新を適用するには -Force オプションなしで再実行してください"
    exit 0
}

# PATH設定
Write-Host ""
Write-Host "PATH設定中..." -ForegroundColor Yellow

$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$pathsToAdd = @()

if ($javaHome) { $pathsToAdd += "$javaHome\bin" }
if ($gradleHome) { $pathsToAdd += "$gradleHome\bin" }
if ($nodeHome) { $pathsToAdd += $nodeHome }

foreach ($p in $pathsToAdd) {
    if ($currentPath -notlike "*$p*") {
        $currentPath = "$p;$currentPath"
    }
}
[Environment]::SetEnvironmentVariable("PATH", $currentPath, "User")

# ローカルバージョン情報保存
$localVersions | ConvertTo-Json -Depth 10 | Set-Content $localVersionFile

Write-Host ""
Write-Host "=== セットアップ完了 ===" -ForegroundColor Green
```

---

## バージョン管理ファイル

### versions.json

```json
{
  "version": "1.0",
  "updated": "2024-01-15",
  "packages": {
    "java": "11.0.21",
    "gradle": "7.6.1",
    "node": "18.19.0",
    "git": "2.43.0"
  }
}
```

---

## 使用方法

### 初回セットアップ

```powershell
# シンプル版
\\fileserver\dev-tools\scripts\setup-dev-env.ps1

# 高機能版
\\fileserver\dev-tools\scripts\setup-dev-env-advanced.ps1
```

### 更新チェック

```powershell
# 更新があるか確認のみ
.\setup-dev-env-advanced.ps1 -CheckOnly
```

### 強制再インストール

```powershell
.\setup-dev-env-advanced.ps1 -Force
```

### インストール先変更

```powershell
.\setup-dev-env.ps1 -Dest "D:\dev-tools"
```

---

## メリット・デメリット

### メリット

| 項目 | 内容 |
|------|------|
| 依存関係なし | PowerShell標準機能のみで動作 |
| 完全制御 | インストール先、環境変数を完全制御 |
| 透明性 | 何が行われるか明確 |
| トラブル少 | パッケージマネージャー固有の問題なし |
| オフライン | 完全対応 |

### デメリット

| 項目 | 内容 |
|------|------|
| 手動管理 | パッケージ取得は手動 |
| 依存解決なし | ツール間の依存は自分で管理 |
| アンインストール | 削除スクリプトを別途作成必要 |

---

## アンインストールスクリプト

```powershell
# uninstall-dev-env.ps1

param(
    [string]$Dest = "C:\dev-tools"
)

Write-Host "=== 開発環境アンインストール ===" -ForegroundColor Cyan

# 環境変数削除
[Environment]::SetEnvironmentVariable("JAVA_HOME", $null, "User")
[Environment]::SetEnvironmentVariable("GRADLE_HOME", $null, "User")
[Environment]::SetEnvironmentVariable("NODE_HOME", $null, "User")

# PATHから削除
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = ($currentPath -split ";" | Where-Object { $_ -notlike "*$Dest*" }) -join ";"
[Environment]::SetEnvironmentVariable("PATH", $newPath, "User")

# フォルダ削除
if (Test-Path $Dest) {
    Remove-Item $Dest -Recurse -Force
    Write-Host "Removed: $Dest" -ForegroundColor Yellow
}

Write-Host "=== アンインストール完了 ===" -ForegroundColor Green
```
