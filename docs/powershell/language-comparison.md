# 言語・ツール比較ガイド

PowerShell / .NET / Python 等の使い分けガイド。

## PowerShell が適している分野

### Windows システム管理・自動化

| 用途 | 理由 |
|------|------|
| Windows システム管理 | OS標準搭載、追加インストール不要 |
| Active Directory 管理 | AD用コマンドレットが豊富 |
| レジストリ操作 | 標準でサポート |
| サービス管理 | Get-Service, Start-Service 等 |
| タスクスケジューラ連携 | ScheduledTasks モジュール |
| イベントログ管理 | Get-EventLog, Get-WinEvent |

### Microsoft 製品管理

| 製品 | PowerShell モジュール |
|------|----------------------|
| Exchange Server | Exchange Management Shell |
| SharePoint | SharePoint Online Management Shell |
| Microsoft 365 | Microsoft.Graph, ExchangeOnlineManagement |
| Azure | Az モジュール |
| SQL Server | SqlServer モジュール |
| Hyper-V | Hyper-V モジュール |

### 社内ツール配布

```
メリット:
  ✓ Windows 標準搭載（追加インストール不要）
  ✓ .ps1 ファイルをそのまま配布可能
  ✓ オフライン環境でも動作
  ✓ グループポリシーで配布可能
```

---

## .NET (C#) が適している分野

| 分野 | 理由 |
|------|------|
| Windows デスクトップアプリ | WPF, WinForms, MAUI |
| ゲーム開発 | Unity（C#がメイン言語） |
| 企業向け Web API | ASP.NET Core（高性能） |
| Azure 連携 | Azure SDK が最も充実 |
| 高パフォーマンス処理 | JIT コンパイル、ネイティブ並みの速度 |
| C# コード解析 | Roslyn（公式、最強） |

---

## Python が適している分野

| 分野 | 理由・ライブラリ |
|------|-----------------|
| データ分析 | pandas, numpy |
| 機械学習・AI | scikit-learn, PyTorch, TensorFlow |
| コード解析・AST操作 | tree-sitter, esprima, javalang |
| Web スクレイピング | requests, BeautifulSoup, Selenium |
| 自然言語処理 | spaCy, NLTK, transformers |
| 画像処理 | Pillow, OpenCV |
| 科学計算 | scipy, matplotlib |
| 自動化スクリプト | クロスプラットフォーム |

---

## 言語・ツール選択ガイド

| やりたいこと | 推奨 | 理由 |
|-------------|------|------|
| Windows 管理・自動化 | **PowerShell** | OS標準、管理コマンド豊富 |
| 社内パッケージ管理 | **PowerShell** | 追加インストール不要 |
| 環境変数の永続設定 | **PowerShell** | `[Environment]` クラス |
| データ分析・機械学習 | **Python** | pandas, scikit-learn 等 |
| コード解析（JS/Java） | **Python** | tree-sitter, esprima 等 |
| コード解析（C#） | **.NET (Roslyn)** | 公式パーサー、最強 |
| Web スクレイピング | **Python** | requests, BeautifulSoup |
| CLI ツール作成 | **Go / Rust** | シングルバイナリ、高速 |
| Web フロントエンド | **JavaScript/TypeScript** | 唯一の選択肢 |
| Web バックエンド | 言語問わず | Node.js, Python, Go, C# 等 |
| Windows デスクトップ | **C# (.NET)** | WPF, WinForms |
| クロスプラットフォーム GUI | **Electron / Flutter** | 広く普及 |
| 高性能サーバー | **Go / Rust / C#** | 同時接続、低レイテンシ |
| インフラ自動化 | **Ansible / Terraform** | 宣言的、冪等性 |
| Linux サーバー管理 | **Bash / Python** | 標準的 |

---

## スクリプト言語比較

### PowerShell vs Python vs Bash

| 観点 | PowerShell | Python | Bash |
|------|------------|--------|------|
| Windows 管理 | **◎** | △ | × |
| Linux 管理 | △ | ◎ | **◎** |
| macOS 管理 | △ | ◎ | ◎ |
| データ処理 | △ | **◎** | × |
| ライブラリ数 | 少ない | **非常に多い** | 少ない |
| 学習コスト | 中 | 低 | 低 |
| Windows 標準 | **あり** | なし | なし |
| Linux 標準 | なし | 多くの場合あり | **あり** |
| オブジェクト指向 | **◎** | ◎ | × |
| パイプライン | オブジェクト | - | テキスト |
| 型システム | 動的（.NET型利用可） | 動的 | なし |

### 詳細比較

#### Windows 管理

