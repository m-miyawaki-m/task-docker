# JSON方式 バージョン管理設計

パッケージのバージョン管理を JSON 形式で行う設計ドキュメント。

## 概要

### CSV方式からJSON方式へ

| 観点 | CSV | JSON |
|------|-----|------|
| 可読性 | △ Excel依存 | ◎ 構造化 |
| ネスト | × 不可 | ◎ 可能 |
| 型情報 | × 全て文字列 | ◎ 数値・配列・真偽値 |
| コメント | × 不可 | △ 非標準 |
| バージョン管理 | △ 差分見づらい | ◎ 差分見やすい |
| PowerShell連携 | ◎ Import-Csv | ◎ ConvertFrom-Json |

---

## ファイル構成

```
dev-env-setup/
├── packages.json           # パッケージ定義（マスター）
├── configs.json            # 設定ファイル定義
├── installed.json          # インストール済み情報（自動生成）
├── packages/               # インストーラー格納
├── configs/                # 設定ファイル格納
└── scripts/
    ├── Install-DevEnv.ps1
    ├── Apply-Configs.ps1
    ├── Check-Installed.ps1
    └── Uninstall-DevEnv.ps1
```

---

## packages.json 設計

### 基本構造

```json
{
  "$schema": "./schemas/packages.schema.json",
  "version": "1.0.0",
  "description": "開発環境パッケージ定義",
  "lastUpdated": "2024-01-15",
  "defaults": {
    "installRoot": "C:\\dev-tools",
    "createShortcut": false
  },
  "packages": [
    {
      "id": "openjdk",
      "name": "OpenJDK",
      "version": "21.0.2",
      "source": {
        "type": "zip",
        "path": "packages/openjdk-21.0.2_windows-x64_bin.zip",
        "hash": {
          "algorithm": "SHA256",
          "value": "abc123..."
        }
      },
      "install": {
        "path": "C:\\dev-tools\\jdk-21",
        "skipRootFolder": true
      },
      "environment": {
        "variables": {
          "JAVA_HOME": "C:\\dev-tools\\jdk-21"
        },
        "pathEntries": [
          "%JAVA_HOME%\\bin"
        ]
      },
      "verify": {
        "command": "java",
        "args": ["-version"],
        "versionPattern": "openjdk (\\d+\\.\\d+\\.\\d+)"
      },
      "dependencies": [],
      "tags": ["java", "jdk", "required"]
    }
  ]
}
```

### フィールド定義

#### トップレベル

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|:----:|------|
| `$schema` | string | - | JSONスキーマ参照 |
| `version` | string | ◎ | 定義ファイルバージョン |
| `description` | string | - | 説明 |
| `lastUpdated` | string | - | 最終更新日 |
| `defaults` | object | - | デフォルト設定 |
| `packages` | array | ◎ | パッケージ定義配列 |

#### packages[]

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|:----:|------|
| `id` | string | ◎ | 一意識別子（英数字、ハイフン） |
| `name` | string | ◎ | 表示名 |
| `version` | string | ◎ | バージョン |
| `enabled` | boolean | - | 有効/無効（デフォルト: true） |
| `source` | object | ◎ | ソース情報 |
| `install` | object | ◎ | インストール設定 |
| `environment` | object | - | 環境変数設定 |
| `verify` | object | - | 検証コマンド |
| `dependencies` | array | - | 依存パッケージID |
| `tags` | array | - | タグ |

#### source

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|:----:|------|
| `type` | string | ◎ | "zip", "msi", "exe", "copy" |
| `path` | string | ◎ | ファイルパス（相対/絶対） |
| `hash` | object | - | ハッシュ検証 |
| `hash.algorithm` | string | - | "SHA256", "SHA512", "MD5" |
| `hash.value` | string | - | ハッシュ値 |

#### install

| フィールド | 型 | 必須 | 説明 |
|-----------|-----|:----:|------|
| `path` | string | ◎ | インストール先パス |
| `skipRootFolder` | boolean | - | ZIPのルートフォルダをスキップ |
| `silentArgs` | array | - | サイレントインストール引数 |
| `postInstall` | array | - | インストール後コマンド |

#### environment

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `variables` | object | 環境変数（キー:値） |
| `pathEntries` | array | PATHに追加するパス |
| `scope` | string | "User"（デフォルト） or "Machine" |

