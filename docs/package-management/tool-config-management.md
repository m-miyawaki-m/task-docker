# ツール別 設定ファイル管理比較

各開発ツールの設定ファイルについて、パッケージマネージャー（winget/Chocolatey/Scoop）と自作スクリプトでの管理可否を比較する。

## 比較サマリー

| ツール | 主な設定ファイル | winget | Choco | Scoop | 自作 |
|--------|-----------------|:------:|:-----:|:-----:|:----:|
| Eclipse | eclipse.ini, formatter, preferences | × | × | × | ◎ |
| SQLDeveloper | connections.json, preferences | × | × | × | ◎ |
| JDK | - (環境変数のみ) | △ | △ | ◎ | ◎ |
| Git | .gitconfig | × | × | × | ◎ |
| Maven | settings.xml | × | × | × | ◎ |
| Gradle | gradle.properties, init.gradle | × | × | × | ◎ |
| VS Code | settings.json, extensions | × | × | × | ◎ |
| IntelliJ IDEA | idea.properties, codestyles | × | × | × | ◎ |
| Node.js | .npmrc | × | × | × | ◎ |
| Docker | daemon.json, config.json | × | × | × | ◎ |

**凡例:** ◎=完全対応 / △=部分対応 / ×=非対応

---

## ツール別 詳細比較

### 1. Eclipse

#### 設定ファイル一覧

| ファイル | 場所 | 用途 |
|----------|------|------|
| `eclipse.ini` | `%ECLIPSE_HOME%/eclipse.ini` | JVM設定、メモリ、プラグイン |
| `formatter.xml` | ワークスペース or エクスポート | コードフォーマッター |
| `*.epf` | エクスポートファイル | 全般設定（Preferences） |
| `dropins/` | `%ECLIPSE_HOME%/dropins/` | オフラインプラグイン |

#### 管理方式比較

| 項目 | winget | Chocolatey | Scoop | 自作スクリプト |
|------|--------|------------|-------|----------------|
| インストール | ◎ | ◎ | ◎ | ◎ |
| eclipse.ini 編集 | × | × | × | ◎ (patch) |
| formatter 配置 | × | × | × | ◎ (copy) |
| プラグイン配置 | × | × | × | ◎ (copy_folder) |
| ワークスペース設定 | × | × | × | ◎ (copy) |

#### 自作スクリプトでの設定例

```csv
# configs.csv
tool,config_name,source,destination,action,backup,description
eclipse,ini_patch,configs/eclipse/eclipse.ini.patch,%ECLIPSE_HOME%/eclipse.ini,patch,true,JVMメモリ設定
eclipse,formatter,configs/eclipse/formatter.xml,%ECLIPSE_HOME%/formatter.xml,copy,false,コードフォーマッター
eclipse,plugins,configs/eclipse/plugins,%ECLIPSE_HOME%/dropins,copy_folder,false,オフラインプラグイン
eclipse,preferences,configs/eclipse/project.epf,%USERPROFILE%/.eclipse/project.epf,copy,true,環境設定
```

---

### 2. Oracle SQLDeveloper

#### 設定ファイル一覧

| ファイル | 場所 | 用途 |
|----------|------|------|
| `connections.json` | `%APPDATA%/SQL Developer/system*/o.jdeveloper.db.connection/` | DB接続情報 |
| `ide-preferences.xml` | `%APPDATA%/SQL Developer/system*/o.ide/` | IDE設定 |
| `format.xml` | `%APPDATA%/SQL Developer/system*/o.sqldeveloper/` | SQLフォーマッター |
| `snippets/` | `%APPDATA%/SQL Developer/UserSnippets/` | コードスニペット |

#### 管理方式比較

| 項目 | winget | Chocolatey | Scoop | 自作スクリプト |
|------|--------|------------|-------|----------------|
| インストール | △※ | ◎ | × | ◎ |
| DB接続情報 | × | × | × | ◎ (copy) |
| IDE設定 | × | × | × | ◎ (copy) |
| フォーマッター | × | × | × | ◎ (copy) |
| スニペット | × | × | × | ◎ (copy_folder) |

※ winget: SQLDeveloper のパッケージなし（2024年時点）

#### 自作スクリプトでの設定例

```csv
# configs.csv
tool,config_name,source,destination,action,backup,description
sqldeveloper,connections,configs/sqldeveloper/connections.json,%APPDATA%/SQL Developer/system*/o.jdeveloper.db.connection/connections.json,copy,true,DB接続情報
sqldeveloper,format,configs/sqldeveloper/format.xml,%APPDATA%/SQL Developer/system*/o.sqldeveloper/format.xml,copy,true,SQLフォーマッター
sqldeveloper,snippets,configs/sqldeveloper/snippets,%APPDATA%/SQL Developer/UserSnippets,copy_folder,false,コードスニペット
```

