# PowerShell 概要と基本コマンド

## PowerShell とは

PowerShell は Microsoft が開発したタスク自動化・構成管理フレームワーク。

### 特徴

| 特徴 | 説明 |
|------|------|
| オブジェクト指向 | コマンドの出力がテキストではなく .NET オブジェクト |
| パイプライン | オブジェクトをパイプで連携可能 |
| クロスプラットフォーム | Windows / macOS / Linux 対応（PowerShell 7+） |
| .NET 統合 | .NET Framework / .NET Core のクラス利用可能 |

### バージョン

| バージョン | 状況 | 備考 |
|-----------|------|------|
| Windows PowerShell 5.1 | Windows 標準搭載 | .NET Framework ベース |
| PowerShell 7.x | 最新版 | .NET Core ベース、クロスプラットフォーム |

```powershell
# バージョン確認
$PSVersionTable.PSVersion
```

---

## 基本構文

### 変数

```powershell
# 変数定義
$name = "value"
$number = 123
$array = @(1, 2, 3)
$hash = @{ key1 = "value1"; key2 = "value2" }

# 型指定
[string]$text = "hello"
[int]$count = 10
[bool]$flag = $true
```

### 型システム

PowerShell は .NET の型システムを利用可能。`[型名]` で型を指定する。

#### 基本型（プリミティブ型）

| 型 | 説明 | 例 |
|----|------|-----|
| `[string]` | 文字列 | `[string]$name = "hello"` |
| `[int]` | 32ビット整数 | `[int]$num = 123` |
| `[long]` | 64ビット整数 | `[long]$big = 9999999999` |
| `[double]` | 倍精度浮動小数点 | `[double]$pi = 3.14159` |
| `[decimal]` | 高精度小数 | `[decimal]$price = 99.99` |
| `[bool]` | 真偽値 | `[bool]$flag = $true` |
| `[char]` | 単一文字 | `[char]$c = 'A'` |
| `[byte]` | 0-255 | `[byte]$b = 255` |
| `[array]` | 配列 | `[array]$arr = @(1,2,3)` |
| `[hashtable]` | ハッシュテーブル | `[hashtable]$h = @{}` |

#### .NET クラス型

PowerShell から .NET Framework / .NET Core のクラスを直接利用可能。

```powershell
# System 名前空間は省略可能
[Environment]           # = [System.Environment]
[DateTime]              # = [System.DateTime]
[Math]                  # = [System.Math]
[IO.Path]               # = [System.IO.Path]
[IO.File]               # = [System.IO.File]
[IO.Directory]          # = [System.IO.Directory]
[Text.Encoding]         # = [System.Text.Encoding]
[Net.WebClient]         # = [System.Net.WebClient]
[Version]               # = [System.Version]
[Guid]                  # = [System.Guid]
[Regex]                 # = [System.Text.RegularExpressions.Regex]
[Convert]               # = [System.Convert]
```

#### よく使う .NET クラス一覧

| クラス | 用途 | 主なメソッド/プロパティ |
|--------|------|------------------------|
| `[Environment]` | 環境変数・システム情報 | `GetEnvironmentVariable()`, `SetEnvironmentVariable()` |
| `[DateTime]` | 日時操作 | `Now`, `Today`, `Parse()` |
| `[Math]` | 数学関数 | `Round()`, `Max()`, `Min()`, `Abs()` |
| `[IO.Path]` | パス操作 | `Combine()`, `GetFileName()`, `GetExtension()` |
| `[IO.File]` | ファイル操作 | `ReadAllText()`, `WriteAllText()`, `Exists()` |
| `[IO.Directory]` | ディレクトリ操作 | `CreateDirectory()`, `Exists()` |
| `[Version]` | バージョン比較 | 比較演算子で使用 |
| `[Guid]` | GUID生成 | `NewGuid()` |
| `[Convert]` | 型変換 | `ToInt32()`, `ToString()`, `ToBase64String()` |

#### .NET クラス使用例