#### verify

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `command` | string | 検証コマンド |
| `args` | array | コマンド引数 |
| `versionPattern` | string | バージョン抽出正規表現 |
| `successExitCode` | number | 成功時終了コード（デフォルト: 0） |

---

## packages.json 完全サンプル

```json
{
  "$schema": "./schemas/packages.schema.json",
  "version": "1.0.0",
  "description": "開発環境パッケージ定義",
  "lastUpdated": "2024-01-15",
  "defaults": {
    "installRoot": "C:\\dev-tools",
    "hashAlgorithm": "SHA256",
    "environmentScope": "User"
  },
  "packages": [
    {
      "id": "openjdk-21",
      "name": "OpenJDK 21",
      "version": "21.0.2",
      "enabled": true,
      "source": {
        "type": "zip",
        "path": "packages/openjdk-21.0.2_windows-x64_bin.zip",
        "hash": {
          "algorithm": "SHA256",
          "value": "9a5a38b02e0bdd0b2d5f37b7815c6a246e7fb7e6d0b5a5e13d3e5d3e7a9c1b4d"
        }
      },
      "install": {
        "path": "C:\\dev-tools\\jdk-21",
        "skipRootFolder": true
      },
      "environment": {
        "variables": {
          "JAVA_HOME": "C:\\dev-tools\\jdk-21"
        },
        "pathEntries": [
          "%JAVA_HOME%\\bin"
        ]
      },
      "verify": {
        "command": "java",
        "args": ["-version"],
        "versionPattern": "openjdk (\\d+)"
      },
      "tags": ["java", "jdk", "required"]
    },
    {
      "id": "maven",
      "name": "Apache Maven",
      "version": "3.9.6",
      "source": {
        "type": "zip",
        "path": "packages/apache-maven-3.9.6-bin.zip",
        "hash": {
          "algorithm": "SHA256",
          "value": "1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b"
        }
      },
      "install": {
        "path": "C:\\dev-tools\\maven-3.9.6",
        "skipRootFolder": true
      },
      "environment": {
        "variables": {
          "MAVEN_HOME": "C:\\dev-tools\\maven-3.9.6",
          "M2_HOME": "C:\\dev-tools\\maven-3.9.6"
        },
        "pathEntries": [
          "%MAVEN_HOME%\\bin"
        ]
      },
      "verify": {
        "command": "mvn",
        "args": ["--version"],
        "versionPattern": "Apache Maven (\\d+\\.\\d+\\.\\d+)"
      },
      "dependencies": ["openjdk-21"],
      "tags": ["java", "build"]
    },
    {
      "id": "gradle",
      "name": "Gradle",
      "version": "8.5",
      "source": {
        "type": "zip",
        "path": "packages/gradle-8.5-bin.zip",
        "hash": {
          "algorithm": "SHA256",
          "value": "2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c"
        }
      },
      "install": {
        "path": "C:\\dev-tools\\gradle-8.5",
        "skipRootFolder": true
      },
      "environment": {
        "variables": {
          "GRADLE_HOME": "C:\\dev-tools\\gradle-8.5"
        },
        "pathEntries": [
          "%GRADLE_HOME%\\bin"
        ]
      },
      "verify": {
        "command": "gradle",
        "args": ["--version"],
        "versionPattern": "Gradle (\\d+\\.\\d+)"
      },
      "dependencies": ["openjdk-21"],
      "tags": ["java", "build"]
    },
    {
      "id": "git",
      "name": "Git for Windows",
      "version": "2.43.0",
      "source": {
        "type": "exe",
        "path": "packages/Git-2.43.0-64-bit.exe",
        "hash": {
          "algorithm": "SHA256",
          "value": "3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d"
        }
      },
      "install": {
        "path": "C:\\dev-tools\\git",
        "silentArgs": [
          "/VERYSILENT",
          "/NORESTART",
          "/NOCANCEL",
          "/SP-",
          "/CLOSEAPPLICATIONS",
          "/RESTARTAPPLICATIONS",
          "/DIR=C:\\dev-tools\\git"
        ]
      },
      "environment": {
        "pathEntries": [
          "C:\\dev-tools\\git\\bin",
          "C:\\dev-tools\\git\\cmd"
        ]
      },
      "verify": {
        "command": "git",
        "args": ["--version"],
        "versionPattern": "git version (\\d+\\.\\d+\\.\\d+)"
      },
      "tags": ["vcs", "required"]
    },
    {
      "id": "nodejs",
      "name": "Node.js LTS",
      "version": "20.11.0",
      "source": {
        "type": "zip",
        "path": "packages/node-v20.11.0-win-x64.zip",
        "hash": {
          "algorithm": "SHA256",
          "value": "4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e"
        }
      },
      "install": {
        "path": "C:\\dev-tools\\nodejs",
        "skipRootFolder": true
      },
      "environment": {
        "variables": {
          "NODE_HOME": "C:\\dev-tools\\nodejs"
        },
        "pathEntries": [
          "%NODE_HOME%"
        ]
      },
      "verify": {
        "command": "node",
        "args": ["--version"],
        "versionPattern": "v(\\d+\\.\\d+\\.\\d+)"
      },
      "tags": ["javascript", "runtime"]
    },
    {
      "id": "eclipse",
      "name": "Eclipse IDE for Java Developers",
      "version": "2023-12",
      "source": {
        "type": "zip",
        "path": "packages/eclipse-java-2023-12-R-win32-x86_64.zip"
      },
      "install": {
        "path": "C:\\dev-tools\\eclipse",
        "skipRootFolder": true
      },
      "environment": {
        "variables": {
          "ECLIPSE_HOME": "C:\\dev-tools\\eclipse"
        }
      },
      "verify": {
        "command": "C:\\dev-tools\\eclipse\\eclipse.exe",
        "args": ["-version"],
        "versionPattern": "Eclipse IDE (\\d{4}-\\d{2})"
      },
      "dependencies": ["openjdk-21"],
      "tags": ["ide", "java"]
    },
    {
      "id": "sqldeveloper",
      "name": "Oracle SQL Developer",
      "version": "23.1.1",
      "enabled": true,
      "source": {
        "type": "zip",
        "path": "packages/sqldeveloper-23.1.1.345-x64.zip"
      },
      "install": {
        "path": "C:\\dev-tools\\sqldeveloper",
        "skipRootFolder": true
      },
      "environment": {
        "variables": {
          "SQLDEVELOPER_HOME": "C:\\dev-tools\\sqldeveloper"
        }
      },
      "dependencies": ["openjdk-21"],
      "tags": ["database", "oracle"]
    }
  ]
}
```