#### 注意事項

- `system*` はバージョンにより `system23.1.0.0` 等になる
- 接続情報にはパスワードが含まれる可能性あり → 暗号化 or 除外を検討

---

### 3. JDK (OpenJDK / Oracle JDK)

#### 設定ファイル一覧

| 項目 | 場所 | 用途 |
|------|------|------|
| `JAVA_HOME` | 環境変数 | JDKインストール先 |
| `PATH` | 環境変数 | java/javac コマンドパス |
| `java.security` | `%JAVA_HOME%/conf/security/` | セキュリティ設定 |
| `cacerts` | `%JAVA_HOME%/lib/security/` | 証明書ストア |

#### 管理方式比較

| 項目 | winget | Chocolatey | Scoop | 自作スクリプト |
|------|--------|------------|-------|----------------|
| インストール | ◎ | ◎ | ◎ | ◎ |
| JAVA_HOME 設定 | × | △ | ◎ | ◎ |
| PATH 追加 | × | △ | ◎ | ◎ |
| 証明書追加 | × | × | × | ◎ |
| security設定 | × | × | × | ◎ (patch) |

#### 自作スクリプトでの設定例

```csv
# packages.csv
name,version,source,type,install_path,env_var,add_to_path
openjdk,21.0.2,packages/openjdk-21.0.2.zip,zip,C:\dev-tools\jdk-21,JAVA_HOME,%JAVA_HOME%\bin

# configs.csv（証明書追加が必要な場合）
tool,config_name,source,destination,action,backup,description
jdk,cacerts,configs/jdk/custom-cacerts,%JAVA_HOME%/lib/security/cacerts,copy,true,社内CA証明書追加済み
```

#### 社内CA証明書の追加

```powershell
# 証明書追加コマンド（参考）
keytool -importcert -trustcacerts -keystore "%JAVA_HOME%\lib\security\cacerts" `
    -storepass changeit -alias company-ca -file company-ca.crt -noprompt
```

---

### 4. Git

#### 設定ファイル一覧

| ファイル | 場所 | 用途 |
|----------|------|------|
| `.gitconfig` | `%USERPROFILE%/.gitconfig` | ユーザー設定（グローバル） |
| `.gitattributes` | プロジェクトルート | ファイル属性 |
| `.gitignore_global` | `%USERPROFILE%/.gitignore_global` | グローバル除外設定 |

#### 管理方式比較

| 項目 | winget | Chocolatey | Scoop | 自作スクリプト |
|------|--------|------------|-------|----------------|
| インストール | ◎ | ◎ | ◎ | ◎ |
| .gitconfig | × | × | × | ◎ (merge) |
| .gitignore_global | × | × | × | ◎ (copy) |
| user.name/email | × | × | × | ◎ |

#### 自作スクリプトでの設定例

```csv
# configs.csv
tool,config_name,source,destination,action,backup,description
git,gitconfig,configs/git/.gitconfig,%USERPROFILE%/.gitconfig,merge,true,Git設定（プロキシ等）
git,gitignore,configs/git/.gitignore_global,%USERPROFILE%/.gitignore_global,copy,false,グローバル除外
```

#### 設定ファイル例（.gitconfig）

```ini
[user]
    name = Your Name
    email = your.name@company.com

[http]
    proxy = http://proxy.company.com:8080

[https]
    proxy = http://proxy.company.com:8080

[core]
    autocrlf = true
    excludesfile = ~/.gitignore_global

[credential]
    helper = manager-core
```

---

### 5. Maven

#### 設定ファイル一覧

| ファイル | 場所 | 用途 |
|----------|------|------|
| `settings.xml` | `%USERPROFILE%/.m2/settings.xml` | リポジトリ、プロキシ、認証 |
| `settings-security.xml` | `%USERPROFILE%/.m2/settings-security.xml` | 暗号化マスターパスワード |
| `toolchains.xml` | `%USERPROFILE%/.m2/toolchains.xml` | JDKツールチェーン |

#### 管理方式比較

| 項目 | winget | Chocolatey | Scoop | 自作スクリプト |
|------|--------|------------|-------|----------------|
| インストール | × | ◎ | ◎ | ◎ |
| settings.xml | × | × | × | ◎ (copy) |
| プロキシ設定 | × | × | × | ◎ |
| 社内リポジトリ | × | × | × | ◎ |
| 認証情報 | × | × | × | ◎ |

#### 自作スクリプトでの設定例

```csv
# configs.csv
tool,config_name,source,destination,action,backup,description
maven,settings,configs/maven/settings.xml,%USERPROFILE%/.m2/settings.xml,copy,true,Nexus/プロキシ設定
maven,toolchains,configs/maven/toolchains.xml,%USERPROFILE%/.m2/toolchains.xml,copy,true,JDKツールチェーン
```

#### 設定ファイル例（settings.xml）

```xml
<settings>
  <proxies>
    <proxy>
      <id>company-proxy</id>
      <active>true</active>
      <protocol>http</protocol>
      <host>proxy.company.com</host>
      <port>8080</port>
    </proxy>
  </proxies>

  <mirrors>
    <mirror>
      <id>nexus</id>
      <mirrorOf>*</mirrorOf>
      <url>http://nexus.company.com/repository/maven-public/</url>
    </mirror>
  </mirrors>
