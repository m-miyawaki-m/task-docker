# パッケージ管理ソフト作成用 PowerShell 機能

開発環境セットアップツールを自作する際に必要な機能とコマンドのリファレンス。

## 機能カテゴリ一覧

| カテゴリ | 用途 |
|----------|------|
| [ファイル操作](#1-ファイル操作) | コピー、移動、展開、権限 |
| [JSON/CSV操作](#2-jsoncsv操作) | 設定ファイル読み書き |
| [環境変数](#3-環境変数操作) | PATH、JAVA_HOME 等の設定 |
| [レジストリ](#4-レジストリ操作) | インストール情報確認 |
| [プロセス実行](#5-プロセス実行) | インストーラー実行、コマンド実行 |
| [アーカイブ](#6-アーカイブ操作) | ZIP展開、圧縮 |
| [ハッシュ検証](#7-ハッシュ検証) | ファイル整合性チェック |
| [ログ出力](#8-ログ出力) | 進捗・エラー記録 |
| [ネットワーク](#9-ネットワーク) | ダウンロード（オンライン環境） |
| [バージョン比較](#10-バージョン比較) | バージョン文字列の比較 |

---

## 1. ファイル操作

### 基本操作

```powershell
# ファイル/フォルダ存在確認
Test-Path -Path "C:\dev-tools\jdk-21"
Test-Path -Path "C:\dev-tools\jdk-21" -PathType Container  # フォルダ
Test-Path -Path "C:\dev-tools\jdk-21\bin\java.exe" -PathType Leaf  # ファイル

# フォルダ作成（親ディレクトリも含めて）
New-Item -Path "C:\dev-tools\jdk-21" -ItemType Directory -Force

# ファイルコピー
Copy-Item -Path "source.txt" -Destination "dest.txt" -Force

# フォルダごとコピー（再帰）
Copy-Item -Path "source\*" -Destination "dest\" -Recurse -Force

# 移動
Move-Item -Path "old\file.txt" -Destination "new\file.txt" -Force

# 削除（再帰）
Remove-Item -Path "C:\dev-tools\old-jdk" -Recurse -Force

# ファイル一覧取得
Get-ChildItem -Path "C:\dev-tools" -Recurse -Filter "*.exe"
```

### 高度なコピー操作

```powershell
# 特定パターンのみコピー
Get-ChildItem -Path "source" -Filter "*.jar" |
    Copy-Item -Destination "dest\" -Force

# 除外パターン
Get-ChildItem -Path "source" -Recurse -Exclude "*.log", "*.tmp" |
    Copy-Item -Destination "dest\" -Force

# ミラーリング（robocopy相当）
function Copy-Mirror {
    param([string]$Source, [string]$Destination)
    robocopy $Source $Destination /MIR /R:3 /W:5 /NP
}
```

### ファイル属性・権限

```powershell
# 読み取り専用解除
Set-ItemProperty -Path "file.txt" -Name IsReadOnly -Value $false

# 属性取得
(Get-Item "file.txt").Attributes

# ACL取得
Get-Acl -Path "C:\dev-tools"

# ACL設定（管理者向け）
$acl = Get-Acl -Path "C:\dev-tools"
$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "Users", "FullControl", "ContainerInherit,ObjectInherit", "None", "Allow"
)
$acl.SetAccessRule($rule)
Set-Acl -Path "C:\dev-tools" -AclObject $acl
```

---

## 2. JSON/CSV操作

### JSON読み書き

```powershell
# JSON読み込み
$config = Get-Content -Path "packages.json" -Raw | ConvertFrom-Json

# プロパティアクセス
$config.packages | ForEach-Object {
    Write-Host "$($_.name): $($_.version)"
}

# JSON書き込み
$data = @{
    name = "jdk"
    version = "21.0.2"
    installed = $true
    timestamp = (Get-Date -Format "yyyy-MM-dd HH:mm:ss")
}
$data | ConvertTo-Json -Depth 10 | Set-Content -Path "installed.json" -Encoding UTF8

# 配列のJSON
$packages = @(
    @{ name = "jdk"; version = "21.0.2" },
    @{ name = "maven"; version = "3.9.6" }
)
$packages | ConvertTo-Json -Depth 10 | Set-Content -Path "packages.json" -Encoding UTF8
```

### JSONマージ

```powershell
function Merge-Json {
    param (
        [string]$BasePath,
        [string]$OverridePath,
        [string]$OutputPath
    )

    $base = Get-Content -Path $BasePath -Raw | ConvertFrom-Json
    $override = Get-Content -Path $OverridePath -Raw | ConvertFrom-Json

    # プロパティをマージ
    foreach ($prop in $override.PSObject.Properties) {
        $base | Add-Member -NotePropertyName $prop.Name -NotePropertyValue $prop.Value -Force
    }

    $base | ConvertTo-Json -Depth 10 | Set-Content -Path $OutputPath -Encoding UTF8
}
```

### CSV読み書き

```powershell
# CSV読み込み
$packages = Import-Csv -Path "packages.csv" -Encoding UTF8

# 各行処理
$packages | ForEach-Object {
    Write-Host "Name: $($_.name), Version: $($_.version)"
}

# CSV書き込み
$data = @(
    [PSCustomObject]@{ name = "jdk"; version = "21.0.2"; status = "installed" },
    [PSCustomObject]@{ name = "maven"; version = "3.9.6"; status = "pending" }
)
$data | Export-Csv -Path "status.csv" -NoTypeInformation -Encoding UTF8
```

---

## 3. 環境変数操作

### ユーザー環境変数

```powershell
# 取得
$javaHome = [Environment]::GetEnvironmentVariable("JAVA_HOME", "User")

# 設定
[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\dev-tools\jdk-21", "User")

# 削除
[Environment]::SetEnvironmentVariable("JAVA_HOME", $null, "User")
```

### システム環境変数（管理者権限必要）

```powershell
# 取得
$systemPath = [Environment]::GetEnvironmentVariable("PATH", "Machine")

# 設定
[Environment]::SetEnvironmentVariable("MY_VAR", "value", "Machine")
```

### PATH操作

```powershell
# PATH追加（ユーザー）
function Add-ToPath {
    param ([string]$NewPath)

    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")

    if ($currentPath -notlike "*$NewPath*") {
        $newPathValue = "$currentPath;$NewPath"
        [Environment]::SetEnvironmentVariable("PATH", $newPathValue, "User")
        Write-Host "PATHに追加しました: $NewPath"
    } else {
        Write-Host "既にPATHに存在します: $NewPath"
    }
}

# PATH削除
function Remove-FromPath {
    param ([string]$RemovePath)

    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    $paths = $currentPath -split ";" | Where-Object { $_ -ne $RemovePath -and $_ -ne "" }
    $newPathValue = $paths -join ";"
    [Environment]::SetEnvironmentVariable("PATH", $newPathValue, "User")
}

# 現在のセッションにも反映
$env:PATH = [Environment]::GetEnvironmentVariable("PATH", "User") + ";" +
            [Environment]::GetEnvironmentVariable("PATH", "Machine")
```

### 環境変数展開

```powershell
# 環境変数を含むパスを展開
function Expand-EnvPath {
    param ([string]$Path)

    # %VAR% 形式を展開
    $expanded = [Environment]::ExpandEnvironmentVariables($Path)

    # $env:VAR 形式も展開
    $expanded = $ExecutionContext.InvokeCommand.ExpandString($expanded)

    return $expanded
}

# 例
$path = Expand-EnvPath "%USERPROFILE%\.m2\settings.xml"
```

---

## 4. レジストリ操作

### インストール済みソフトウェア確認

```powershell
# 64bit アプリケーション
$uninstall64 = Get-ItemProperty "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue

# 32bit アプリケーション
$uninstall32 = Get-ItemProperty "HKLM:\SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue

# ユーザーインストール
$uninstallUser = Get-ItemProperty "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\*" -ErrorAction SilentlyContinue

# 全て結合
$allInstalled = $uninstall64 + $uninstall32 + $uninstallUser

# 検索
function Find-InstalledSoftware {
    param ([string]$Name)

    $allInstalled | Where-Object { $_.DisplayName -like "*$Name*" } |
        Select-Object DisplayName, DisplayVersion, InstallLocation, Publisher
}

# 例
Find-InstalledSoftware "Java"
```

### レジストリ読み書き

```powershell
# レジストリ読み込み
$value = Get-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Setting1" -ErrorAction SilentlyContinue

# レジストリ書き込み
New-Item -Path "HKCU:\Software\MyApp" -Force
Set-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Setting1" -Value "value1"

# レジストリ削除
Remove-ItemProperty -Path "HKCU:\Software\MyApp" -Name "Setting1" -ErrorAction SilentlyContinue
Remove-Item -Path "HKCU:\Software\MyApp" -Recurse -ErrorAction SilentlyContinue
```

---

## 5. プロセス実行

### 外部コマンド実行

```powershell
# 基本実行
& "C:\path\to\program.exe" -arg1 value1 -arg2 value2

# 戻り値取得
$result = & java -version 2>&1
$exitCode = $LASTEXITCODE

# Start-Process（非同期、別ウィンドウ）
Start-Process -FilePath "notepad.exe" -ArgumentList "file.txt"

# Start-Process（同期、出力取得）
$process = Start-Process -FilePath "cmd.exe" -ArgumentList "/c dir" `
    -Wait -NoNewWindow -PassThru -RedirectStandardOutput "stdout.txt" -RedirectStandardError "stderr.txt"
$process.ExitCode
```

### インストーラー実行

```powershell
# MSIインストール（サイレント）
function Install-Msi {
    param (
        [string]$MsiPath,
        [string]$InstallDir,
        [string]$LogPath = "$env:TEMP\msi_install.log"
    )

    $arguments = @(
        "/i", "`"$MsiPath`""
        "/qn"                          # サイレント
        "/norestart"                   # 再起動しない
        "INSTALLDIR=`"$InstallDir`""
        "/L*v", "`"$LogPath`""         # 詳細ログ
    )

    $process = Start-Process -FilePath "msiexec.exe" -ArgumentList $arguments -Wait -PassThru
    return $process.ExitCode
}

# EXEインストール（サイレント）- 製品により異なる
function Install-Exe {
    param (
        [string]$ExePath,
        [string[]]$Arguments
    )

    $process = Start-Process -FilePath $ExePath -ArgumentList $Arguments -Wait -PassThru
    return $process.ExitCode
}

# 例: NSIS系
Install-Exe -ExePath "setup.exe" -Arguments @("/S", "/D=C:\install\path")

# 例: InstallShield系
Install-Exe -ExePath "setup.exe" -Arguments @("/s", "/v`"/qn INSTALLDIR=C:\path`"")
```

### バージョン取得コマンド実行

```powershell
function Get-ToolVersion {
    param (
        [string]$Command,
        [string[]]$Arguments = @("--version"),
        [string]$Pattern = "(\d+\.\d+[\.\d]*)"
    )

    try {
        $output = & $Command $Arguments 2>&1 | Out-String
        if ($output -match $Pattern) {
            return $Matches[1]
        }
    } catch {
        return $null
    }
    return $null
}

# 例
Get-ToolVersion -Command "java" -Arguments @("-version")
Get-ToolVersion -Command "git" -Arguments @("--version")
Get-ToolVersion -Command "node" -Arguments @("--version") -Pattern "v?(\d+\.\d+\.\d+)"
```

---

## 6. アーカイブ操作

### ZIP展開

```powershell
# PowerShell標準（5.0+）
Expand-Archive -Path "archive.zip" -DestinationPath "C:\extract\" -Force

# .NET直接利用（より細かい制御）
Add-Type -AssemblyName System.IO.Compression.FileSystem

function Expand-ZipFile {
    param (
        [string]$ZipPath,
        [string]$DestinationPath,
        [switch]$Overwrite
    )

    if ($Overwrite -and (Test-Path $DestinationPath)) {
        Remove-Item -Path $DestinationPath -Recurse -Force
    }

    [System.IO.Compression.ZipFile]::ExtractToDirectory($ZipPath, $DestinationPath)
}

# ルートフォルダをスキップして展開
function Expand-ZipSkipRoot {
    param (
        [string]$ZipPath,
        [string]$DestinationPath
    )

    $tempPath = Join-Path $env:TEMP ([System.IO.Path]::GetRandomFileName())
    Expand-Archive -Path $ZipPath -DestinationPath $tempPath -Force

    # ルートフォルダを特定
    $rootItems = Get-ChildItem -Path $tempPath
    if ($rootItems.Count -eq 1 -and $rootItems[0].PSIsContainer) {
        # 単一フォルダの場合、その中身をコピー
        Copy-Item -Path "$($rootItems[0].FullName)\*" -Destination $DestinationPath -Recurse -Force
    } else {
        Copy-Item -Path "$tempPath\*" -Destination $DestinationPath -Recurse -Force
    }

    Remove-Item -Path $tempPath -Recurse -Force
}
```

### 7-Zip利用（より多くの形式対応）

```powershell
function Expand-7Zip {
    param (
        [string]$ArchivePath,
        [string]$DestinationPath,
        [string]$SevenZipPath = "C:\Program Files\7-Zip\7z.exe"
    )

    if (-not (Test-Path $SevenZipPath)) {
        throw "7-Zip が見つかりません: $SevenZipPath"
    }

    $arguments = @("x", "`"$ArchivePath`"", "-o`"$DestinationPath`"", "-y")
    $process = Start-Process -FilePath $SevenZipPath -ArgumentList $arguments -Wait -PassThru -NoNewWindow
    return $process.ExitCode
}
```

### ZIP圧縮

```powershell
# PowerShell標準
Compress-Archive -Path "C:\source\*" -DestinationPath "archive.zip" -Force

# 複数ソース
Compress-Archive -Path "file1.txt", "file2.txt", "folder\" -DestinationPath "archive.zip"
```

---

## 7. ハッシュ検証

```powershell
# ハッシュ計算
$hash = Get-FileHash -Path "file.zip" -Algorithm SHA256
$hash.Hash  # 大文字のハッシュ値

# ハッシュ検証関数
function Test-FileHash {
    param (
        [string]$FilePath,
        [string]$ExpectedHash,
        [string]$Algorithm = "SHA256"
    )

    if (-not (Test-Path $FilePath)) {
        Write-Warning "ファイルが存在しません: $FilePath"
        return $false
    }

    $actualHash = (Get-FileHash -Path $FilePath -Algorithm $Algorithm).Hash

    if ($actualHash -eq $ExpectedHash.ToUpper()) {
        Write-Host "[OK] ハッシュ一致: $FilePath" -ForegroundColor Green
        return $true
    } else {
        Write-Warning "[NG] ハッシュ不一致: $FilePath"
        Write-Warning "  期待値: $ExpectedHash"
        Write-Warning "  実際値: $actualHash"
        return $false
    }
}

# 使用例
if (Test-FileHash -FilePath "jdk-21.zip" -ExpectedHash "abc123...") {
    Expand-Archive -Path "jdk-21.zip" -DestinationPath "C:\dev-tools\jdk-21"
}
```

---

## 8. ログ出力

### ログ関数

```powershell
# グローバル設定
$script:LogPath = "C:\logs\setup.log"

function Write-Log {
    param (
        [string]$Message,
        [ValidateSet("INFO", "WARN", "ERROR", "DEBUG")]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "[$timestamp] [$Level] $Message"

    # コンソール出力
    switch ($Level) {
        "ERROR" { Write-Host $logMessage -ForegroundColor Red }
        "WARN"  { Write-Host $logMessage -ForegroundColor Yellow }
        "DEBUG" { Write-Host $logMessage -ForegroundColor Gray }
        default { Write-Host $logMessage }
    }

    # ファイル出力
    if ($script:LogPath) {
        $logDir = Split-Path -Parent $script:LogPath
        if (-not (Test-Path $logDir)) {
            New-Item -Path $logDir -ItemType Directory -Force | Out-Null
        }
        Add-Content -Path $script:LogPath -Value $logMessage -Encoding UTF8
    }
}

# 使用例
Write-Log "インストール開始: JDK 21" -Level INFO
Write-Log "ファイルが見つかりません" -Level ERROR
```

### 進捗表示

```powershell
# Write-Progress
$packages = @("jdk", "maven", "gradle", "git", "node")
$total = $packages.Count

for ($i = 0; $i -lt $total; $i++) {
    $package = $packages[$i]
    $percentComplete = (($i + 1) / $total) * 100

    Write-Progress -Activity "パッケージインストール中" `
                   -Status "$package をインストール中..." `
                   -PercentComplete $percentComplete `
                   -CurrentOperation "($($i + 1) / $total)"

    # インストール処理...
    Start-Sleep -Seconds 1
}

Write-Progress -Activity "パッケージインストール中" -Completed
```

---

## 9. ネットワーク

### ファイルダウンロード

```powershell
# Invoke-WebRequest（PowerShell標準）
Invoke-WebRequest -Uri "https://example.com/file.zip" -OutFile "file.zip"

# 高速ダウンロード（.NET直接）
function Download-File {
    param (
        [string]$Url,
        [string]$OutputPath,
        [int]$TimeoutSec = 300
    )

    $webClient = New-Object System.Net.WebClient
    try {
        $webClient.DownloadFile($Url, $OutputPath)
        return $true
    } catch {
        Write-Warning "ダウンロード失敗: $_"
        return $false
    } finally {
        $webClient.Dispose()
    }
}

# プロキシ設定付きダウンロード
function Download-FileWithProxy {
    param (
        [string]$Url,
        [string]$OutputPath,
        [string]$ProxyUrl
    )

    $webClient = New-Object System.Net.WebClient

    if ($ProxyUrl) {
        $proxy = New-Object System.Net.WebProxy($ProxyUrl)
        $proxy.UseDefaultCredentials = $true
        $webClient.Proxy = $proxy
    }

    try {
        $webClient.DownloadFile($Url, $OutputPath)
    } finally {
        $webClient.Dispose()
    }
}
```

### 疎通確認

```powershell
# ping相当
Test-Connection -ComputerName "server.example.com" -Count 1 -Quiet

# ポート疎通
Test-NetConnection -ComputerName "server.example.com" -Port 443

# HTTP疎通
function Test-HttpConnection {
    param ([string]$Url)

    try {
        $response = Invoke-WebRequest -Uri $Url -Method Head -TimeoutSec 10 -UseBasicParsing
        return $response.StatusCode -eq 200
    } catch {
        return $false
    }
}
```

---

## 10. バージョン比較

### バージョン文字列比較

```powershell
# [version]型を使用
[version]"1.2.3" -gt [version]"1.2.0"  # True
[version]"2.0" -lt [version]"1.10"     # False（2.0 > 1.10）

# バージョン比較関数
function Compare-Version {
    param (
        [string]$Version1,
        [string]$Version2
    )

    # "v" プレフィックス除去
    $v1 = $Version1 -replace "^v", ""
    $v2 = $Version2 -replace "^v", ""

    try {
        $ver1 = [version]$v1
        $ver2 = [version]$v2

        if ($ver1 -gt $ver2) { return 1 }
        elseif ($ver1 -lt $ver2) { return -1 }
        else { return 0 }
    } catch {
        # バージョン形式でない場合は文字列比較
        return [string]::Compare($v1, $v2)
    }
}

# 使用例
$result = Compare-Version "21.0.2" "17.0.1"
if ($result -gt 0) { "Version1が新しい" }
elseif ($result -lt 0) { "Version2が新しい" }
else { "同じバージョン" }
```

### セマンティックバージョニング対応

```powershell
function Compare-SemVer {
    param (
        [string]$Version1,
        [string]$Version2
    )

    # プレリリースタグを分離 (1.0.0-beta.1)
    $v1Parts = $Version1 -split "-"
    $v2Parts = $Version2 -split "-"

    $v1Main = $v1Parts[0] -replace "^v", ""
    $v2Main = $v2Parts[0] -replace "^v", ""

    # メインバージョン比較
    $mainCompare = Compare-Version $v1Main $v2Main
    if ($mainCompare -ne 0) { return $mainCompare }

    # プレリリースタグ比較
    $v1Pre = if ($v1Parts.Count -gt 1) { $v1Parts[1] } else { $null }
    $v2Pre = if ($v2Parts.Count -gt 1) { $v2Parts[1] } else { $null }

    # プレリリースなし > プレリリースあり
    if ($v1Pre -eq $null -and $v2Pre -ne $null) { return 1 }
    if ($v1Pre -ne $null -and $v2Pre -eq $null) { return -1 }
    if ($v1Pre -eq $null -and $v2Pre -eq $null) { return 0 }

    return [string]::Compare($v1Pre, $v2Pre)
}
```

---

## 参考リンク

### 公式ドキュメント

| トピック | URL |
|----------|-----|
| PowerShell ドキュメント | https://learn.microsoft.com/ja-jp/powershell/ |
| ファイルシステム | https://learn.microsoft.com/ja-jp/powershell/module/microsoft.powershell.management/ |
| 環境変数 | https://learn.microsoft.com/ja-jp/powershell/module/microsoft.powershell.core/about/about_environment_variables |
| レジストリ | https://learn.microsoft.com/ja-jp/powershell/scripting/samples/working-with-registry-entries |
| JSON処理 | https://learn.microsoft.com/ja-jp/powershell/module/microsoft.powershell.utility/convertfrom-json |
| アーカイブ | https://learn.microsoft.com/ja-jp/powershell/module/microsoft.powershell.archive/ |
| Web リクエスト | https://learn.microsoft.com/ja-jp/powershell/module/microsoft.powershell.utility/invoke-webrequest |

### サンプル・チュートリアル

| トピック | URL |
|----------|-----|
| PowerShell スクリプティング | https://learn.microsoft.com/ja-jp/powershell/scripting/learn/ps101/00-introduction |
| エラーハンドリング | https://learn.microsoft.com/ja-jp/powershell/scripting/learn/deep-dives/everything-about-exceptions |
| パラメータ設計 | https://learn.microsoft.com/ja-jp/powershell/module/microsoft.powershell.core/about/about_functions_advanced_parameters |

### 関連ツール

| ツール | 用途 | URL |
|--------|------|-----|
| PSScriptAnalyzer | 静的解析 | https://github.com/PowerShell/PSScriptAnalyzer |
| Pester | テストフレームワーク | https://pester.dev/ |
| platyPS | ヘルプドキュメント生成 | https://github.com/PowerShell/platyPS |
