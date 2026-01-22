# Java クラス解析ツール

Pythonとjavalangを使用して、Javaクラス内のインスタンス生成とメソッド呼び出しを解析するツールです。

## 機能

- クラス内で使用しているインスタンス（フィールド・ローカル変数）の一覧化
- メソッド呼び出しの一覧化
- CSV形式での出力

## 取得できる情報

### インスタンス一覧
| 項目 | 説明 |
|------|------|
| クラス名 | インスタンス化されるクラス（型） |
| 変数名 | インスタンス変数名/ローカル変数名 |
| スコープ | `field`（フィールド）/ `local`（ローカル変数） |
| 行番号 | 宣言されている行番号 |

### メソッド呼び出し一覧
| 項目 | 説明 |
|------|------|
| インスタンス名 | メソッドを呼び出しているインスタンス |
| メソッド名 | 呼び出されているメソッド名 |
| 行番号 | 呼び出している行番号 |

## セットアップ

```bash
# リポジトリのディレクトリに移動
cd /home/m-miyawaki/dev/task-docker/java_analyzer

# 仮想環境の作成（初回のみ）
python3 -m venv venv

# 仮想環境の有効化
source venv/bin/activate

# 依存パッケージのインストール（初回のみ）
pip install javalang
```

## 使い方

### 基本的な使い方

```bash
# 仮想環境を有効化
source venv/bin/activate

# サンプルファイルを解析
python analyze_java.py

# 特定のJavaファイルを解析
python analyze_java.py /path/to/YourClass.java

# CSV出力付きで解析
python analyze_java.py /path/to/YourClass.java --csv
```

### 出力例

```
============================================================
クラス: SampleClass
============================================================

【インスタンス一覧】
クラス名                           変数名                  スコープ       行番号
----------------------------------------------------------------------
UserService                    userService          field      9
OrderRepository                orderRepository      field      10
List<String> (impl: ArrayList) names                field      11
Order                          order                local      18
ValidationHelper               validator            local      21

【メソッド呼び出し一覧】
インスタンス名              メソッド名                          行番号
------------------------------------------------------------
orderRepository      findById                       18
userService          getCurrentUser                 19
validator            validate                       22
```

### CSV出力

`--csv`オプションを付けると、以下のファイルが生成されます：

- `{クラス名}_instances.csv` - インスタンス一覧
- `{クラス名}_method_calls.csv` - メソッド呼び出し一覧

## Pythonからの利用

```python
from analyze_java import analyze_java_file, analyze_java_source, print_results, export_to_csv

# ファイルから解析
results = analyze_java_file("/path/to/YourClass.java")

# ソースコード文字列から解析
source_code = """
public class Example {
    private MyService service = new MyService();
    public void run() {
        service.execute();
    }
}
"""
results = analyze_java_source(source_code)

# 結果を表示
print_results(results)

# CSVに出力
export_to_csv(results, output_dir="./output")

# 結果をプログラムで利用
for result in results:
    print(f"クラス: {result.class_name}")
    for inst in result.instances:
        print(f"  インスタンス: {inst.class_name} {inst.variable_name}")
    for call in result.method_calls:
        print(f"  呼び出し: {call.instance_name}.{call.method_name}()")
```

## ファイル構成

```
java_analyzer/
├── README.md           # このファイル
├── analyze_java.py     # 解析スクリプト
├── sample/
│   └── SampleClass.java  # サンプルJavaファイル
└── venv/               # Python仮想環境
```

## 注意事項

- 解析対象のJavaファイルは構文的に正しい必要があります
- インポート文のみのクラスや、アノテーションのみの記述は解析対象外です
- 匿名クラス内のインスタンス生成も検出されます

## 依存パッケージ

- Python 3.8以上
- javalang