```powershell
# PowerShell - 自然に書ける
Get-Service | Where-Object { $_.Status -eq "Running" }
Get-Process | Sort-Object CPU -Descending | Select-Object -First 10
Get-ChildItem -Recurse | Where-Object { $_.Length -gt 1MB }
```

```python
# Python - subprocess や pywin32 が必要
import subprocess
result = subprocess.run(["sc", "query"], capture_output=True, text=True)
# パースが面倒
```

#### データ処理

```python
# Python - 自然に書ける
import pandas as pd
df = pd.read_csv("data.csv")
df.groupby("category").mean()
df[df["value"] > 100].to_csv("filtered.csv")
```

```powershell
# PowerShell - 可能だが pandas ほど便利ではない
$data = Import-Csv "data.csv"
$data | Group-Object category | ForEach-Object {
    # 集計処理を自分で書く必要あり
}
```

---

## コード解析の言語比較

| 解析対象 | 推奨ツール | 理由 |
|----------|-----------|------|
| JavaScript | Python + tree-sitter / esprima | ライブラリ充実 |
| TypeScript | Python + tree-sitter | 多言語対応 |
| Java | Python + javalang / tree-sitter | ライブラリ充実 |
| C# | **.NET + Roslyn** | 公式、完全なAST |
| Python | Python + ast モジュール | 標準ライブラリ |
| Go | Go + go/ast | 標準ライブラリ |
| 複数言語 | Python + tree-sitter | 40+言語対応 |

### PowerShell での簡易コード解析

```powershell
# 正規表現による簡易的な関数抽出（限界あり）
$code = Get-Content "app.js" -Raw

# JavaScript function 抽出
$pattern = 'function\s+(\w+)\s*\([^)]*\)'
[regex]::Matches($code, $pattern) | ForEach-Object {
    $_.Groups[1].Value
}

# 出力例: myFunction, handleClick, ...
```

**限界:**
- ネスト構造に対応できない
- コメント内・文字列内の誤検出
- アロー関数、クラスメソッド等に非対応

**結論:** 本格的なコード解析には Python + tree-sitter が適切

---

## パッケージ管理ツールに PowerShell が適している理由

今回のオフライン開発環境パッケージ管理ツールの要件:

| 要件 | PowerShell の対応 |
|------|------------------|
| Windows 標準搭載 | ◎ 追加インストール不要 |
| オフライン環境 | ◎ 外部依存なし |
| 環境変数の永続化 | ◎ `[Environment]` クラス |
| ZIP展開 | ◎ `Expand-Archive` |
| MSI/EXE実行 | ◎ `Start-Process` |
| JSON読み書き | ◎ `ConvertFrom-Json` |
| ハッシュ検証 | ◎ `Get-FileHash` |
| レジストリ確認 | ◎ `Get-ItemProperty` |
| 社内配布 | ◎ .ps1 ファイル配布 |

```
結論: パッケージ管理ツールは PowerShell が最適
```

---

## 使い分けのまとめ

```
┌─────────────────────────────────────────────────────────┐
│                    使い分け指針                          │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Windows 管理・自動化・社内ツール                        │
│    → PowerShell                                        │
│                                                         │
│  データ分析・機械学習・コード解析                        │
│    → Python                                            │
│                                                         │
│  Windows デスクトップアプリ                              │
│    → C# (.NET)                                         │
│                                                         │
│  高性能 CLI ツール                                      │
│    → Go / Rust                                         │
│                                                         │
│  Web 開発                                               │
│    → JavaScript/TypeScript (フロント)                  │
│    → Node.js / Python / Go / C# (バック)               │
│                                                         │
│  Linux サーバー管理                                     │
│    → Bash / Python                                     │
│                                                         │
└─────────────────────────────────────────────────────────┘

複数の言語を使い分けるのが現実的。
一つの言語で全てをカバーしようとしない。
```

---

## 参考リンク

### PowerShell

- [Microsoft Learn - PowerShell](https://learn.microsoft.com/ja-jp/powershell/)
- [PowerShell Gallery](https://www.powershellgallery.com/)

### .NET / C#

- [Microsoft Learn - .NET](https://learn.microsoft.com/ja-jp/dotnet/)
- [Roslyn (C# コンパイラ)](https://github.com/dotnet/roslyn)

### Python

- [Python 公式](https://www.python.org/)
- [tree-sitter](https://tree-sitter.github.io/tree-sitter/)
- [pandas](https://pandas.pydata.org/)

### その他

- [Go 公式](https://go.dev/)
- [Rust 公式](https://www.rust-lang.org/)