---

## configs.json 設計

### 基本構造

```json
{
  "$schema": "./schemas/configs.schema.json",
  "version": "1.0.0",
  "configs": [
    {
      "id": "eclipse-ini",
      "targetPackage": "eclipse",
      "name": "Eclipse JVM設定",
      "source": "configs/eclipse/eclipse.ini.patch",
      "destination": "%ECLIPSE_HOME%/eclipse.ini",
      "action": "patch",
      "backup": true
    }
  ]
}
```

### 完全サンプル

```json
{
  "$schema": "./schemas/configs.schema.json",
  "version": "1.0.0",
  "description": "開発ツール設定ファイル定義",
  "configs": [
    {
      "id": "eclipse-ini",
      "targetPackage": "eclipse",
      "name": "Eclipse JVM設定",
      "source": "configs/eclipse/eclipse.ini.patch",
      "destination": "%ECLIPSE_HOME%\\eclipse.ini",
      "action": "patch",
      "backup": true,
      "description": "JVMメモリ設定、エンコーディング"
    },
    {
      "id": "eclipse-formatter",
      "targetPackage": "eclipse",
      "name": "Eclipseコードフォーマッター",
      "source": "configs/eclipse/formatter.xml",
      "destination": "%ECLIPSE_HOME%\\formatter.xml",
      "action": "copy",
      "backup": false
    },
    {
      "id": "eclipse-plugins",
      "targetPackage": "eclipse",
      "name": "Eclipseプラグイン",
      "source": "configs/eclipse/plugins",
      "destination": "%ECLIPSE_HOME%\\dropins",
      "action": "copy_folder",
      "backup": false
    },
    {
      "id": "sqldeveloper-connections",
      "targetPackage": "sqldeveloper",
      "name": "SQLDeveloper接続情報",
      "source": "configs/sqldeveloper/connections.json",
      "destination": "%APPDATA%\\SQL Developer\\system*\\o.jdeveloper.db.connection\\connections.json",
      "action": "copy",
      "backup": true
    },
    {
      "id": "git-config",
      "targetPackage": "git",
      "name": "Git設定",
      "source": "configs/git/.gitconfig",
      "destination": "%USERPROFILE%\\.gitconfig",
      "action": "merge",
      "backup": true
    },
    {
      "id": "maven-settings",
      "targetPackage": "maven",
      "name": "Maven設定",
      "source": "configs/maven/settings.xml",
      "destination": "%USERPROFILE%\\.m2\\settings.xml",
      "action": "copy",
      "backup": true
    },
    {
      "id": "gradle-properties",
      "targetPackage": "gradle",
      "name": "Gradle設定",
      "source": "configs/gradle/gradle.properties",
      "destination": "%USERPROFILE%\\.gradle\\gradle.properties",
      "action": "copy",
      "backup": true
    },
    {
      "id": "npm-config",
      "targetPackage": "nodejs",
      "name": "npm設定",
      "source": "configs/nodejs/.npmrc",
      "destination": "%USERPROFILE%\\.npmrc",
      "action": "copy",
      "backup": true
    }
  ]
}
```

