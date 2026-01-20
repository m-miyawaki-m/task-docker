# CSV + スクリプトによるシンプルパッケージ管理

## 概要

パッケージマネージャーを使わず、CSVファイルでバージョン・URLを管理し、PowerShellスクリプトでダウンロード・インストールを行うシンプルな方式です。

**オフライン環境では最も実用的な方法**です。

---

## なぜCSV + スクリプトか

### パッケージマネージャー vs CSV + スクリプト

| 項目 | Chocolatey等 | CSV + スクリプト |
|------|--------------|------------------|
| 事前準備 | 多い（nupkg化等） | **少ない（ZIP配置のみ）** |
| 依存関係 | パッケージマネージャー本体 | **なし** |
| 学習コスト | 中〜高 | **低** |
| トラブル時 | ブラックボックス | **透明** |
| カスタマイズ | 制限あり | **完全に自由** |
| バージョン管理 | 専用形式 | **CSV（Excel編集可）** |

### オフラインでパッケージマネージャーを使うメリットが薄い理由

- 依存解決 → 開発ツール（JDK, Gradle等）は依存が単純
- アップデート検知 → オフラインでは意味がない
- 統一コマンド → 使用頻度が低い（初回セットアップのみ）

---

## 共有フォルダ構成

```
\\fileserver\dev-tools\
├── packages.csv                      ← パッケージ定義（メイン）
├── packages\                         ← ダウンロード済みファイル
│   ├── java\
│   │   └── OpenJDK11U-jdk_x64_windows_hotspot_11.0.21_9.zip
│   ├── gradle\
│   │   └── gradle-7.6.1-bin.zip
│   ├── node\
│   │   └── node-v18.19.0-win-x64.zip
│   └── git\
│       └── PortableGit-2.43.0-64-bit.7z.exe
├── scripts\
│   ├── download-packages.ps1         ← ダウンロード用（オンライン）
│   ├── setup-dev-env.ps1             ← セットアップ用（オフライン）
│   └── uninstall-dev-env.ps1         ← アンインストール用
└── README.md
```

---

## packages.csv

### 形式

```csv
name,version,url,filename,install_type,env_var,path_add
java,11.0.21,https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.21%2B9/OpenJDK11U-jdk_x64_windows_hotspot_11.0.21_9.zip,OpenJDK11U-jdk_x64_windows_hotspot_11.0.21_9.zip,zip,JAVA_HOME,bin
gradle,7.6.1,https://services.gradle.org/distributions/gradle-7.6.1-bin.zip,gradle-7.6.1-bin.zip,zip,GRADLE_HOME,bin
node,18.19.0,https://nodejs.org/dist/v18.19.0/node-v18.19.0-win-x64.zip,node-v18.19.0-win-x64.zip,zip,NODE_HOME,
git,2.43.0,https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/PortableGit-2.43.0-64-bit.7z.exe,PortableGit-2.43.0-64-bit.7z.exe,7z_sfx,,bin
vscode,1.85.0,https://update.code.visualstudio.com/1.85.0/win32-x64-archive/stable,VSCode-win32-x64-1.85.0.zip,zip,,
```

### 列の説明

| 列名 | 説明 | 例 |
|------|------|-----|
| name | パッケージ名 | java |
| version | バージョン | 11.0.21 |
| url | ダウンロードURL | https://... |
| filename | ファイル名 | OpenJDK11U-*.zip |
| install_type | インストール種別 | zip / 7z_sfx / msi / exe |
| env_var | 設定する環境変数 | JAVA_HOME |
| path_add | PATHに追加するサブディレクトリ | bin |

---

## スクリプト

### download-packages.ps1（オンライン環境用）

```powershell
<#
.SYNOPSIS
    packages.csv に記載されたURLからファイルをダウンロードする

.PARAMETER CsvPath
    packages.csv のパス

.PARAMETER OutputDir
    ダウンロード先ディレクトリ

.EXAMPLE
    .\download-packages.ps1 -OutputDir "\\fileserver\dev-tools\packages"
#>

param(
    [string]$CsvPath = ".\packages.csv",
    [string]$OutputDir = ".\packages"
)

$ErrorActionPreference = "Stop"

Write-Host "=== パッケージダウンロード ===" -ForegroundColor Cyan
Write-Host "CSV: $CsvPath"
Write-Host "Output: $OutputDir"
Write-Host ""

$packages = Import-Csv $CsvPath

foreach ($pkg in $packages) {
    $pkgDir = Join-Path $OutputDir $pkg.name
    $outFile = Join-Path $pkgDir $pkg.filename

    # ディレクトリ作成
    if (!(Test-Path $pkgDir)) {
        New-Item -ItemType Directory -Path $pkgDir -Force | Out-Null
    }

    # 既にダウンロード済みかチェック
    if (Test-Path $outFile) {
        Write-Host "[$($pkg.name)] 既にダウンロード済み: $($pkg.filename)" -ForegroundColor Gray
        continue
    }

    Write-Host "[$($pkg.name)] ダウンロード中... v$($pkg.version)" -ForegroundColor Yellow
    Write-Host "  URL: $($pkg.url)" -ForegroundColor Gray

    try {
        # プログレス表示を抑制（高速化）
        $ProgressPreference = 'SilentlyContinue'
        Invoke-WebRequest -Uri $pkg.url -OutFile $outFile -UseBasicParsing
        Write-Host "  完了: $($pkg.filename)" -ForegroundColor Green
    }
    catch {
        Write-Host "  エラー: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "=== ダウンロード完了 ===" -ForegroundColor Green
Write-Host "ファイル一覧:"
Get-ChildItem $OutputDir -Recurse -File | ForEach-Object {
    Write-Host "  $($_.FullName)"
}
```

---

### setup-dev-env.ps1（オフライン環境用）