</settings>
```

---

### 6. Gradle

#### 設定ファイル一覧

| ファイル | 場所 | 用途 |
|----------|------|------|
| `gradle.properties` | `%USERPROFILE%/.gradle/gradle.properties` | プロキシ、メモリ設定 |
| `init.gradle` | `%USERPROFILE%/.gradle/init.gradle` | グローバル初期化スクリプト |

#### 管理方式比較

| 項目 | winget | Chocolatey | Scoop | 自作スクリプト |
|------|--------|------------|-------|----------------|
| インストール | × | ◎ | ◎ | ◎ |
| gradle.properties | × | × | × | ◎ (copy) |
| init.gradle | × | × | × | ◎ (copy) |
| プロキシ設定 | × | × | × | ◎ |

#### 自作スクリプトでの設定例

```csv
# configs.csv
tool,config_name,source,destination,action,backup,description
gradle,properties,configs/gradle/gradle.properties,%USERPROFILE%/.gradle/gradle.properties,copy,true,プロキシ・メモリ設定
gradle,init,configs/gradle/init.gradle,%USERPROFILE%/.gradle/init.gradle,copy,true,社内リポジトリ設定
```

#### 設定ファイル例（gradle.properties）

```properties
# プロキシ設定
systemProp.http.proxyHost=proxy.company.com
systemProp.http.proxyPort=8080
systemProp.https.proxyHost=proxy.company.com
systemProp.https.proxyPort=8080

# メモリ設定
org.gradle.jvmargs=-Xmx2048m -XX:+HeapDumpOnOutOfMemoryError