### action 種別

| action | 説明 | 用途 |
|--------|------|------|
| `copy` | ファイルコピー | 設定ファイル配置 |
| `copy_folder` | フォルダコピー | プラグイン配置 |
| `patch` | 差分適用 | INIファイル編集 |
| `merge` | マージ（JSON/INI） | 既存設定との統合 |
| `template` | テンプレート展開 | 環境変数置換 |

---

## installed.json 設計

インストール済み情報を記録するファイル（自動生成）。

```json
{
  "$schema": "./schemas/installed.schema.json",
  "version": "1.0.0",
  "generatedAt": "2024-01-15T10:30:00+09:00",
  "machineId": "DESKTOP-ABC123",
  "userName": "developer",
  "packages": [
    {
      "id": "openjdk-21",
      "name": "OpenJDK 21",
      "version": "21.0.2",
      "installedVersion": "21.0.2",
      "installPath": "C:\\dev-tools\\jdk-21",
      "installedAt": "2024-01-15T10:00:00+09:00",
      "status": "installed",
      "sourceHash": "9a5a38b02e0bdd0b...",
      "environment": {
        "variables": {
          "JAVA_HOME": "C:\\dev-tools\\jdk-21"
        },
        "pathEntries": [
          "C:\\dev-tools\\jdk-21\\bin"
        ]
      }
    },
    {
      "id": "maven",
      "name": "Apache Maven",
      "version": "3.9.6",
      "installedVersion": "3.9.6",
      "installPath": "C:\\dev-tools\\maven-3.9.6",
      "installedAt": "2024-01-15T10:05:00+09:00",
      "status": "installed"
    },
    {
      "id": "git",
      "name": "Git for Windows",
      "version": "2.43.0",
      "installedVersion": "2.42.0",
      "installPath": "C:\\dev-tools\\git",
      "installedAt": "2024-01-10T09:00:00+09:00",
      "status": "version_mismatch",
      "note": "期待: 2.43.0, 実際: 2.42.0"
    }
  ],
  "configs": [
    {
      "id": "eclipse-ini",
      "appliedAt": "2024-01-15T10:10:00+09:00",
      "backupPath": "C:\\dev-tools\\backups\\eclipse.ini.20240115_101000"
    }
  ]
}
```

### status 値

| status | 説明 |
|--------|------|
| `installed` | 正常インストール済み |
| `version_mismatch` | バージョン不一致 |
| `failed` | インストール失敗 |
| `removed` | アンインストール済み |

---

## PowerShell スクリプト例

### Install-DevEnv.ps1