```powershell
<#
.SYNOPSIS
    共有フォルダからパッケージをインストールする

.PARAMETER Source
    共有フォルダのパス

.PARAMETER Dest
    インストール先

.PARAMETER CsvPath
    packages.csv のパス（Sourceからの相対パス）

.EXAMPLE
    .\setup-dev-env.ps1 -Source "\\fileserver\dev-tools"
#>

param(
    [string]$Source = "\\fileserver\dev-tools",
    [string]$Dest = "C:\dev-tools",
    [string]$CsvPath = "packages.csv"
)

$ErrorActionPreference = "Stop"

Write-Host "=== 開発環境セットアップ ===" -ForegroundColor Cyan
Write-Host "Source: $Source"
Write-Host "Dest:   $Dest"
Write-Host ""

# CSV読み込み
$csvFullPath = Join-Path $Source $CsvPath
if (!(Test-Path $csvFullPath)) {
    Write-Host "CSVが見つかりません: $csvFullPath" -ForegroundColor Red
    exit 1
}

$packages = Import-Csv $csvFullPath
$totalCount = $packages.Count
$currentCount = 0

# インストール先作成
if (!(Test-Path $Dest)) {
    New-Item -ItemType Directory -Path $Dest -Force | Out-Null
}

# インストール結果を記録
$installed = @()

foreach ($pkg in $packages) {
    $currentCount++
    Write-Host "[$currentCount/$totalCount] $($pkg.name) v$($pkg.version) インストール中..." -ForegroundColor Yellow

    $srcDir = Join-Path $Source "packages\$($pkg.name)"
    $srcFile = Join-Path $srcDir $pkg.filename
    $destDir = Join-Path $Dest $pkg.name

    # ファイル存在チェック
    if (!(Test-Path $srcFile)) {
        Write-Host "  スキップ: ファイルが見つかりません" -ForegroundColor Red
        continue
    }

    # インストール先作成
    if (!(Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }

    # インストール種別に応じて処理
    $installPath = $null

    switch ($pkg.install_type) {
        "zip" {
            Expand-Archive $srcFile -DestinationPath $destDir -Force
            $installPath = (Get-ChildItem $destDir -Directory | Select-Object -First 1).FullName
            if (!$installPath) { $installPath = $destDir }
        }
        "7z_sfx" {
            # 7z自己展開形式
            Start-Process $srcFile -ArgumentList "-o`"$destDir`"", "-y" -Wait -NoNewWindow
            $installPath = $destDir
        }
        "msi" {
            # MSIインストーラー（サイレント）
            Start-Process msiexec.exe -ArgumentList "/i", "`"$srcFile`"", "/qn" -Wait
            # MSIの場合はProgram Filesにインストールされる
            $installPath = $null
        }
        "exe" {
            # EXEインストーラー（サイレント）
            Start-Process $srcFile -ArgumentList "/S" -Wait
            $installPath = $null
        }
        default {
            Write-Host "  未対応のインストール種別: $($pkg.install_type)" -ForegroundColor Red
            continue
        }
    }

    Write-Host "  展開完了: $destDir" -ForegroundColor Gray

    # 環境変数設定
    if ($pkg.env_var -and $installPath) {
        [Environment]::SetEnvironmentVariable($pkg.env_var, $installPath, "User")
        Write-Host "  環境変数: $($pkg.env_var) = $installPath" -ForegroundColor Gray
    }

    # インストール結果記録
    $installed += [PSCustomObject]@{
        Name = $pkg.name
        Version = $pkg.version
        Path = $installPath
        EnvVar = $pkg.env_var
        PathAdd = $pkg.path_add
    }
}

# PATH設定
Write-Host ""
Write-Host "PATH設定中..." -ForegroundColor Yellow

$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$pathsToAdd = @()

foreach ($item in $installed) {
    if ($item.Path -and $item.PathAdd) {
        $addPath = Join-Path $item.Path $item.PathAdd
        if (Test-Path $addPath) {
            $pathsToAdd += $addPath
        }
    }
    elseif ($item.Path -and !$item.PathAdd) {
        # path_addが空の場合はインストールパス自体を追加
        if ($item.Name -eq "node") {
            $pathsToAdd += $item.Path
        }
    }
}

foreach ($p in $pathsToAdd) {
    if ($currentPath -notlike "*$p*") {
        $currentPath = "$p;$currentPath"
        Write-Host "  PATH追加: $p" -ForegroundColor Gray
    }
}

[Environment]::SetEnvironmentVariable("PATH", $currentPath, "User")

# インストール情報を保存
$installedJsonPath = Join-Path $Dest "installed.json"
$installed | ConvertTo-Json | Set-Content $installedJsonPath

# 完了メッセージ
Write-Host ""
Write-Host "=== セットアップ完了 ===" -ForegroundColor Green
Write-Host ""
Write-Host "インストール済みパッケージ:" -ForegroundColor Cyan

foreach ($item in $installed) {
    Write-Host "  $($item.Name) v$($item.Version)"
    if ($item.EnvVar) {
        Write-Host "    $($item.EnvVar) = $($item.Path)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "ターミナルを再起動して以下のコマンドで確認してください:" -ForegroundColor Cyan
Write-Host "  java -version"
Write-Host "  gradle -v"
Write-Host "  node -v"
Write-Host "  git --version"
```

---

### uninstall-dev-env.ps1（アンインストール用）

```powershell
<#
.SYNOPSIS
    インストールした開発環境を削除する

.PARAMETER Dest
    インストール先ディレクトリ

.EXAMPLE
    .\uninstall-dev-env.ps1
#>

param(
    [string]$Dest = "C:\dev-tools"
)

$ErrorActionPreference = "Stop"

Write-Host "=== 開発環境アンインストール ===" -ForegroundColor Cyan

# インストール情報読み込み
$installedJsonPath = Join-Path $Dest "installed.json"

if (Test-Path $installedJsonPath) {
    $installed = Get-Content $installedJsonPath | ConvertFrom-Json

    # 環境変数削除
    foreach ($item in $installed) {
        if ($item.EnvVar) {
            [Environment]::SetEnvironmentVariable($item.EnvVar, $null, "User")
            Write-Host "環境変数削除: $($item.EnvVar)" -ForegroundColor Yellow
        }
    }
}

# PATHから削除
$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$newPath = ($currentPath -split ";" | Where-Object { $_ -notlike "*$Dest*" }) -join ";"
[Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
Write-Host "PATH更新完了" -ForegroundColor Yellow

# フォルダ削除
if (Test-Path $Dest) {
    Remove-Item $Dest -Recurse -Force
    Write-Host "フォルダ削除: $Dest" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== アンインストール完了 ===" -ForegroundColor Green
```

---

## 運用フロー

### 初回構築（管理者）

```
1. packages.csv を作成
2. オンライン環境で download-packages.ps1 実行
3. 共有フォルダに配置
```

```powershell
# オンライン環境
.\download-packages.ps1 -OutputDir "\\fileserver\dev-tools\packages"
```

### 開発者セットアップ

```powershell
# オフライン環境
\\fileserver\dev-tools\scripts\setup-dev-env.ps1
```

### パッケージ更新（管理者）

```
1. packages.csv のバージョンとURLを更新
2. 新バージョンをダウンロード
3. 共有フォルダに配置
4. 開発者に通知
```

```powershell
# 差分ダウンロード（既存ファイルはスキップ）
.\download-packages.ps1 -OutputDir "\\fileserver\dev-tools\packages"
```

### 開発者の更新適用

```powershell
# 再セットアップ
\\fileserver\dev-tools\scripts\setup-dev-env.ps1 -Dest "C:\dev-tools"
```

---

## カスタマイズ例

### 特定パッケージのみインストール

```powershell
# packages.csv をフィルタリング
$packages = Import-Csv "packages.csv" | Where-Object { $_.name -in @("java", "gradle") }
```

### バージョン確認スクリプト

```powershell
# check-versions.ps1

$installed = Get-Content "C:\dev-tools\installed.json" | ConvertFrom-Json
$remote = Import-Csv "\\fileserver\dev-tools\packages.csv"

Write-Host "バージョン比較:" -ForegroundColor Cyan
foreach ($r in $remote) {
    $l = $installed | Where-Object { $_.Name -eq $r.name }
    if ($l.Version -ne $r.version) {
        Write-Host "  $($r.name): $($l.Version) → $($r.version) (更新あり)" -ForegroundColor Yellow
    } else {
        Write-Host "  $($r.name): $($l.Version) (最新)" -ForegroundColor Gray
    }
}
```

---

## メリット・デメリット

### メリット

| 項目 | 内容 |
|------|------|
| シンプル | CSV編集とスクリプト実行のみ |
| 透明性 | 何がインストールされるか完全に把握 |
| 依存なし | PowerShell標準機能のみ |
| Excel対応 | CSVはExcelで編集可能 |
| カスタマイズ自由 | スクリプトを自由に改変可能 |
| トラブル対応容易 | 問題箇所が特定しやすい |

### デメリット

| 項目 | 対策 |
|------|------|
| 依存解決なし | 必要なら手動でCSVに追加 |
| アンインストール | uninstallスクリプトで対応 |
| 更新検知 | check-versionsスクリプトで対応 |

---

## 結論

**オフライン環境での開発ツール配布は CSV + PowerShellスクリプト が最適解**

- パッケージマネージャーのオーバーヘッドなし
- 何が起きているか完全に把握可能
- 問題発生時の切り分けが容易
- Excelでバージョン管理可能

---

## 拡張版: ハッシュ検証・環境変数対応

より堅牢な運用のため、以下の機能を追加した拡張版です。

### packages.csv（拡張版）

```csv
name,version,url,filename,sha256,install_type,env_var,env_value_suffix,path_add,post_install
java,11.0.21,https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.21%2B9/OpenJDK11U-jdk_x64_windows_hotspot_11.0.21_9.zip,OpenJDK11U-jdk_x64_windows_hotspot_11.0.21_9.zip,a1b2c3d4e5f6...,zip,JAVA_HOME,,bin,
gradle,7.6.1,https://services.gradle.org/distributions/gradle-7.6.1-bin.zip,gradle-7.6.1-bin.zip,b2c3d4e5f6a7...,zip,GRADLE_HOME,,bin,
node,18.19.0,https://nodejs.org/dist/v18.19.0/node-v18.19.0-win-x64.zip,node-v18.19.0-win-x64.zip,c3d4e5f6a7b8...,zip,NODE_HOME,,,
git,2.43.0,https://github.com/git-for-windows/git/releases/download/v2.43.0.windows.1/PortableGit-2.43.0-64-bit.7z.exe,PortableGit-2.43.0-64-bit.7z.exe,d4e5f6a7b8c9...,7z_sfx,,,bin,
maven,3.9.6,https://dlcdn.apache.org/maven/maven-3/3.9.6/binaries/apache-maven-3.9.6-bin.zip,apache-maven-3.9.6-bin.zip,e5f6a7b8c9d0...,zip,MAVEN_HOME;M2_HOME,,bin,
```

### 拡張列の説明

| 列名 | 説明 | 例 |
|------|------|-----|
| sha256 | ファイルのSHA256ハッシュ値 | a1b2c3d4... |
| env_value_suffix | 環境変数値に追加するサフィックス | （空=自動検出） |
| post_install | インストール後実行コマンド | npm install -g yarn |

**env_var に複数指定**: セミコロン区切りで複数の環境変数を設定可能（例: `MAVEN_HOME;M2_HOME`）

---

### setup-dev-env-v2.ps1（拡張版セットアップスクリプト）

```powershell
<#
.SYNOPSIS
    拡張版セットアップスクリプト（ハッシュ検証・環境変数対応）

.PARAMETER Source
    共有フォルダのパス

.PARAMETER Dest
    インストール先

.PARAMETER SkipHashCheck
    ハッシュ検証をスキップ

.PARAMETER Force
    既存インストールを上書き

.EXAMPLE
    .\setup-dev-env-v2.ps1 -Source "\\fileserver\dev-tools"
    .\setup-dev-env-v2.ps1 -SkipHashCheck -Force
#>

param(
    [string]$Source = "\\fileserver\dev-tools",
    [string]$Dest = "C:\dev-tools",
    [switch]$SkipHashCheck,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# ========== 関数定義 ==========

function Test-FileHash {
    param([string]$FilePath, [string]$ExpectedHash)

    if ([string]::IsNullOrEmpty($ExpectedHash)) {
        return $true  # ハッシュ未設定はスキップ
    }

    $actualHash = (Get-FileHash $FilePath -Algorithm SHA256).Hash
    return $actualHash -eq $ExpectedHash.ToUpper()
}

function Install-Package {
    param($Package, $SrcFile, $DestDir)

    switch ($Package.install_type) {
        "zip" {
            Expand-Archive $SrcFile -DestinationPath $DestDir -Force
            return (Get-ChildItem $DestDir -Directory | Select-Object -First 1).FullName
        }
        "7z_sfx" {
            # 7z自己展開形式
            Start-Process $SrcFile -ArgumentList "-o`"$DestDir`"", "-y" -Wait -NoNewWindow
            return $DestDir
        }
        "msi" {
            # MSIインストーラー（サイレント）
            Start-Process msiexec.exe -ArgumentList "/i", "`"$SrcFile`"", "/qn", "INSTALLDIR=`"$DestDir`"" -Wait
            return $DestDir
        }
        "exe" {
            # EXEインストーラー（サイレント）
            Start-Process $SrcFile -ArgumentList "/S", "/D=$DestDir" -Wait
            return $DestDir
        }
        default {
            throw "未対応のインストール種別: $($Package.install_type)"
        }
    }
}

