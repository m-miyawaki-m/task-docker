#!/usr/bin/env python3
"""
Javaクラス解析ツール
javalangを使用して、クラス内のインスタンス生成とメソッド呼び出しを解析する
"""

import javalang
from dataclasses import dataclass, field
from typing import List, Dict, Set
from pathlib import Path


@dataclass
class InstanceInfo:
    """インスタンス情報"""
    class_name: str           # インスタンス対象のクラス名
    variable_name: str        # 変数名
    scope: str                # スコープ (field/local)
    line: int = 0             # 行番号


@dataclass
class MethodCallInfo:
    """メソッド呼び出し情報"""
    instance_name: str        # インスタンス名（呼び出し元）
    method_name: str          # メソッド名
    class_type: str = ""      # インスタンスのクラス型
    line: int = 0             # 行番号

    @property
    def call_signature(self) -> str:
        """呼び出し箇所の文字列表現（インスタンス名.メソッド名）"""
        return f"{self.instance_name}.{self.method_name}()"


@dataclass
class AnalysisResult:
    """解析結果"""
    class_name: str
    instances: List[InstanceInfo] = field(default_factory=list)
    method_calls: List[MethodCallInfo] = field(default_factory=list)


def analyze_java_file(file_path: str) -> List[AnalysisResult]:
    """Javaファイルを解析する"""
    with open(file_path, 'r', encoding='utf-8') as f:
        source_code = f.read()
    return analyze_java_source(source_code)


def analyze_java_source(source_code: str) -> List[AnalysisResult]:
    """Javaソースコードを解析する"""
    tree = javalang.parse.parse(source_code)
    results = []

    for _, class_decl in tree.filter(javalang.tree.ClassDeclaration):
        result = AnalysisResult(class_name=class_decl.name)

        # フィールド宣言からインスタンスを抽出
        for field_decl in class_decl.fields:
            for declarator in field_decl.declarators:
                class_type = get_type_name(field_decl.type)
                instance = InstanceInfo(
                    class_name=class_type,
                    variable_name=declarator.name,
                    scope="field",
                    line=field_decl.position.line if field_decl.position else 0
                )
                result.instances.append(instance)

                # フィールドでnewしている場合の初期化クラスも取得
                if declarator.initializer and isinstance(declarator.initializer, javalang.tree.ClassCreator):
                    creator_class = declarator.initializer.type.name
                    if creator_class != class_type:
                        # ArrayList<String> names = new ArrayList<>(); のようなケース
                        instance.class_name = f"{class_type} (impl: {creator_class})"

        # メソッド内のローカル変数とメソッド呼び出しを解析
        for method_decl in class_decl.methods:
            analyze_method(method_decl, result)

        # コンストラクタ内も解析
        for constructor in class_decl.constructors:
            analyze_method(constructor, result)

        results.append(result)

    return results


def get_type_name(type_node) -> str:
    """型ノードから型名を取得"""
    if isinstance(type_node, javalang.tree.ReferenceType):
        name = type_node.name
        if type_node.arguments:
            args = ", ".join(get_type_name(arg.type) if hasattr(arg, 'type') else str(arg)
                           for arg in type_node.arguments if arg)
            name += f"<{args}>"
        return name
    elif isinstance(type_node, javalang.tree.BasicType):
        return type_node.name
    return str(type_node)


def analyze_method(method_node, result: AnalysisResult):
    """メソッド/コンストラクタ内を解析"""
    if not method_node.body:
        return

    # まずローカル変数宣言を収集
    local_vars: Dict[str, str] = {}  # 変数名 -> クラス型
    for path, node in method_node:
        if isinstance(node, javalang.tree.LocalVariableDeclaration):
            class_type = get_type_name(node.type)
            for declarator in node.declarators:
                instance = InstanceInfo(
                    class_name=class_type,
                    variable_name=declarator.name,
                    scope="local",
                    line=node.position.line if node.position else 0
                )
                result.instances.append(instance)
                local_vars[declarator.name] = class_type

    # インスタンス名からクラス型を引くための辞書を作成
    instance_type_map: Dict[str, str] = {}
    for inst in result.instances:
        instance_type_map[inst.variable_name] = inst.class_name

    # メソッド呼び出しを探す
    for path, node in method_node:
        if isinstance(node, javalang.tree.MethodInvocation):
            qualifier = node.qualifier if node.qualifier else "this"
            # インスタンス名からクラス型を取得
            class_type = instance_type_map.get(qualifier, "")
            call = MethodCallInfo(
                instance_name=qualifier,
                method_name=node.member,
                class_type=class_type,
                line=node.position.line if node.position else 0
            )
            result.method_calls.append(call)


def print_results(results: List[AnalysisResult]):
    """解析結果を表示"""
    for result in results:
        print(f"\n{'='*60}")
        print(f"クラス: {result.class_name}")
        print(f"{'='*60}")

        print(f"\n【インスタンス一覧】")
        print(f"{'クラス名':<30} {'変数名':<20} {'スコープ':<10} {'行番号'}")
        print("-" * 70)
        for inst in result.instances:
            print(f"{inst.class_name:<30} {inst.variable_name:<20} {inst.scope:<10} {inst.line}")

        print(f"\n【メソッド呼び出し一覧】")
        print(f"{'呼び出し箇所':<40} {'クラス型':<25} {'行番号'}")
        print("-" * 75)
        for call in result.method_calls:
            print(f"{call.call_signature:<40} {call.class_type:<25} {call.line}")


def export_to_csv(results: List[AnalysisResult], output_dir: str = "."):
    """結果をCSVファイルに出力"""
    import csv
    output_path = Path(output_dir)

    for result in results:
        # インスタンス一覧
        instance_file = output_path / f"{result.class_name}_instances.csv"
        with open(instance_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['クラス名', '変数名', 'スコープ', '行番号'])
            for inst in result.instances:
                writer.writerow([inst.class_name, inst.variable_name, inst.scope, inst.line])
        print(f"出力: {instance_file}")

        # メソッド呼び出し一覧
        method_file = output_path / f"{result.class_name}_method_calls.csv"
        with open(method_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['呼び出し箇所', 'インスタンス名', 'メソッド名', 'クラス型', '行番号'])
            for call in result.method_calls:
                writer.writerow([call.call_signature, call.instance_name, call.method_name, call.class_type, call.line])
        print(f"出力: {method_file}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        # デフォルトでサンプルを解析
        sample_path = Path(__file__).parent / "sample" / "SampleClass.java"
        if sample_path.exists():
            print(f"サンプルファイルを解析: {sample_path}")
            results = analyze_java_file(str(sample_path))
            print_results(results)
        else:
            print("使用方法: python analyze_java.py <Javaファイルパス> [--csv]")
            sys.exit(1)
    else:
        file_path = sys.argv[1]
        results = analyze_java_file(file_path)
        print_results(results)

        if "--csv" in sys.argv:
            export_to_csv(results)