# 並列ビルド
org.gradle.parallel=true
```

---

### 7. VS Code

#### 設定ファイル一覧

| ファイル | 場所 | 用途 |
|----------|------|------|
| `settings.json` | `%APPDATA%/Code/User/settings.json` | ユーザー設定 |
| `keybindings.json` | `%APPDATA%/Code/User/keybindings.json` | キーバインド |
| `extensions/` | `%USERPROFILE%/.vscode/extensions/` | 拡張機能 |
| `snippets/` | `%APPDATA%/Code/User/snippets/` | コードスニペット |

#### 管理方式比較

| 項目 | winget | Chocolatey | Scoop | 自作スクリプト |
|------|--------|------------|-------|----------------|
| インストール | ◎ | ◎ | ◎ | ◎ |
| settings.json | × | × | × | ◎ (merge) |
| keybindings.json | × | × | × | ◎ (copy) |
| 拡張機能（オフライン） | × | × | × | ◎ (copy_folder) |
| スニペット | × | × | × | ◎ (copy_folder) |

#### 自作スクリプトでの設定例

```csv
# configs.csv
tool,config_name,source,destination,action,backup,description
vscode,settings,configs/vscode/settings.json,%APPDATA%/Code/User/settings.json,merge,true,エディタ設定
vscode,keybindings,configs/vscode/keybindings.json,%APPDATA%/Code/User/keybindings.json,copy,true,キーバインド
vscode,extensions,configs/vscode/extensions,%USERPROFILE%/.vscode/extensions,copy_folder,false,オフライン拡張機能
vscode,snippets,configs/vscode/snippets,%APPDATA%/Code/User/snippets,copy_folder,false,コードスニペット
```

---

### 8. IntelliJ IDEA

#### 設定ファイル一覧

| ファイル | 場所 | 用途 |
|----------|------|------|
| `idea.properties` | `%IDEA_HOME%/bin/idea.properties` | システムプロパティ |
| `idea64.exe.vmoptions` | `%IDEA_HOME%/bin/idea64.exe.vmoptions` | JVMオプション |
| `codestyles/` | `%APPDATA%/JetBrains/IntelliJIdea*/codestyles/` | コードスタイル |
| `options/` | `%APPDATA%/JetBrains/IntelliJIdea*/options/` | IDE設定 |

#### 管理方式比較

| 項目 | winget | Chocolatey | Scoop | 自作スクリプト |
|------|--------|------------|-------|----------------|
| インストール | ◎ | ◎ | ◎ | ◎ |
| vmoptions | × | × | × | ◎ (patch) |
| codestyles | × | × | × | ◎ (copy_folder) |
| プラグイン（オフライン） | × | × | × | ◎ (copy_folder) |

#### 自作スクリプトでの設定例

```csv
# configs.csv
tool,config_name,source,destination,action,backup,description
idea,vmoptions,configs/idea/idea64.exe.vmoptions,%IDEA_HOME%/bin/idea64.exe.vmoptions,copy,true,JVMメモリ設定
idea,codestyles,configs/idea/codestyles,%APPDATA%/JetBrains/IntelliJIdea*/codestyles,copy_folder,true,コードスタイル
idea,plugins,configs/idea/plugins,%USERPROFILE%/.IntelliJIdea*/config/plugins,copy_folder,false,オフラインプラグイン
```

---

### 9. Node.js / npm

#### 設定ファイル一覧

| ファイル | 場所 | 用途 |
|----------|------|------|
| `.npmrc` | `%USERPROFILE%/.npmrc` | npm設定（レジストリ、プロキシ） |
| `.nvmrc` | プロジェクトルート | Node.jsバージョン指定 |

#### 管理方式比較

| 項目 | winget | Chocolatey | Scoop | 自作スクリプト |
|------|--------|------------|-------|----------------|
| インストール | ◎ | ◎ | ◎ | ◎ |
| .npmrc | × | × | × | ◎ (copy) |
| 社内レジストリ | × | × | × | ◎ |
| プロキシ設定 | × | × | × | ◎ |

#### 自作スクリプトでの設定例

```csv
# configs.csv
tool,config_name,source,destination,action,backup,description
nodejs,npmrc,configs/nodejs/.npmrc,%USERPROFILE%/.npmrc,copy,true,npm設定（プロキシ・レジストリ）
```

#### 設定ファイル例（.npmrc）

```ini
registry=http://nexus.company.com/repository/npm-public/
proxy=http://proxy.company.com:8080/
https-proxy=http://proxy.company.com:8080/
strict-ssl=false
```

---

### 10. Docker

#### 設定ファイル一覧

| ファイル | 場所 | 用途 |
|----------|------|------|
| `daemon.json` | `C:\ProgramData\docker\config\daemon.json` | Docker Engine設定 |
| `config.json` | `%USERPROFILE%/.docker/config.json` | CLI設定（認証情報等） |

#### 管理方式比較

| 項目 | winget | Chocolatey | Scoop | 自作スクリプト |
|------|--------|------------|-------|----------------|
| インストール | ◎ | ◎ | × | ◎ |
| daemon.json | × | × | × | ◎ (merge) |
| config.json | × | × | × | ◎ (merge) |
| プロキシ設定 | × | × | × | ◎ |
| 社内レジストリ | × | × | × | ◎ |

#### 自作スクリプトでの設定例

```csv
# configs.csv
tool,config_name,source,destination,action,backup,description
docker,daemon,configs/docker/daemon.json,C:\ProgramData\docker\config\daemon.json,merge,true,Docker Engine設定
docker,config,configs/docker/config.json,%USERPROFILE%/.docker/config.json,merge,true,CLI設定
```

#### 設定ファイル例（daemon.json）

```json
{
  "insecure-registries": ["registry.company.com:5000"],
  "registry-mirrors": ["http://registry.company.com:5000"]
}
```

---

## 総合比較表

| ツール | 設定ファイル数 | パッケージマネージャー対応 | 自作スクリプト対応 | 設定の複雑さ |
|--------|---------------|--------------------------|-------------------|-------------|
| Eclipse | 4+ | × | ◎ | 高 |
| SQLDeveloper | 4+ | × | ◎ | 高 |
| JDK | 2 | △（環境変数のみ） | ◎ | 低 |
| Git | 2 | × | ◎ | 低 |
| Maven | 3 | × | ◎ | 中 |
| Gradle | 2 | × | ◎ | 中 |
| VS Code | 4+ | × | ◎ | 中 |
| IntelliJ IDEA | 4+ | × | ◎ | 高 |
| Node.js | 1 | × | ◎ | 低 |
| Docker | 2 | × | ◎ | 中 |

---

## 結論

### パッケージマネージャーの限界

- **インストールのみ対応** - 設定ファイルの配置・編集は非対応
- **環境変数設定** - Scoop 以外は基本非対応
- **オフラインプラグイン** - 全て非対応

### 自作スクリプトの優位性

1. **全ツールの設定に対応** - copy / patch / merge で柔軟に対応
2. **環境変数の完全制御** - JAVA_HOME、PATH 等を確実に設定
3. **バックアップ機能** - 既存設定を保護
4. **オフラインプラグイン** - Eclipse、VS Code、IntelliJ 等のプラグインも配置可能

### 推奨アプローチ

```
オフライン環境 + 設定管理 = 自作スクリプト（CSV + PowerShell）一択
```

パッケージマネージャーは「インストール」に特化しており、企業環境で必要な「設定の統一」には対応できない。