```powershell
#Requires -Version 5.1

[CmdletBinding()]
param (
    [string]$PackagesFile = ".\packages.json",
    [string]$InstalledFile = ".\installed.json",
    [string[]]$Tags,
    [string[]]$PackageIds,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# JSONファイル読み込み
$packagesJson = Get-Content -Path $PackagesFile -Raw | ConvertFrom-Json
$packages = $packagesJson.packages

# インストール済み情報読み込み
$installed = @{}
if (Test-Path $InstalledFile) {
    $installedJson = Get-Content -Path $InstalledFile -Raw | ConvertFrom-Json
    foreach ($pkg in $installedJson.packages) {
        $installed[$pkg.id] = $pkg
    }
}

# フィルタリング
if ($Tags) {
    $packages = $packages | Where-Object {
        $pkgTags = $_.tags
        $Tags | Where-Object { $pkgTags -contains $_ }
    }
}
if ($PackageIds) {
    $packages = $packages | Where-Object { $PackageIds -contains $_.id }
}

# インストール処理
$results = @()

foreach ($pkg in $packages) {
    if (-not $pkg.enabled -and $pkg.enabled -ne $null) {
        Write-Host "[$($pkg.id)] スキップ（無効化）" -ForegroundColor Gray
        continue
    }

    # 既存チェック
    if ($installed.ContainsKey($pkg.id) -and -not $Force) {
        $existingVersion = $installed[$pkg.id].installedVersion
        if ($existingVersion -eq $pkg.version) {
            Write-Host "[$($pkg.id)] スキップ（インストール済み: $existingVersion）" -ForegroundColor Green
            continue
        } else {
            Write-Host "[$($pkg.id)] バージョン不一致（期待: $($pkg.version), 現在: $existingVersion）" -ForegroundColor Yellow
        }
    }

    Write-Host "[$($pkg.id)] インストール開始: $($pkg.name) $($pkg.version)" -ForegroundColor Cyan

    # ハッシュ検証
    if ($pkg.source.hash) {
        $sourcePath = $pkg.source.path
        $expectedHash = $pkg.source.hash.value
        $algorithm = $pkg.source.hash.algorithm

        $actualHash = (Get-FileHash -Path $sourcePath -Algorithm $algorithm).Hash
        if ($actualHash -ne $expectedHash.ToUpper()) {
            Write-Warning "[$($pkg.id)] ハッシュ不一致！"
            $results += @{ id = $pkg.id; status = "failed"; reason = "hash_mismatch" }
            continue
        }
    }

    # インストール実行
    try {
        switch ($pkg.source.type) {
            "zip" {
                $destPath = $pkg.install.path
                if (Test-Path $destPath) {
                    Remove-Item -Path $destPath -Recurse -Force
                }
                New-Item -Path $destPath -ItemType Directory -Force | Out-Null

                if ($pkg.install.skipRootFolder) {
                    # 一時展開してルートフォルダをスキップ
                    $tempPath = Join-Path $env:TEMP ([System.IO.Path]::GetRandomFileName())
                    Expand-Archive -Path $pkg.source.path -DestinationPath $tempPath -Force

                    $rootItems = Get-ChildItem -Path $tempPath
                    if ($rootItems.Count -eq 1 -and $rootItems[0].PSIsContainer) {
                        Copy-Item -Path "$($rootItems[0].FullName)\*" -Destination $destPath -Recurse -Force
                    } else {
                        Copy-Item -Path "$tempPath\*" -Destination $destPath -Recurse -Force
                    }
                    Remove-Item -Path $tempPath -Recurse -Force
                } else {
                    Expand-Archive -Path $pkg.source.path -DestinationPath $destPath -Force
                }
            }
            "msi" {
                $args = @("/i", "`"$($pkg.source.path)`"", "/qn", "/norestart")
                if ($pkg.install.path) {
                    $args += "INSTALLDIR=`"$($pkg.install.path)`""
                }
                Start-Process -FilePath "msiexec.exe" -ArgumentList $args -Wait -NoNewWindow
            }
            "exe" {
                $args = $pkg.install.silentArgs -join " "
                Start-Process -FilePath $pkg.source.path -ArgumentList $args -Wait -NoNewWindow
            }
            "copy" {
                Copy-Item -Path $pkg.source.path -Destination $pkg.install.path -Recurse -Force
            }
        }

        # 環境変数設定
        if ($pkg.environment) {
            $scope = if ($pkg.environment.scope) { $pkg.environment.scope } else { "User" }

            # 変数設定
            if ($pkg.environment.variables) {
                foreach ($varName in $pkg.environment.variables.PSObject.Properties.Name) {
                    $varValue = $pkg.environment.variables.$varName
                    [Environment]::SetEnvironmentVariable($varName, $varValue, $scope)
                    Write-Host "  環境変数設定: $varName = $varValue"
                }
            }

            # PATH追加
            if ($pkg.environment.pathEntries) {
                $currentPath = [Environment]::GetEnvironmentVariable("PATH", $scope)
                foreach ($entry in $pkg.environment.pathEntries) {
                    $expandedEntry = [Environment]::ExpandEnvironmentVariables($entry)
                    if ($currentPath -notlike "*$expandedEntry*") {
                        $currentPath = "$currentPath;$expandedEntry"
                        Write-Host "  PATH追加: $expandedEntry"
                    }
                }
                [Environment]::SetEnvironmentVariable("PATH", $currentPath, $scope)
            }
        }

        Write-Host "[$($pkg.id)] インストール完了" -ForegroundColor Green

        $results += @{
            id = $pkg.id
            name = $pkg.name
            version = $pkg.version
            installedVersion = $pkg.version
            installPath = $pkg.install.path
            installedAt = (Get-Date -Format "o")
            status = "installed"
        }

    } catch {
        Write-Warning "[$($pkg.id)] インストール失敗: $_"
        $results += @{
            id = $pkg.id
            status = "failed"
            reason = $_.Exception.Message
        }
    }
}

# installed.json 更新
foreach ($result in $results) {
    $installed[$result.id] = $result
}

$installedOutput = @{
    "`$schema" = "./schemas/installed.schema.json"
    version = "1.0.0"
    generatedAt = (Get-Date -Format "o")
    machineId = $env:COMPUTERNAME
    userName = $env:USERNAME
    packages = @($installed.Values)
}