```powershell
# [Environment] - 環境変数・システム情報
[Environment]::GetEnvironmentVariable("PATH", "User")      # ユーザーPATH取得
[Environment]::SetEnvironmentVariable("MY_VAR", "value", "User")  # 環境変数設定
[Environment]::MachineName              # PC名
[Environment]::UserName                 # ユーザー名
[Environment]::OSVersion                # OS情報
[Environment]::Is64BitOperatingSystem   # 64bit確認
[Environment]::GetFolderPath("Desktop") # 特殊フォルダパス

# SetEnvironmentVariable の第3引数（スコープ）
# "Process" - 現在のプロセスのみ（デフォルト）
# "User"    - 現在のユーザー（永続化）
# "Machine" - システム全体（管理者権限必要、永続化）

# [DateTime] - 日時操作
[DateTime]::Now                         # 現在日時
[DateTime]::Today                       # 今日の日付（時刻は00:00:00）
[DateTime]::UtcNow                      # UTC現在日時
[DateTime]::Parse("2024-01-15")         # 文字列から変換
[DateTime]::Now.ToString("yyyy-MM-dd HH:mm:ss")  # フォーマット

# [Math] - 数学関数
[Math]::Round(3.14159, 2)               # 3.14（小数点2桁で丸め）
[Math]::Floor(3.7)                      # 3（切り捨て）
[Math]::Ceiling(3.2)                    # 4（切り上げ）
[Math]::Max(10, 20)                     # 20
[Math]::Min(10, 20)                     # 10
[Math]::Abs(-5)                         # 5
[Math]::Pow(2, 10)                      # 1024（2の10乗）
[Math]::Sqrt(16)                        # 4（平方根）

# [IO.Path] - パス操作
[IO.Path]::Combine("C:\dev", "tools", "jdk")   # C:\dev\tools\jdk
[IO.Path]::GetFileName("C:\dev\file.txt")      # file.txt
[IO.Path]::GetFileNameWithoutExtension("file.txt")  # file
[IO.Path]::GetExtension("file.txt")            # .txt
[IO.Path]::GetDirectoryName("C:\dev\file.txt") # C:\dev
[IO.Path]::GetFullPath(".\file.txt")           # 絶対パスに変換
[IO.Path]::GetTempPath()                       # 一時フォルダパス

# [IO.File] - ファイル操作
[IO.File]::Exists("C:\dev\file.txt")           # ファイル存在確認
[IO.File]::ReadAllText("C:\dev\file.txt")      # 全文読み込み
[IO.File]::WriteAllText("C:\dev\file.txt", "content")  # 書き込み
[IO.File]::ReadAllLines("C:\dev\file.txt")     # 行配列で読み込み
[IO.File]::Copy("src.txt", "dest.txt", $true)  # コピー（上書き）

# [IO.Directory] - ディレクトリ操作
[IO.Directory]::Exists("C:\dev\tools")         # フォルダ存在確認
[IO.Directory]::CreateDirectory("C:\dev\new")  # フォルダ作成
[IO.Directory]::GetFiles("C:\dev", "*.txt")    # ファイル一覧
[IO.Directory]::GetDirectories("C:\dev")       # サブフォルダ一覧

# [Version] - バージョン比較
[Version]"21.0.2" -gt [Version]"17.0.1"        # True
[Version]"1.2.3" -eq [Version]"1.2.3"          # True
$v = [Version]"21.0.2"
$v.Major    # 21
$v.Minor    # 0
$v.Build    # 2

# [Guid] - GUID生成
[Guid]::NewGuid()                              # 新しいGUID生成
[Guid]::NewGuid().ToString()                   # 文字列として取得

# [Convert] - 型変換
[Convert]::ToInt32("123")                      # 文字列→整数
[Convert]::ToString(123)                       # 整数→文字列
[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes("hello"))  # Base64エンコード
[Text.Encoding]::UTF8.GetString([Convert]::FromBase64String("aGVsbG8="))  # Base64デコード

# [Regex] - 正規表現
[Regex]::Match("version 1.2.3", "\d+\.\d+\.\d+").Value  # "1.2.3"
[Regex]::IsMatch("hello", "^h")                # True
[Regex]::Replace("hello world", "world", "PS") # "hello PS"
```

#### 静的メソッド vs インスタンスメソッド

```powershell
# 静的メソッド: [クラス]::メソッド()
[DateTime]::Now
[Math]::Round(3.14, 1)
[IO.Path]::Combine("a", "b")

# インスタンスメソッド: $オブジェクト.メソッド()
$date = Get-Date
$date.AddDays(7)
$date.ToString("yyyy-MM-dd")

$str = "Hello"
$str.ToUpper()
$str.Contains("ell")
```

### 演算子

