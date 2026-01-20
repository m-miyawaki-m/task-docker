# Windowsパッケージ管理ガイド

## 概要

オフライン環境でWindowsの開発ツールを共有フォルダから配布・管理する方法をまとめたドキュメント集です。

---

## ドキュメント一覧

| ファイル | 内容 |
|----------|------|
| [offline-package-distribution.md](offline-package-distribution.md) | オフラインパッケージ配布の概要・検討事項 |
| [csv-script-setup.md](csv-script-setup.md) | **CSV + スクリプト方式（推奨）** |
| [chocolatey-offline-setup.md](chocolatey-offline-setup.md) | Chocolateyによるオフラインセットアップ |
| [scoop-offline-setup.md](scoop-offline-setup.md) | Scoopによるオフラインセットアップ |
| [winget-offline-setup.md](winget-offline-setup.md) | wingetによるセットアップ（制限あり） |
| [manual-script-setup.md](manual-script-setup.md) | 手動スクリプトによるセットアップ |

---

## クイック選択ガイド

### 条件別推奨

| 条件 | 推奨 | ドキュメント |
|------|------|--------------|
| **オフライン + 開発ツール配布** | **CSV + スクリプト** | [csv-script-setup.md](csv-script-setup.md) |
| 管理者権限あり + 複雑な依存 | Chocolatey | [chocolatey-offline-setup.md](chocolatey-offline-setup.md) |
| 管理者権限なし | Scoop | [scoop-offline-setup.md](scoop-offline-setup.md) |
| オンライン接続あり | winget | [winget-offline-setup.md](winget-offline-setup.md) |

### オフライン環境での推奨理由

**CSV + スクリプト方式が最適な理由：**

| 項目 | パッケージマネージャー | CSV + スクリプト |
|------|------------------------|------------------|
| 事前準備 | 多い（nupkg化等） | **少ない（ZIP配置のみ）** |
| 依存関係 | 本体インストール必要 | **なし** |
| トラブル時 | ブラックボックス | **透明** |
| バージョン管理 | 専用形式 | **CSV（Excel編集可）** |

パッケージマネージャーのメリット（依存解決、アップデート検知）は**オンライン前提**の機能であり、オフライン環境ではオーバーヘッドになります。

### 判断フロー

```
完全オフライン環境？
  │
  ├─ Yes ──→ 管理者権限あり？
  │            │
  │            ├─ Yes ──→ Chocolatey or 手動スクリプト
  │            │
  │            └─ No ───→ Scoop or 手動スクリプト
  │
  └─ No ───→ winget（Windows 11推奨）
```

---

## パッケージマネージャー比較表

| 項目 | Chocolatey | Scoop | winget | 手動 |
|------|------------|-------|--------|------|
| オフライン対応 | ◎ | ○ | △ | ◎ |
| 管理者権限 | 必要 | 不要 | 不要 | 設定次第 |
| バージョン固定 | ◎ | ◎ | △ | ◎ |
| 定義ファイル | XML | JSON | JSON/YAML | 自由 |
| 依存解決 | ◎ | ○ | ◎ | なし |
| 学習コスト | 中 | 低 | 低 | 低 |
| 企業利用 | ◎ | ○ | ○ | ◎ |

---

## 共有フォルダ構成例

### Chocolatey

```
\\fileserver\dev-tools\
├── chocolatey\
│   ├── install\
│   │   └── chocolatey.nupkg
│   └── packages\
│       └── *.nupkg
├── packages.config
└── setup-chocolatey.ps1
```

### Scoop

```
\\fileserver\dev-tools\
├── scoop\
│   ├── install\
│   │   └── scoop-master.zip
│   ├── buckets\
│   │   └── *.zip
│   └── cache\
│       └── *.zip
├── apps.json
└── setup-scoop.ps1
```

### 手動スクリプト

```
\\fileserver\dev-tools\
├── packages\
│   ├── java\
│   │   └── *.zip
│   ├── gradle\
│   │   └── *.zip
│   └── node\
│       └── *.zip
├── versions.json
└── setup-dev-env.ps1
```

---

## 定義ファイル形式

### XML（Chocolatey packages.config）

```xml
<?xml version="1.0" encoding="utf-8"?>
<packages>
  <package id="openjdk11" version="11.0.21" />
  <package id="gradle" version="7.6.1" />
  <package id="nodejs-lts" version="18.19.0" />
</packages>
```

### JSON（Scoop apps.json / winget）

```json
{
  "apps": [
    { "name": "openjdk11", "bucket": "java" },
    { "name": "gradle", "bucket": "main" },
    { "name": "nodejs-lts", "bucket": "main" }
  ]
}
```

### YAML（winget configuration）

```yaml
properties:
  configurationVersion: 0.2.0
  resources:
    - resource: Microsoft.WinGet.DSC/WinGetPackage
      settings:
        id: Microsoft.OpenJDK.11
```

---

## 運用フロー

### 初回構築（管理者）

1. オンライン環境でパッケージを取得
2. 共有フォルダに配置
3. 定義ファイル・セットアップスクリプト作成
4. versions.json作成

### 開発者セットアップ

1. 共有フォルダのセットアップスクリプト実行
2. ターミナル再起動
3. バージョン確認

### パッケージ更新（管理者）

1. 新バージョンをダウンロード
2. 共有フォルダに配置
3. versions.json更新
4. 開発者に通知

### 開発者の更新適用

1. セットアップスクリプト再実行
2. または更新スクリプト実行

---

## 関連ドキュメント

- [WSL2 + Docker 概要](../wsl2-docker-overview.md)
- [WSL2 + Docker オフライン環境構築ガイド](../wsl-docker-offline-setup.md)
- [Dockerfile運用ガイド](../dockerfile-operation.md)