function Set-EnvironmentVariables {
    param($Package, $InstallPath)

    if ([string]::IsNullOrEmpty($Package.env_var)) { return }

    # 複数の環境変数に対応（セミコロン区切り）
    $envVars = $Package.env_var -split ";"

    foreach ($envVar in $envVars) {
        $envVar = $envVar.Trim()
        if ([string]::IsNullOrEmpty($envVar)) { continue }

        $value = $InstallPath
        if ($Package.env_value_suffix) {
            $value = Join-Path $InstallPath $Package.env_value_suffix
        }

        [Environment]::SetEnvironmentVariable($envVar, $value, "User")
        Write-Host "    環境変数: $envVar = $value" -ForegroundColor Gray
    }
}

function Add-ToPath {
    param($Package, $InstallPath)

    if ([string]::IsNullOrEmpty($Package.path_add)) { return $null }

    $pathToAdd = Join-Path $InstallPath $Package.path_add
    if (!(Test-Path $pathToAdd)) {
        # path_addがない場合はインストールパス直下を使用
        $pathToAdd = $InstallPath
    }

    return $pathToAdd
}

# ========== メイン処理 ==========

Write-Host "=== 開発環境セットアップ v2 ===" -ForegroundColor Cyan
Write-Host "Source: $Source"
Write-Host "Dest:   $Dest"
Write-Host "ハッシュ検証: $(-not $SkipHashCheck)"
Write-Host "強制上書き: $Force"
Write-Host ""

# CSV読み込み
$csvPath = Join-Path $Source "packages.csv"
if (!(Test-Path $csvPath)) {
    Write-Host "エラー: CSVが見つかりません: $csvPath" -ForegroundColor Red
    exit 1
}

$packages = Import-Csv $csvPath
$totalCount = $packages.Count
$currentCount = 0

# インストール先作成
New-Item -ItemType Directory -Path $Dest -Force | Out-Null

$installed = @()
$skipped = @()
$pathsToAdd = @()
$errors = @()