```powershell
# 比較演算子
-eq    # 等しい
-ne    # 等しくない
-gt    # より大きい
-lt    # より小さい
-ge    # 以上
-le    # 以下
-like  # ワイルドカードマッチ
-match # 正規表現マッチ

# 論理演算子
-and   # AND
-or    # OR
-not   # NOT
!      # NOT（省略形）

# 例
if ($version -ge "1.0" -and $installed -eq $true) {
    Write-Host "OK"
}
```

### 制御構文

```powershell
# if文
if ($condition) {
    # 処理
} elseif ($other) {
    # 処理
} else {
    # 処理
}

# switch文
switch ($value) {
    "a" { "A です" }
    "b" { "B です" }
    default { "その他" }
}

# for ループ
for ($i = 0; $i -lt 10; $i++) {
    Write-Host $i
}

# foreach ループ
foreach ($item in $collection) {
    Write-Host $item
}

# ForEach-Object（パイプライン）
$collection | ForEach-Object {
    Write-Host $_
}

# while ループ
while ($condition) {
    # 処理
}
```

### 関数定義

```powershell
# 基本的な関数
function Get-Greeting {
    param (
        [string]$Name = "World"
    )
    return "Hello, $Name!"
}

# 呼び出し
Get-Greeting -Name "PowerShell"

# 高度なパラメータ
function Install-Package {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory=$true)]
        [string]$Name,

        [Parameter(Mandatory=$false)]
        [string]$Version = "latest",

        [switch]$Force
    )

    if ($Force) {
        Write-Host "強制インストール: $Name ($Version)"
    }
}
```

---

## 基本コマンドレット

### ヘルプ・情報

| コマンド | 説明 | 例 |
|----------|------|-----|
| `Get-Help` | ヘルプ表示 | `Get-Help Get-Process -Full` |
| `Get-Command` | コマンド一覧 | `Get-Command *-Item*` |
| `Get-Member` | オブジェクトのメンバー | `$obj \| Get-Member` |
| `Get-Alias` | エイリアス一覧 | `Get-Alias ls` |

### 出力

| コマンド | 説明 | 例 |
|----------|------|-----|
| `Write-Host` | コンソール出力 | `Write-Host "Hello" -ForegroundColor Green` |
| `Write-Output` | パイプライン出力 | `Write-Output $result` |
| `Write-Warning` | 警告出力 | `Write-Warning "注意"` |
| `Write-Error` | エラー出力 | `Write-Error "エラー発生"` |
| `Write-Verbose` | 詳細出力 | `Write-Verbose "詳細情報"` |

### ファイル・フォルダ操作

| コマンド | エイリアス | 説明 |
|----------|-----------|------|
| `Get-ChildItem` | `ls`, `dir`, `gci` | ファイル一覧 |
| `Get-Item` | `gi` | アイテム取得 |
| `Set-Location` | `cd`, `sl` | ディレクトリ移動 |
| `Get-Location` | `pwd`, `gl` | カレントディレクトリ |
| `New-Item` | `ni` | ファイル/フォルダ作成 |
| `Copy-Item` | `cp`, `copy`, `ci` | コピー |
| `Move-Item` | `mv`, `move`, `mi` | 移動 |
| `Remove-Item` | `rm`, `del`, `ri` | 削除 |
| `Rename-Item` | `ren`, `rni` | 名前変更 |
| `Test-Path` | - | 存在確認 |

```powershell
# 例
Get-ChildItem -Path "C:\dev" -Recurse -Filter "*.ps1"
New-Item -Path "C:\dev\tools" -ItemType Directory -Force
Copy-Item -Path "source.txt" -Destination "dest.txt" -Force
Test-Path -Path "C:\dev\tools"  # True/False
```

### ファイル内容操作

| コマンド | 説明 | 例 |
|----------|------|-----|
| `Get-Content` | ファイル読み込み | `Get-Content -Path "file.txt"` |
| `Set-Content` | ファイル書き込み（上書き） | `Set-Content -Path "file.txt" -Value "text"` |
| `Add-Content` | ファイル追記 | `Add-Content -Path "file.txt" -Value "追加"` |
| `Clear-Content` | ファイル内容クリア | `Clear-Content -Path "file.txt"` |

```powershell
# 全行読み込み
$lines = Get-Content -Path "file.txt"

# 配列として処理
$lines | ForEach-Object { Write-Host $_ }

# エンコーディング指定
Get-Content -Path "file.txt" -Encoding UTF8
Set-Content -Path "file.txt" -Value $content -Encoding UTF8
```

### 文字列操作