$installedOutput | ConvertTo-Json -Depth 10 | Set-Content -Path $InstalledFile -Encoding UTF8

# サマリー表示
Write-Host "`n=== インストールサマリー ===" -ForegroundColor Cyan
$results | ForEach-Object {
    $status = $_.status
    $color = if ($status -eq "installed") { "Green" } elseif ($status -eq "failed") { "Red" } else { "Yellow" }
    Write-Host "[$($_.id)] $status" -ForegroundColor $color
}
```

### Check-Installed.ps1

```powershell
#Requires -Version 5.1

[CmdletBinding()]
param (
    [string]$PackagesFile = ".\packages.json",
    [string]$InstalledFile = ".\installed.json"
)

$packagesJson = Get-Content -Path $PackagesFile -Raw | ConvertFrom-Json
$packages = $packagesJson.packages

$installed = @{}
if (Test-Path $InstalledFile) {
    $installedJson = Get-Content -Path $InstalledFile -Raw | ConvertFrom-Json
    foreach ($pkg in $installedJson.packages) {
        $installed[$pkg.id] = $pkg
    }
}

Write-Host "=== インストール状況 ===" -ForegroundColor Cyan

foreach ($pkg in $packages) {
    $status = "--"
    $actualVersion = "N/A"
    $color = "Gray"

    # コマンドでバージョン確認
    if ($pkg.verify -and $pkg.verify.command) {
        try {
            $output = & $pkg.verify.command $pkg.verify.args 2>&1 | Out-String
            if ($output -match $pkg.verify.versionPattern) {
                $actualVersion = $Matches[1]
            }
        } catch {
            $actualVersion = "コマンド失敗"
        }
    }

    # ステータス判定
    if ($installed.ContainsKey($pkg.id)) {
        $installedPkg = $installed[$pkg.id]
        if ($actualVersion -ne "N/A" -and $actualVersion -ne "コマンド失敗") {
            $expectedNorm = $pkg.version -replace "^v", ""
            $actualNorm = $actualVersion -replace "^v", ""

            if ($actualNorm -like "*$expectedNorm*" -or $expectedNorm -like "*$actualNorm*") {
                $status = "OK"
                $color = "Green"
            } else {
                $status = "!!"
                $color = "Yellow"
            }
        } else {
            $status = "OK"
            $color = "Green"
        }
    } else {
        $status = "--"
        $color = "Gray"
    }

    Write-Host "[$status] $($pkg.name.PadRight(25)) 期待: $($pkg.version.PadRight(10)) 実際: $actualVersion" -ForegroundColor $color
}
```

---

## 参考リンク

| トピック | URL |
|----------|-----|
| JSON Schema | https://json-schema.org/ |
| PowerShell JSON | https://learn.microsoft.com/ja-jp/powershell/module/microsoft.powershell.utility/convertfrom-json |
| セマンティックバージョニング | https://semver.org/lang/ja/ |
