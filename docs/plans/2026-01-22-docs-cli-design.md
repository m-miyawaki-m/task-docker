# docs-cli 設計ドキュメント

ドキュメント構造管理のためのRust製CLIツール

## 概要

- **目的**: ドキュメントの構造管理
- **機能**: カテゴリプレフィックス命名規則の適用、カテゴリ別リスト表示
- **言語**: Rust
- **アプローチ**: 設定ファイル駆動型

## CLIコマンド体系

```
docs-cli <COMMAND>

COMMANDS:
  list      カテゴリ別にドキュメント一覧を表示
  rename    命名規則に従ってファイルをリネーム
  check     命名規則違反のファイルを検出
  init      設定ファイル (docs-cli.toml) を生成
```

### 使用例

```bash
# 初期設定
$ docs-cli init
Created: docs-cli.toml

# カテゴリ別一覧表示
$ docs-cli list
[setup] (3 files)
  - setup-wsl-docker-offline.md
  - setup-chocolatey-offline.md
  - setup-scoop-offline.md

[reference] (2 files)
  - reference-docker-commands.md
  - reference-wsl-commands.md

[uncategorized] (1 file)
  - README.md

# 命名規則チェック
$ docs-cli check
⚠ docs/wsl-docker-offline-setup.md
  → カテゴリプレフィックスがありません
  提案: setup-wsl-docker-offline.md

# 一括リネーム (dry-run)
$ docs-cli rename --dry-run
Would rename: wsl-docker-offline-setup.md → setup-wsl-docker-offline.md

# 実行
$ docs-cli rename
Renamed: 5 files
```

## 設定ファイル

```toml
# docs-cli.toml

# 対象ディレクトリ
root = "docs"

# 対象ファイル拡張子
extensions = ["md"]

# カテゴリ定義
[categories]
setup = { keywords = ["setup", "install", "offline", "構築"] }
reference = { keywords = ["command", "overview", "概要", "コマンド"] }
guide = { keywords = ["guide", "tutorial", "ガイド"] }
comparison = { keywords = ["comparison", "比較", "vs"] }

# 命名規則
[naming]
# プレフィックス形式: {category}-{title}.md
pattern = "{category}-{title}"
# タイトル部分の変換ルール
transform = "kebab-case"  # スペース/アンダースコア → ハイフン

# 除外設定
[exclude]
files = ["README.md", "CHANGELOG.md"]
directories = ["drafts", "archive"]
```

### カテゴリ自動判定ロジック

1. ファイル名・ファイル内容から `keywords` を検索
2. マッチしたカテゴリを割り当て
3. 複数マッチ時は最初にマッチしたものを優先
4. マッチなしは `uncategorized`

## プロジェクト構成

```
docs-cli/
├── Cargo.toml
├── src/
│   ├── main.rs           # エントリーポイント、CLIパーサー
│   ├── config.rs         # 設定ファイル読み込み (toml)
│   ├── category.rs       # カテゴリ判定ロジック
│   ├── scanner.rs        # ファイルスキャン
│   ├── renamer.rs        # リネーム処理
│   └── commands/
│       ├── mod.rs
│       ├── list.rs       # list コマンド
│       ├── check.rs      # check コマンド
│       ├── rename.rs     # rename コマンド
│       └── init.rs       # init コマンド
```

### 主要な依存クレート

| クレート | 用途 |
|----------|------|
| `clap` | CLIパーサー (derive マクロ) |
| `toml` | 設定ファイル読み込み |
| `serde` | シリアライズ/デシリアライズ |
| `walkdir` | ディレクトリ再帰走査 |
| `colored` | ターミナル出力の色付け |

### 主要な型

```rust
struct Config {
    root: PathBuf,
    extensions: Vec<String>,
    categories: HashMap<String, Category>,
    naming: NamingRule,
    exclude: ExcludeRule,
}

struct Category {
    keywords: Vec<String>,
}

struct Document {
    path: PathBuf,
    category: Option<String>,
    suggested_name: Option<String>,
}
```

## エラー処理

| ケース | 動作 |
|--------|------|
| 設定ファイルなし | `docs-cli init` を促すメッセージ表示 |
| 対象ディレクトリなし | エラー終了 (exit code 1) |
| リネーム先が既存 | スキップして警告表示、続行 |
| 権限エラー | ファイル単位でスキップ、最後にサマリ表示 |

## 出力形式

```bash
# list: カラー付きカテゴリ表示
$ docs-cli list
[setup] (3 files)
  setup-wsl-docker-offline.md
  setup-chocolatey-offline.md
  setup-scoop-offline.md

[reference] (2 files)
  reference-docker-commands.md
  reference-wsl-commands.md

# check: 警告表示
$ docs-cli check
⚠ wsl-docker-offline-setup.md
  現在: (カテゴリなし)
  提案: setup-wsl-docker-offline.md

✓ 5 files OK, 3 files need attention

# rename: 実行結果
$ docs-cli rename
✓ wsl-docker-offline-setup.md → setup-wsl-docker-offline.md
✓ tool-urls.md → reference-tool-urls.md
⚠ skipped: setup-docker.md (already exists)

Renamed: 2 files, Skipped: 1 file
```

## 終了コード

| コード | 意味 |
|--------|------|
| 0 | 正常終了 |
| 1 | エラー (設定不正、ディレクトリなし等) |
| 2 | 警告あり (check で違反検出時) |