```powershell
# 文字列操作メソッド
$str = "Hello World"
$str.ToUpper()          # HELLO WORLD
$str.ToLower()          # hello world
$str.Replace("World", "PowerShell")
$str.Split(" ")         # @("Hello", "World")
$str.Trim()             # 前後空白削除
$str.StartsWith("Hello") # True
$str.EndsWith("World")   # True
$str.Contains("llo")     # True
$str.Substring(0, 5)     # Hello

# 正規表現
$str -match "^Hello"     # True
$str -replace "World", "PS"

# フォーマット
"Name: {0}, Age: {1}" -f "John", 30
```

### パイプラインとフィルタリング

| コマンド | 説明 | 例 |
|----------|------|-----|
| `Where-Object` | フィルタリング | `$items \| Where-Object { $_.Name -like "*.txt" }` |
| `Select-Object` | プロパティ選択 | `$items \| Select-Object Name, Size` |
| `Sort-Object` | ソート | `$items \| Sort-Object Name` |
| `Group-Object` | グループ化 | `$items \| Group-Object Extension` |
| `Measure-Object` | 集計 | `$items \| Measure-Object -Property Size -Sum` |
| `ForEach-Object` | 各要素処理 | `$items \| ForEach-Object { $_.Name }` |

```powershell
# パイプライン例
Get-ChildItem -Path "C:\dev" -File |
    Where-Object { $_.Length -gt 1MB } |
    Sort-Object Length -Descending |
    Select-Object Name, @{N="SizeMB";E={[math]::Round($_.Length/1MB, 2)}}
```

---

## エラーハンドリング

### try-catch-finally

```powershell
try {
    # エラーが発生する可能性のある処理
    $result = Get-Content -Path "notexist.txt" -ErrorAction Stop
}
catch [System.IO.FileNotFoundException] {
    Write-Warning "ファイルが見つかりません: $_"
}
catch {
    Write-Error "予期しないエラー: $_"
}
finally {
    # 常に実行される処理
    Write-Host "処理完了"
}
```

### ErrorAction

```powershell
# エラー時の動作制御
-ErrorAction Stop        # エラーで停止（例外発生）
-ErrorAction Continue    # エラー表示して続行（デフォルト）
-ErrorAction SilentlyContinue  # エラー非表示で続行
-ErrorAction Ignore      # 完全無視

# 例
Remove-Item -Path "notexist.txt" -ErrorAction SilentlyContinue
```

### $ErrorActionPreference

```powershell
# スクリプト全体のデフォルト設定
$ErrorActionPreference = "Stop"
```

---

## スクリプト実行

### 実行ポリシー

```powershell
# 現在のポリシー確認
Get-ExecutionPolicy

# ポリシー変更（管理者権限必要）
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# 一時的にバイパス
powershell -ExecutionPolicy Bypass -File script.ps1
```

| ポリシー | 説明 |
|----------|------|
| Restricted | スクリプト実行不可（デフォルト） |
| AllSigned | 署名付きのみ実行可 |
| RemoteSigned | ローカルは実行可、リモートは署名必要 |
| Unrestricted | 全て実行可（警告あり） |
| Bypass | 警告なしで全て実行可 |

### スクリプトファイル

```powershell
# script.ps1
param (
    [Parameter(Mandatory=$true)]
    [string]$InputPath,

    [string]$OutputPath = ".\output"
)

# スクリプトのディレクトリ取得
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# 処理
Write-Host "入力: $InputPath"
Write-Host "出力: $OutputPath"
```

```powershell
# 実行
.\script.ps1 -InputPath "C:\data" -OutputPath "C:\output"
```

---

## よく使うコマンドレット一覧

### システム情報

| コマンド | 説明 |
|----------|------|
| `Get-Process` | プロセス一覧 |
| `Get-Service` | サービス一覧 |
| `Get-EventLog` | イベントログ |
| `Get-WmiObject` | WMI情報取得 |
| `Get-CimInstance` | CIM情報取得（推奨） |
| `Get-ComputerInfo` | PC情報 |

### ネットワーク

| コマンド | 説明 |
|----------|------|
| `Test-Connection` | ping相当 |
| `Test-NetConnection` | ポート疎通確認 |
| `Invoke-WebRequest` | HTTPリクエスト |
| `Invoke-RestMethod` | REST API呼び出し |

### アーカイブ

| コマンド | 説明 |
|----------|------|
| `Compress-Archive` | ZIP圧縮 |
| `Expand-Archive` | ZIP展開 |

### データ変換