foreach ($pkg in $packages) {
    $currentCount++
    Write-Host "[$currentCount/$totalCount] $($pkg.name) v$($pkg.version)" -ForegroundColor Yellow

    $srcDir = Join-Path $Source "packages\$($pkg.name)"
    $srcFile = Join-Path $srcDir $pkg.filename
    $destDir = Join-Path $Dest $pkg.name

    # ファイル存在チェック
    if (!(Test-Path $srcFile)) {
        Write-Host "    スキップ: ファイルなし ($($pkg.filename))" -ForegroundColor Red
        $errors += "$($pkg.name): ファイルが見つかりません"
        continue
    }

    # ハッシュ検証
    if (!$SkipHashCheck -and $pkg.sha256) {
        Write-Host "    ハッシュ検証中..." -ForegroundColor Gray
        if (!(Test-FileHash $srcFile $pkg.sha256)) {
            Write-Host "    エラー: ハッシュ不一致！" -ForegroundColor Red
            Write-Host "    期待値: $($pkg.sha256)" -ForegroundColor Gray
            $actual = (Get-FileHash $srcFile -Algorithm SHA256).Hash
            Write-Host "    実際値: $actual" -ForegroundColor Gray
            $errors += "$($pkg.name): ハッシュ値が一致しません（ファイル改ざんの可能性）"
            continue
        }
        Write-Host "    ハッシュOK" -ForegroundColor Green
    }

    # 既存チェック
    if ((Test-Path $destDir) -and !$Force) {
        Write-Host "    スキップ: インストール済み" -ForegroundColor Gray
        $skipped += $pkg.name

        # 既存インストールのパス取得
        $installPath = (Get-ChildItem $destDir -Directory -ErrorAction SilentlyContinue | Select-Object -First 1).FullName
        if (!$installPath) { $installPath = $destDir }

        $pathToAdd = Add-ToPath $pkg $installPath
        if ($pathToAdd) { $pathsToAdd += $pathToAdd }
        continue
    }

    # インストール
    Write-Host "    インストール中..." -ForegroundColor Gray

    # 既存削除
    if (Test-Path $destDir) {
        Remove-Item $destDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null

    try {
        $installPath = Install-Package $pkg $srcFile $destDir

        # インストールパスが取得できない場合
        if (!$installPath) { $installPath = $destDir }

        # 環境変数設定
        Set-EnvironmentVariables $pkg $installPath

        # PATH追加用
        $pathToAdd = Add-ToPath $pkg $installPath
        if ($pathToAdd) { $pathsToAdd += $pathToAdd }

        # post_install実行
        if ($pkg.post_install) {
            Write-Host "    後処理: $($pkg.post_install)" -ForegroundColor Gray
            try {
                Invoke-Expression $pkg.post_install
            }
            catch {
                Write-Host "    後処理エラー: $_" -ForegroundColor Yellow
            }
        }

        $installed += [PSCustomObject]@{
            Name = $pkg.name
            Version = $pkg.version
            Path = $installPath
            EnvVar = $pkg.env_var
        }

        Write-Host "    完了" -ForegroundColor Green
    }
    catch {
        Write-Host "    エラー: $_" -ForegroundColor Red
        $errors += "$($pkg.name): $_"
    }
}

# PATH設定
Write-Host ""
Write-Host "PATH設定中..." -ForegroundColor Yellow

$currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
$addedPaths = @()

foreach ($p in $pathsToAdd) {
    if ($p -and ($currentPath -notlike "*$p*")) {
        $currentPath = "$p;$currentPath"
        $addedPaths += $p
        Write-Host "  追加: $p" -ForegroundColor Gray
    }
}

[Environment]::SetEnvironmentVariable("PATH", $currentPath, "User")

# インストール情報保存
$installedJsonPath = Join-Path $Dest "installed.json"
@{
    installed_at = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    source = $Source
    packages = $installed
} | ConvertTo-Json -Depth 10 | Set-Content $installedJsonPath

# ========== 結果表示 ==========

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "          セットアップ完了" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($installed.Count -gt 0) {
    Write-Host "インストール済み ($($installed.Count)):" -ForegroundColor Green
    foreach ($item in $installed) {
        Write-Host "  [OK] $($item.Name) v$($item.Version)" -ForegroundColor Green
        if ($item.EnvVar) {
            Write-Host "       $($item.EnvVar) = $($item.Path)" -ForegroundColor Gray
        }
    }
}

if ($skipped.Count -gt 0) {
    Write-Host ""
    Write-Host "スキップ ($($skipped.Count)):" -ForegroundColor Gray
    foreach ($name in $skipped) {
        Write-Host "  [--] $name (既存)" -ForegroundColor Gray
    }
}

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "エラー ($($errors.Count)):" -ForegroundColor Red
    foreach ($e in $errors) {
        Write-Host "  [NG] $e" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "----------------------------------------"
Write-Host "ターミナルを再起動して確認してください:"
Write-Host "  java -version"
Write-Host "  gradle -v"
Write-Host "  node -v"
Write-Host "  git --version"
Write-Host "----------------------------------------"
```

---

### get-hashes.ps1（ハッシュ値取得スクリプト）

ダウンロードしたファイルのハッシュ値を取得してCSVに記載するためのスクリプトです。

```powershell
<#
.SYNOPSIS
    パッケージファイルのSHA256ハッシュ値を取得

.PARAMETER PackagesDir
    パッケージディレクトリ

.PARAMETER OutputFormat
    出力形式（csv / table）

.EXAMPLE
    .\get-hashes.ps1 -PackagesDir "\\fileserver\dev-tools\packages"
#>

param(
    [string]$PackagesDir = ".\packages",
    [ValidateSet("csv", "table")]
    [string]$OutputFormat = "table"
)

Write-Host "=== ハッシュ値取得 ===" -ForegroundColor Cyan
Write-Host "対象: $PackagesDir"
Write-Host ""

$results = @()

Get-ChildItem $PackagesDir -Recurse -File | ForEach-Object {
    $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash

    $relativePath = $_.FullName.Replace("$PackagesDir\", "")
    $packageName = $relativePath.Split("\")[0]

    $results += [PSCustomObject]@{
        Package = $packageName
        FileName = $_.Name
        SHA256 = $hash
        Size = "{0:N2} MB" -f ($_.Length / 1MB)
    }
}

if ($OutputFormat -eq "csv") {
    $results | ForEach-Object {
        Write-Host "$($_.FileName),$($_.SHA256)"
    }
}
else {
    $results | Format-Table -AutoSize
}
```

**使用例:**

```powershell
# テーブル形式で表示
.\get-hashes.ps1 -PackagesDir "\\fileserver\dev-tools\packages"

# CSV形式で出力（packages.csvに貼り付け用）
.\get-hashes.ps1 -PackagesDir "\\fileserver\dev-tools\packages" -OutputFormat csv
```

---

### check-versions.ps1（バージョン確認スクリプト）

ローカルと共有フォルダのバージョンを比較して更新があるか確認します。

```powershell
<#
.SYNOPSIS
    ローカルと共有フォルダのバージョンを比較

.EXAMPLE
    .\check-versions.ps1 -Source "\\fileserver\dev-tools"
#>

param(
    [string]$Source = "\\fileserver\dev-tools",
    [string]$LocalInstallDir = "C:\dev-tools"
)

Write-Host "=== バージョン確認 ===" -ForegroundColor Cyan
Write-Host ""

# ローカルのインストール情報
$localJsonPath = Join-Path $LocalInstallDir "installed.json"
if (Test-Path $localJsonPath) {
    $localInfo = Get-Content $localJsonPath | ConvertFrom-Json
    $localPackages = @{}
    foreach ($pkg in $localInfo.packages) {
        $localPackages[$pkg.Name] = $pkg.Version
    }
    Write-Host "ローカル最終更新: $($localInfo.installed_at)" -ForegroundColor Gray
}
else {
    $localPackages = @{}
    Write-Host "ローカル: 未インストール" -ForegroundColor Yellow
}

# 共有フォルダのCSV
$remoteCsv = Import-Csv (Join-Path $Source "packages.csv")

Write-Host ""
Write-Host "パッケージ比較:"
Write-Host "----------------------------------------"

$hasUpdates = $false

foreach ($remote in $remoteCsv) {
    $localVer = $localPackages[$remote.name]
    $remoteVer = $remote.version

    if (!$localVer) {
        Write-Host "  $($remote.name): 未インストール → v$remoteVer" -ForegroundColor Yellow
        $hasUpdates = $true
    }
    elseif ($localVer -ne $remoteVer) {
        Write-Host "  $($remote.name): v$localVer → v$remoteVer (更新あり)" -ForegroundColor Cyan
        $hasUpdates = $true
    }
    else {
        Write-Host "  $($remote.name): v$localVer (最新)" -ForegroundColor Gray
    }
}

Write-Host "----------------------------------------"
Write-Host ""

if ($hasUpdates) {
    Write-Host "更新を適用するには以下を実行:" -ForegroundColor Yellow
    Write-Host "  .\setup-dev-env-v2.ps1 -Source `"$Source`" -Force"
}
else {
    Write-Host "すべて最新です" -ForegroundColor Green
}
```

---

### 共有フォルダ構成（拡張版）

```
\\fileserver\dev-tools\
├── packages.csv                      ← パッケージ定義（ハッシュ含む）
├── packages\
│   ├── java\
│   │   └── OpenJDK11U-jdk_x64_windows_hotspot_11.0.21_9.zip
│   ├── gradle\
│   │   └── gradle-7.6.1-bin.zip
│   ├── node\
│   │   └── node-v18.19.0-win-x64.zip
│   ├── git\
│   │   └── PortableGit-2.43.0-64-bit.7z.exe
│   └── maven\
│       └── apache-maven-3.9.6-bin.zip
├── scripts\
│   ├── download-packages.ps1         ← ダウンロード（オンライン）
│   ├── setup-dev-env-v2.ps1          ← セットアップ（オフライン）
│   ├── get-hashes.ps1                ← ハッシュ値取得
│   ├── check-versions.ps1            ← バージョン確認
│   └── uninstall-dev-env.ps1         ← アンインストール
└── README.md
```

---

### 運用フロー（拡張版）

#### 初回構築（管理者）

```powershell
# 1. packages.csv作成（バージョン・URL記載）

# 2. ダウンロード
.\download-packages.ps1 -OutputDir "\\fileserver\dev-tools\packages"

# 3. ハッシュ値取得
.\get-hashes.ps1 -PackagesDir "\\fileserver\dev-tools\packages" -OutputFormat csv

# 4. packages.csv にハッシュ値を記載
```

#### 開発者セットアップ

```powershell
# セットアップ実行
\\fileserver\dev-tools\scripts\setup-dev-env-v2.ps1
```

#### バージョン更新確認

```powershell
# 更新があるか確認
.\check-versions.ps1 -Source "\\fileserver\dev-tools"

# 更新適用
.\setup-dev-env-v2.ps1 -Force
```

---

### ハッシュ検証のメリット

| メリット | 説明 |
|----------|------|
| 改ざん検知 | ファイルが改変されていないことを確認 |
| 破損検知 | ダウンロード・コピー時の破損を検知 |
| バージョン確認 | 正しいバージョンのファイルか確認 |
| 監査対応 | セキュリティ監査要件への対応 |

---

### check-installed.ps1（インストール状況確認スクリプト）

ローカル環境にツールがインストール済みか、**期待するバージョンと一致しているか**を確認します。

```powershell
<#
.SYNOPSIS
    インストール済みツールの確認（バージョン不一致検知対応）

.DESCRIPTION
    以下を確認します:
    - installed.json の記録
    - 実際のファイル存在
    - 環境変数の設定状況
    - コマンドの実行可否
    - 期待バージョンとの一致（packages.csv と比較）

.PARAMETER LocalInstallDir
    インストール先ディレクトリ

.PARAMETER Source
    共有フォルダのパス（packages.csv の場所）

.PARAMETER Detailed
    詳細情報を表示

.EXAMPLE
    .\check-installed.ps1
    .\check-installed.ps1 -Source "\\fileserver\dev-tools"
    .\check-installed.ps1 -Detailed
#>

param(
    [string]$LocalInstallDir = "C:\dev-tools",
    [string]$Source = "",
    [switch]$Detailed
)

Write-Host "=== インストール状況確認 ===" -ForegroundColor Cyan
Write-Host "対象: $LocalInstallDir"
Write-Host ""

# ========== 期待バージョン読み込み ==========

$expectedVersions = @{}

# 1. 共有フォルダの packages.csv から読み込み
if ($Source -and (Test-Path (Join-Path $Source "packages.csv"))) {
    $csvPath = Join-Path $Source "packages.csv"
    Write-Host "期待バージョン: $csvPath" -ForegroundColor Gray
    Import-Csv $csvPath | ForEach-Object {
        $expectedVersions[$_.name.ToLower()] = $_.version
    }
}
# 2. installed.json から読み込み（フォールバック）
elseif (Test-Path (Join-Path $LocalInstallDir "installed.json")) {
    $installedJson = Get-Content (Join-Path $LocalInstallDir "installed.json") | ConvertFrom-Json
    Write-Host "期待バージョン: installed.json" -ForegroundColor Gray
    foreach ($pkg in $installedJson.packages) {
        $expectedVersions[$pkg.Name.ToLower()] = $pkg.Version
    }
}
else {
    Write-Host "期待バージョン: なし（存在確認のみ）" -ForegroundColor Yellow
}

Write-Host ""

# ========== installed.json からの情報 ==========

$installedJsonPath = Join-Path $LocalInstallDir "installed.json"

if (Test-Path $installedJsonPath) {
    $installedInfo = Get-Content $installedJsonPath | ConvertFrom-Json
    Write-Host "最終セットアップ: $($installedInfo.installed_at)" -ForegroundColor Gray
    Write-Host "ソース: $($installedInfo.source)" -ForegroundColor Gray
    Write-Host ""
}
else {
    Write-Host "installed.json が見つかりません" -ForegroundColor Yellow
    Write-Host "セットアップスクリプトが未実行の可能性があります" -ForegroundColor Yellow
    Write-Host ""
}

# ========== ツール別確認 ==========

$tools = @(
    @{
        Name = "java"
        DisplayName = "Java"
        EnvVar = "JAVA_HOME"
        Command = "java"
        VersionArg = "-version"
        VersionPattern = 'version "([^"]+)"'
    },
    @{
        Name = "gradle"
        DisplayName = "Gradle"
        EnvVar = "GRADLE_HOME"
        Command = "gradle"
        VersionArg = "-v"
        VersionPattern = "Gradle (\d+\.\d+\.?\d*)"
    },
    @{
        Name = "node"
        DisplayName = "Node.js"
        EnvVar = "NODE_HOME"
        Command = "node"
        VersionArg = "-v"
        VersionPattern = "v?(\d+\.\d+\.\d+)"
    },
    @{
        Name = "npm"
        DisplayName = "npm"
        EnvVar = $null
        Command = "npm"
        VersionArg = "-v"
        VersionPattern = "(\d+\.\d+\.\d+)"
    },
    @{
        Name = "git"
        DisplayName = "Git"
        EnvVar = $null
        Command = "git"
        VersionArg = "--version"
        VersionPattern = "git version (\d+\.\d+\.\d+)"
    },
    @{
        Name = "maven"
        DisplayName = "Maven"
        EnvVar = "MAVEN_HOME"
        Command = "mvn"
        VersionArg = "-v"
        VersionPattern = "Apache Maven (\d+\.\d+\.\d+)"
    }
)

Write-Host "-----------------------------------------------------------"
Write-Host "ツール           状態      実際Ver      期待Ver    判定"
Write-Host "-----------------------------------------------------------"

$results = @()

foreach ($tool in $tools) {
    $status = @{
        Name = $tool.DisplayName
        ToolKey = $tool.Name
        Installed = $false
        Version = "-"
        ExpectedVersion = $expectedVersions[$tool.Name]
        VersionMatch = $false
        EnvVarSet = $false
        EnvVarValue = ""
        CommandFound = $false
        CommandPath = ""
    }

    # 環境変数チェック
    if ($tool.EnvVar) {
        $envValue = [Environment]::GetEnvironmentVariable($tool.EnvVar, "User")
        if ($envValue) {
            $status.EnvVarSet = $true
            $status.EnvVarValue = $envValue
        }
    }

    # コマンド実行チェック
    try {
        $cmdPath = (Get-Command $tool.Command -ErrorAction SilentlyContinue).Source
        if ($cmdPath) {
            $status.CommandFound = $true
            $status.CommandPath = $cmdPath

            # バージョン取得
            $versionOutput = & $tool.Command $tool.VersionArg 2>&1 | Out-String
            if ($versionOutput -match $tool.VersionPattern) {
                $status.Version = $Matches[1]
                $status.Installed = $true

                # バージョン比較
                if ($status.ExpectedVersion) {
                    # バージョン文字列の正規化（先頭の v を除去等）
                    $actualNorm = $status.Version -replace "^v", ""
                    $expectedNorm = $status.ExpectedVersion -replace "^v", ""

                    # 部分一致でOKとする（11.0.21 が 11.0.21+9 に含まれる等）
                    if ($actualNorm -like "*$expectedNorm*" -or $expectedNorm -like "*$actualNorm*") {
                        $status.VersionMatch = $true
                    }
                }
                else {
                    # 期待バージョンが指定されていない場合はOK
                    $status.VersionMatch = $true
                }
            }
        }
    }
    catch {
        # コマンドが見つからない
    }

    # 結果表示
    if (!$status.Installed) {
        $statusIcon = "[--]"
        $statusColor = "Gray"
        $verdict = ""
    }
    elseif ($status.VersionMatch) {
        $statusIcon = "[OK]"
        $statusColor = "Green"
        $verdict = "OK"
    }
    else {
        $statusIcon = "[!!]"
        $statusColor = "Yellow"
        $verdict = "不一致"
    }

    $displayName = $tool.DisplayName.PadRight(16)
    $displayStatus = $statusIcon.PadRight(10)
    $displayActual = $status.Version.PadRight(12)
    $displayExpected = if ($status.ExpectedVersion) { $status.ExpectedVersion.PadRight(10) } else { "-".PadRight(10) }

    Write-Host "  $displayName $displayStatus $displayActual $displayExpected $verdict" -ForegroundColor $statusColor

    $results += $status
}

Write-Host "-----------------------------------------------------------"
Write-Host ""

# ========== 詳細表示 ==========

if ($Detailed) {
    Write-Host "=== 詳細情報 ===" -ForegroundColor Cyan
    Write-Host ""

    foreach ($result in $results) {
        Write-Host "[$($result.Name)]" -ForegroundColor Yellow

        if ($result.EnvVarSet) {
            Write-Host "  環境変数: $($result.EnvVarValue)" -ForegroundColor Gray
        }

        if ($result.CommandFound) {
            Write-Host "  コマンド: $($result.CommandPath)" -ForegroundColor Gray
            Write-Host "  実際バージョン: $($result.Version)" -ForegroundColor Gray
            if ($result.ExpectedVersion) {
                Write-Host "  期待バージョン: $($result.ExpectedVersion)" -ForegroundColor Gray
                if ($result.VersionMatch) {
                    Write-Host "  判定: OK" -ForegroundColor Green
                }
                else {
                    Write-Host "  判定: バージョン不一致！" -ForegroundColor Red
                }
            }
        }
        else {
            Write-Host "  コマンドが見つかりません" -ForegroundColor Red
        }

        Write-Host ""
    }
}

# ========== サマリー ==========

$installedCount = ($results | Where-Object { $_.Installed }).Count
$matchCount = ($results | Where-Object { $_.Installed -and $_.VersionMatch }).Count
$mismatchCount = ($results | Where-Object { $_.Installed -and !$_.VersionMatch }).Count
$notInstalledCount = ($results | Where-Object { !$_.Installed }).Count
$totalCount = $results.Count

Write-Host "サマリー:" -ForegroundColor Cyan
Write-Host "  インストール済み: $installedCount / $totalCount"

if ($mismatchCount -gt 0) {
    Write-Host "  バージョン一致:   $matchCount" -ForegroundColor Green
    Write-Host "  バージョン不一致: $mismatchCount" -ForegroundColor Yellow
}

if ($notInstalledCount -gt 0) {
    Write-Host "  未インストール:   $notInstalledCount" -ForegroundColor Gray
}

# 問題がある場合のアドバイス
if ($mismatchCount -gt 0 -or $notInstalledCount -gt 0) {
    Write-Host ""
    Write-Host "問題を解決するには:" -ForegroundColor Yellow

    if ($mismatchCount -gt 0) {
        Write-Host "  バージョン更新: .\setup-dev-env-v2.ps1 -Force" -ForegroundColor Yellow
    }

    if ($notInstalledCount -gt 0) {
        Write-Host "  新規インストール: .\setup-dev-env-v2.ps1" -ForegroundColor Yellow
    }
}
else {
    Write-Host ""
    Write-Host "すべて正常です" -ForegroundColor Green
}
```

**使用例:**

```powershell
# 簡易確認（installed.json と比較）
.\check-installed.ps1

# 共有フォルダのCSVと比較（推奨）
.\check-installed.ps1 -Source "\\fileserver\dev-tools"

# 出力例:
# === インストール状況確認 ===
# 対象: C:\dev-tools
#
# 期待バージョン: \\fileserver\dev-tools\packages.csv
#
# 最終セットアップ: 2024-01-15 10:30:00
# ソース: \\fileserver\dev-tools
#
# -----------------------------------------------------------
# ツール           状態      実際Ver      期待Ver    判定
# -----------------------------------------------------------
#   Java             [OK]      11.0.21      11.0.21    OK
#   Gradle           [!!]      7.5.1        7.6.1      不一致
#   Node.js          [OK]      18.19.0      18.19.0    OK
#   npm              [OK]      10.2.3       -          OK
#   Git              [OK]      2.43.0       2.43.0     OK
#   Maven            [--]      -            3.9.6
# -----------------------------------------------------------
#
# サマリー:
#   インストール済み: 5 / 6
#   バージョン一致:   4
#   バージョン不一致: 1
#   未インストール:   1
#
# 問題を解決するには:
#   バージョン更新: .\setup-dev-env-v2.ps1 -Force
#   新規インストール: .\setup-dev-env-v2.ps1

# 詳細確認（パス・環境変数も表示）
.\check-installed.ps1 -Source "\\fileserver\dev-tools" -Detailed
```

---

### 検知できる状態

| 状態 | アイコン | 色 | 説明 |
|------|----------|-----|------|
| 正常 | `[OK]` | 緑 | インストール済み、バージョン一致 |
| バージョン不一致 | `[!!]` | 黄 | インストール済みだが期待と異なるバージョン |
| 未インストール | `[--]` | グレー | コマンドが見つからない |

---

### クイックチェック（ワンライナー）

簡易的に確認したい場合:

```powershell
# 各ツールのバージョン確認
java -version; gradle -v; node -v; git --version; mvn -v

# 環境変数確認
echo "JAVA_HOME: $env:JAVA_HOME"
echo "GRADLE_HOME: $env:GRADLE_HOME"
echo "NODE_HOME: $env:NODE_HOME"
echo "MAVEN_HOME: $env:MAVEN_HOME"

# PATHに含まれているか確認
$env:PATH -split ";" | Where-Object { $_ -like "*dev-tools*" }
```

---

### インストール状況の確認フロー

```
check-installed.ps1 実行
        │
        ├─ 期待バージョン読み込み
        │   ├─ -Source 指定時: packages.csv
        │   └─ 未指定時: installed.json
        │
        ├─ installed.json 確認
        │   └─ 最終セットアップ日時
        │
        ├─ 各ツールの確認
        │   ├─ 環境変数が設定されているか
        │   ├─ コマンドが実行可能か
        │   ├─ バージョン取得
        │   └─ 期待バージョンと比較 ★
        │
        └─ サマリー表示
            ├─ バージョン一致数
            ├─ バージョン不一致数 ★
            └─ 未インストール数
```

---

## ツール設定管理

ツール本体だけでなく、各ツールの設定ファイルも一元管理します。

### configs.csv（設定ファイル定義）

```csv
tool,config_name,source,destination,action,backup,description
eclipse,formatter,configs/eclipse/formatter.xml,%ECLIPSE_HOME%/formatter.xml,copy,true,コードフォーマッター
eclipse,workspace_settings,configs/eclipse/workspace.zip,%USERPROFILE%/workspace/.metadata,extract,true,ワークスペース設定
eclipse,plugins,configs/eclipse/plugins,%ECLIPSE_HOME%/dropins,copy_folder,false,オフラインプラグイン
eclipse,ini_memory,configs/eclipse/eclipse.ini.patch,%ECLIPSE_HOME%/eclipse.ini,patch,true,メモリ設定
sqldeveloper,connections,configs/sqldeveloper/connections.json,%APPDATA%/SQL Developer/system*/o.jdeveloper.db.connection/connections.json,copy,true,DB接続情報
sqldeveloper,settings,configs/sqldeveloper/ide.properties,%APPDATA%/SQL Developer/system*/o.sqldeveloper/ide.properties,copy,true,IDE設定
git,gitconfig,configs/git/.gitconfig,%USERPROFILE%/.gitconfig,copy,true,Git設定
git,gitignore_global,configs/git/.gitignore_global,%USERPROFILE%/.gitignore_global,copy,false,グローバル.gitignore
vscode,settings,configs/vscode/settings.json,%APPDATA%/Code/User/settings.json,merge,true,VSCode設定
vscode,extensions,configs/vscode/extensions,%USERPROFILE%/.vscode/extensions,copy_folder,false,VSCode拡張
gradle,init_script,configs/gradle/init.gradle,%USERPROFILE%/.gradle/init.gradle,copy,true,Gradle初期化スクリプト
maven,settings,configs/maven/settings.xml,%USERPROFILE%/.m2/settings.xml,copy,true,Maven設定
```

### 列の説明

| 列名 | 説明 | 値の例 |
|------|------|--------|
| tool | 対象ツール名 | eclipse, sqldeveloper, git |
| config_name | 設定の識別名 | formatter, connections |
| source | 共有フォルダ内のパス | configs/eclipse/formatter.xml |
| destination | 配置先（環境変数展開対応） | %ECLIPSE_HOME%/formatter.xml |
| action | 適用方法 | copy, copy_folder, extract, patch, merge |
| backup | 既存ファイルをバックアップ | true / false |
| description | 説明 | コードフォーマッター |

### action の種類

| action | 説明 | 用途 |
|--------|------|------|
| copy | ファイルをコピー | 設定ファイル単体 |
| copy_folder | フォルダごとコピー | プラグイン、拡張機能 |
| extract | ZIPを展開 | workspace設定など |
| patch | 既存ファイルに追記/置換 | eclipse.ini のメモリ設定 |
| merge | JSONをマージ | 既存設定を残しつつ追加 |

---

### 共有フォルダ構成（設定管理追加版）

```
\\fileserver\dev-tools\
├── packages.csv                      ← ツール本体定義
├── configs.csv                       ← 設定ファイル定義 ★
├── packages\
│   ├── java\
│   ├── eclipse\
│   ├── sqldeveloper\
│   └── ...
├── configs\                           ← 設定ファイル ★
│   ├── eclipse\
│   │   ├── formatter.xml             ← コードフォーマッター
│   │   ├── workspace.zip             ← workspace設定テンプレート
│   │   ├── plugins\                  ← オフラインプラグイン
│   │   │   ├── lombok.jar
│   │   │   └── checkstyle-plugin.jar
│   │   └── eclipse.ini.patch         ← メモリ設定パッチ
│   ├── sqldeveloper\
│   │   ├── connections.json          ← DB接続情報テンプレート
│   │   └── ide.properties            ← IDE設定
│   ├── git\
│   │   ├── .gitconfig                ← Git設定
│   │   └── .gitignore_global         ← グローバルignore
│   ├── vscode\
│   │   ├── settings.json             ← VSCode設定
│   │   └── extensions\               ← VSCode拡張（.vsix）
│   ├── gradle\
│   │   └── init.gradle               ← 社内リポジトリ設定等
│   └── maven\
│       └── settings.xml              ← 社内リポジトリ設定
└── scripts\
    ├── setup-dev-env-v2.ps1          ← ツールセットアップ
    ├── apply-configs.ps1             ← 設定適用 ★
    ├── uninstall-dev-env.ps1         ← アンインストール ★
    ├── check-installed.ps1
    └── check-configs.ps1             ← 設定状況確認 ★
```

---

### apply-configs.ps1（設定適用スクリプト）

```powershell
<#
.SYNOPSIS
    ツール設定ファイルの適用

.PARAMETER Source
    共有フォルダのパス

.PARAMETER Tool
    特定ツールのみ適用（省略時は全ツール）

.PARAMETER Force
    既存設定を上書き

.PARAMETER BackupDir
    バックアップ先ディレクトリ

.EXAMPLE
    .\apply-configs.ps1 -Source "\\fileserver\dev-tools"
    .\apply-configs.ps1 -Source "\\fileserver\dev-tools" -Tool eclipse
    .\apply-configs.ps1 -Force
#>

param(
    [string]$Source = "\\fileserver\dev-tools",
    [string]$Tool = "",
    [switch]$Force,
    [string]$BackupDir = "$env:USERPROFILE\.config-backup"
)

$ErrorActionPreference = "Stop"

# ========== 関数定義 ==========

function Expand-EnvVariables {
    param([string]$Path)

    # 環境変数を展開
    $expanded = [Environment]::ExpandEnvironmentVariables($Path)

    # カスタム変数も展開
    $expanded = $expanded -replace "%ECLIPSE_HOME%", $env:ECLIPSE_HOME
    $expanded = $expanded -replace "%USERPROFILE%", $env:USERPROFILE
    $expanded = $expanded -replace "%APPDATA%", $env:APPDATA
    $expanded = $expanded -replace "%LOCALAPPDATA%", $env:LOCALAPPDATA

    # ワイルドカード対応（SQL Developerのsystem*など）
    if ($expanded -like "*`**") {
        $parentDir = Split-Path $expanded -Parent
        $pattern = Split-Path $expanded -Leaf
        if (Test-Path $parentDir) {
            $match = Get-ChildItem $parentDir -Directory | Where-Object { $_.Name -like $pattern.Replace("*", "*") } | Select-Object -First 1
            if ($match) {
                $expanded = $expanded -replace [regex]::Escape((Split-Path $expanded -Parent)), $match.FullName
            }
        }
    }

    return $expanded
}

function Backup-File {
    param([string]$FilePath, [string]$BackupRoot)

    if (!(Test-Path $FilePath)) { return }

    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $relativePath = $FilePath -replace "^[A-Z]:\\", ""
    $backupPath = Join-Path $BackupRoot "$timestamp\$relativePath"

    $backupDir = Split-Path $backupPath -Parent
    New-Item -ItemType Directory -Path $backupDir -Force | Out-Null

    Copy-Item $FilePath $backupPath -Force
    Write-Host "    バックアップ: $backupPath" -ForegroundColor Gray
}

function Apply-Config {
    param($Config, $SourceRoot, $BackupRoot)

    $srcPath = Join-Path $SourceRoot $Config.source
    $destPath = Expand-EnvVariables $Config.destination

    # ソース存在確認
    if (!(Test-Path $srcPath)) {
        Write-Host "    スキップ: ソースなし ($($Config.source))" -ForegroundColor Yellow
        return $false
    }

    # 配置先ディレクトリ作成
    $destDir = Split-Path $destPath -Parent
    if (!(Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }

    # バックアップ
    if ($Config.backup -eq "true" -and (Test-Path $destPath)) {
        Backup-File $destPath $BackupRoot
    }

    # アクション実行
    switch ($Config.action) {
        "copy" {
            Copy-Item $srcPath $destPath -Force
            Write-Host "    コピー: $destPath" -ForegroundColor Gray
        }
        "copy_folder" {
            if (Test-Path $destPath) {
                Remove-Item $destPath -Recurse -Force
            }
            Copy-Item $srcPath $destPath -Recurse -Force
            Write-Host "    フォルダコピー: $destPath" -ForegroundColor Gray
        }
        "extract" {
            if (Test-Path $destPath) {
                Remove-Item $destPath -Recurse -Force
            }
            Expand-Archive $srcPath -DestinationPath $destPath -Force
            Write-Host "    展開: $destPath" -ForegroundColor Gray
        }
        "patch" {
            # パッチファイルの内容を既存ファイルに追記
            if (Test-Path $destPath) {
                $patchContent = Get-Content $srcPath -Raw
                $existingContent = Get-Content $destPath -Raw

                # 既に含まれていなければ追記
                if ($existingContent -notlike "*$patchContent*") {
                    Add-Content $destPath $patchContent
                    Write-Host "    パッチ適用: $destPath" -ForegroundColor Gray
                }
                else {
                    Write-Host "    パッチ済み: $destPath" -ForegroundColor Gray
                }
            }
            else {
                Copy-Item $srcPath $destPath -Force
                Write-Host "    新規作成: $destPath" -ForegroundColor Gray
            }
        }
        "merge" {
            # JSONマージ
            if (Test-Path $destPath) {
                $existing = Get-Content $destPath -Raw | ConvertFrom-Json -AsHashtable
                $new = Get-Content $srcPath -Raw | ConvertFrom-Json -AsHashtable

                foreach ($key in $new.Keys) {
                    $existing[$key] = $new[$key]
                }

                $existing | ConvertTo-Json -Depth 10 | Set-Content $destPath
                Write-Host "    マージ: $destPath" -ForegroundColor Gray
            }
            else {
                Copy-Item $srcPath $destPath -Force
                Write-Host "    新規作成: $destPath" -ForegroundColor Gray
            }
        }
        default {
            Write-Host "    未対応アクション: $($Config.action)" -ForegroundColor Red
            return $false
        }
    }

    return $true
}

# ========== メイン処理 ==========

Write-Host "=== 設定ファイル適用 ===" -ForegroundColor Cyan
Write-Host "Source: $Source"
Write-Host "BackupDir: $BackupDir"
if ($Tool) {
    Write-Host "対象ツール: $Tool"
}
Write-Host ""

# CSV読み込み
$csvPath = Join-Path $Source "configs.csv"
if (!(Test-Path $csvPath)) {
    Write-Host "エラー: configs.csv が見つかりません: $csvPath" -ForegroundColor Red
    exit 1
}

$configs = Import-Csv $csvPath

# ツールフィルタ
if ($Tool) {
    $configs = $configs | Where-Object { $_.tool -eq $Tool }
}

# ツール別にグループ化
$grouped = $configs | Group-Object tool

$applied = @()
$skipped = @()
$errors = @()

foreach ($group in $grouped) {
    Write-Host "[$($group.Name)]" -ForegroundColor Yellow

    foreach ($config in $group.Group) {
        Write-Host "  $($config.config_name): $($config.description)"

        try {
            $result = Apply-Config $config $Source $BackupDir
            if ($result) {
                $applied += "$($group.Name)/$($config.config_name)"
            }
            else {
                $skipped += "$($group.Name)/$($config.config_name)"
            }
        }
        catch {
            Write-Host "    エラー: $_" -ForegroundColor Red
            $errors += "$($group.Name)/$($config.config_name): $_"
        }
    }
    Write-Host ""
}

# ========== 結果表示 ==========

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "          設定適用完了" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "適用: $($applied.Count) / スキップ: $($skipped.Count) / エラー: $($errors.Count)"

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "エラー詳細:" -ForegroundColor Red
    foreach ($e in $errors) {
        Write-Host "  $e" -ForegroundColor Red
    }
}
```

---

### uninstall-dev-env.ps1（アンインストールスクリプト）

```powershell
<#
.SYNOPSIS
    開発環境のアンインストール

.PARAMETER Dest
    インストール先ディレクトリ

.PARAMETER Tool
    特定ツールのみアンインストール（省略時は全ツール）

.PARAMETER KeepConfigs
    設定ファイルを残す

.EXAMPLE
    .\uninstall-dev-env.ps1
    .\uninstall-dev-env.ps1 -Tool gradle
    .\uninstall-dev-env.ps1 -KeepConfigs
#>

param(
    [string]$Dest = "C:\dev-tools",
    [string]$Tool = "",
    [switch]$KeepConfigs,
    [switch]$Confirm
)

Write-Host "=== 開発環境アンインストール ===" -ForegroundColor Cyan
Write-Host "対象: $Dest"
if ($Tool) {
    Write-Host "ツール: $Tool"
}
Write-Host ""

# installed.json 読み込み
$installedJsonPath = Join-Path $Dest "installed.json"
if (!(Test-Path $installedJsonPath)) {
    Write-Host "installed.json が見つかりません" -ForegroundColor Yellow
    Write-Host "手動でインストールされた可能性があります"
    exit 1
}

$installedInfo = Get-Content $installedJsonPath | ConvertFrom-Json

# 対象パッケージ
$packages = $installedInfo.packages
if ($Tool) {
    $packages = $packages | Where-Object { $_.Name -eq $Tool }
}

if ($packages.Count -eq 0) {
    Write-Host "アンインストール対象がありません" -ForegroundColor Yellow
    exit 0
}

# 確認
Write-Host "以下をアンインストールします:" -ForegroundColor Yellow
foreach ($pkg in $packages) {
    Write-Host "  - $($pkg.Name) v$($pkg.Version)" -ForegroundColor Yellow
    Write-Host "    パス: $($pkg.Path)" -ForegroundColor Gray
    if ($pkg.EnvVar) {
        Write-Host "    環境変数: $($pkg.EnvVar)" -ForegroundColor Gray
    }
}
Write-Host ""

if (!$Confirm) {
    $response = Read-Host "続行しますか？ (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "キャンセルしました" -ForegroundColor Gray
        exit 0
    }
}

# アンインストール実行
$uninstalled = @()
$errors = @()

foreach ($pkg in $packages) {
    Write-Host "[$($pkg.Name)]" -ForegroundColor Yellow

    try {
        # 環境変数削除
        if ($pkg.EnvVar) {
            $envVars = $pkg.EnvVar -split ";"
            foreach ($envVar in $envVars) {
                $envVar = $envVar.Trim()
                if ($envVar) {
                    [Environment]::SetEnvironmentVariable($envVar, $null, "User")
                    Write-Host "  環境変数削除: $envVar" -ForegroundColor Gray
                }
            }
        }

        # PATHから削除
        $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
        $pathParts = $currentPath -split ";" | Where-Object { $_ -notlike "*$($pkg.Path)*" }
        $newPath = $pathParts -join ";"
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Host "  PATHから削除" -ForegroundColor Gray

        # フォルダ削除
        $toolDir = Join-Path $Dest $pkg.Name
        if (Test-Path $toolDir) {
            Remove-Item $toolDir -Recurse -Force
            Write-Host "  フォルダ削除: $toolDir" -ForegroundColor Gray
        }

        $uninstalled += $pkg.Name
        Write-Host "  完了" -ForegroundColor Green
    }
    catch {
        Write-Host "  エラー: $_" -ForegroundColor Red
        $errors += "$($pkg.Name): $_"
    }
    Write-Host ""
}

# installed.json 更新
if (!$Tool) {
    # 全削除の場合
    Remove-Item $installedJsonPath -Force
    if ((Get-ChildItem $Dest -Force | Measure-Object).Count -eq 0) {
        Remove-Item $Dest -Force
    }
}
else {
    # 部分削除の場合
    $remainingPackages = $installedInfo.packages | Where-Object { $_.Name -notin $uninstalled }
    $installedInfo.packages = $remainingPackages
    $installedInfo | ConvertTo-Json -Depth 10 | Set-Content $installedJsonPath
}

# 結果表示
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "       アンインストール完了" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "削除: $($uninstalled.Count) / エラー: $($errors.Count)"

if ($errors.Count -gt 0) {
    Write-Host ""
    Write-Host "エラー詳細:" -ForegroundColor Red
    foreach ($e in $errors) {
        Write-Host "  $e" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "ターミナルを再起動してください"
```

---

### 設定ファイルの例

#### configs/eclipse/eclipse.ini.patch

```ini
# メモリ設定
-Xms512m
-Xmx2048m
-XX:+UseG1GC
```

#### configs/eclipse/formatter.xml

```xml
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<profiles version="21">
    <profile kind="CodeFormatterProfile" name="Company Standard" version="21">
        <setting id="org.eclipse.jdt.core.formatter.tabulation.char" value="space"/>
        <setting id="org.eclipse.jdt.core.formatter.tabulation.size" value="4"/>
        <setting id="org.eclipse.jdt.core.formatter.lineSplit" value="120"/>
        <!-- 他の設定 -->
    </profile>
</profiles>
```

#### configs/sqldeveloper/connections.json

```json
{
    "connections": [
        {
            "name": "開発DB",
            "hostname": "dev-db.example.com",
            "port": 1521,
            "sid": "DEVDB",
            "username": "devuser"
        },
        {
            "name": "検証DB",
            "hostname": "stg-db.example.com",
            "port": 1521,
            "sid": "STGDB",
            "username": "stguser"
        }
    ]
}
```

#### configs/git/.gitconfig

```ini
[user]
    name = Your Name
    email = your.name@example.com

[core]
    autocrlf = true
    excludesfile = ~/.gitignore_global

[init]
    defaultBranch = main

[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    lg = log --oneline --graph

[credential]
    helper = manager
```

#### configs/maven/settings.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<settings>
    <mirrors>
        <mirror>
            <id>company-nexus</id>
            <name>Company Nexus Repository</name>
            <url>http://nexus.example.com/repository/maven-public/</url>
            <mirrorOf>*</mirrorOf>
        </mirror>
    </mirrors>

    <proxies>
        <proxy>
            <id>company-proxy</id>
            <active>true</active>
            <protocol>http</protocol>
            <host>proxy.example.com</host>
            <port>8080</port>
        </proxy>
    </proxies>
</settings>
```

---

### 運用フロー（設定管理込み）

```
1. 初回セットアップ（管理者）
   ├─ packages.csv 作成（ツール定義）
   ├─ configs.csv 作成（設定定義）
   ├─ configs/ に設定ファイル配置
   └─ ダウンロード＆ハッシュ取得

2. 開発者セットアップ
   ├─ setup-dev-env-v2.ps1    ← ツールインストール
   └─ apply-configs.ps1       ← 設定適用

3. 設定更新時
   ├─ 管理者: configs/ 内のファイル更新
   └─ 開発者: apply-configs.ps1 -Force

4. バージョン確認
   └─ check-installed.ps1 -Source "\\fileserver\dev-tools"

5. アンインストール
   ├─ uninstall-dev-env.ps1              ← 全削除
   └─ uninstall-dev-env.ps1 -Tool gradle ← 個別削除
```

---

### スクリプト一覧（最終版）

| スクリプト | 用途 |
|------------|------|
| download-packages.ps1 | パッケージダウンロード（オンライン） |
| get-hashes.ps1 | ハッシュ値取得 |
| setup-dev-env-v2.ps1 | ツールインストール |
| apply-configs.ps1 | 設定ファイル適用 |
| check-installed.ps1 | インストール状況確認 |
| check-versions.ps1 | バージョン比較 |
| uninstall-dev-env.ps1 | アンインストール |