| コマンド | 説明 |
|----------|------|
| `ConvertTo-Json` | JSONへ変換 |
| `ConvertFrom-Json` | JSONから変換 |
| `ConvertTo-Csv` | CSVへ変換 |
| `ConvertFrom-Csv` | CSVから変換 |
| `Import-Csv` | CSVファイル読み込み |
| `Export-Csv` | CSVファイル書き出し |
| `ConvertTo-Xml` | XMLへ変換 |

---

## .NET Framework / .NET Core について

### .NET とは

Microsoft が開発したアプリケーション開発プラットフォーム。プログラミング言語（C#, VB.NET, F# など）と膨大なライブラリ群を提供する。

### 歴史

```
2002年 .NET Framework 1.0 リリース（Windows専用）
  ↓
2016年 .NET Core 1.0 リリース（クロスプラットフォーム）
  ↓
2020年 .NET 5 で統合（.NET Core の後継、"Core" の名前を廃止）
  ↓
2024年 .NET 8（現在の最新LTS）
```

### 比較表

| 項目 | .NET Framework | .NET Core / .NET 5+ |
|------|----------------|---------------------|
| 対応OS | **Windows のみ** | Windows / macOS / Linux |
| 最新版 | 4.8.1（最終版） | .NET 8（継続開発中） |
| 状況 | メンテナンスモード | 現在の主流 |
| Windows標準 | あり | なし（別途インストール） |

### PowerShell との関係

| PowerShell | 基盤 |
|------------|------|
| Windows PowerShell 5.1 | .NET Framework（Windows標準搭載）|
| PowerShell 7.x | .NET Core / .NET 5+（クロスプラットフォーム）|

### 簡単なイメージ

```
.NET Framework / .NET Core
  = 膨大なライブラリ（クラス）の集合体

[Environment], [DateTime], [Math], [IO.Path] など
  = そのライブラリに含まれるクラス

PowerShell
  = これらのクラスを簡単に呼び出せるシェル
```

---

## PowerShell 標準機能 vs .NET クラス

### パッケージ管理ツール作成に必要な機能

| 機能 | PowerShell コマンド | .NET クラス必要? |
|------|-------------------|-----------------|
| JSON読み書き | `ConvertFrom-Json`, `ConvertTo-Json` | 不要 |
| ZIP展開 | `Expand-Archive` | 不要 |
| ハッシュ計算 | `Get-FileHash` | 不要 |
| ファイル操作 | `Copy-Item`, `Remove-Item`, `Test-Path` | 不要 |
| フォルダ操作 | `New-Item`, `Get-ChildItem` | 不要 |
| プロセス実行 | `Start-Process` | 不要 |
| 環境変数（永続化） | - | **必要** `[Environment]` |
| バージョン比較 | - | **必要** `[Version]` |

### 結論

```
パッケージ管理ツール作成に必要な .NET クラス:
  - [Environment]  ← 環境変数の永続化に必須
  - [Version]      ← バージョン比較に便利

それ以外は PowerShell コマンドレットで十分
```

### 実際のコード例

```powershell
# ほぼ PowerShell 標準だけで書ける
$packages = Get-Content "packages.json" -Raw | ConvertFrom-Json  # JSON読み込み
Expand-Archive -Path "jdk.zip" -DestinationPath "C:\dev"         # ZIP展開
$hash = (Get-FileHash -Path "jdk.zip" -Algorithm SHA256).Hash    # ハッシュ
Copy-Item -Path "config.xml" -Destination "C:\app\" -Force       # コピー
Test-Path -Path "C:\dev\jdk"                                     # 存在確認
Start-Process -FilePath "installer.exe" -ArgumentList "/S" -Wait # インストーラー実行

# .NET クラスが必要なのはこの2つだけ
[Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\dev\jdk", "User")  # 環境変数永続化
[Version]"21.0.2" -gt [Version]"17.0.1"  # バージョン比較
```

**.NET の深い知識は不要。** `[Environment]` と `[Version]` の使い方だけ覚えればOK。

---

## 参考リンク

- [Microsoft Learn - PowerShell ドキュメント](https://learn.microsoft.com/ja-jp/powershell/)
- [Microsoft Learn - .NET ドキュメント](https://learn.microsoft.com/ja-jp/dotnet/)
- [PowerShell Gallery](https://www.powershellgallery.com/)
- [About コマンドレット一覧](https://learn.microsoft.com/ja-jp/powershell/module/microsoft.powershell.core/about/about_core_commands)
