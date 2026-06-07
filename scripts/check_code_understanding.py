"""V5.3 code-understanding 章节级 L1 钩子（08-code-understanding 红线）

验证 src/code-understanding/ 下的 AST 调用图示例存在 + 关键函数定义。
"""

from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
CU_DIR = REPO_ROOT / "src" / "code-understanding"

# 关键 .py 示例文件 + 期望含的函数名
EXPECTED_FILES_AND_FUNCS = {
    "call_graph_example.py": ["build_graph", "find_callees", "add_entity"],
}


def main() -> int:
    if not CU_DIR.exists():
        print(f"FAIL: {CU_DIR} 不存在")
        return 1

    errors: list[str] = []

    for filename, expected_funcs in EXPECTED_FILES_AND_FUNCS.items():
        path = CU_DIR / filename
        if not path.exists():
            errors.append(f"缺文件: src/code-understanding/{filename}")
            continue

        # AST 解析 + 检查函数存在
        try:
            source = path.read_text(encoding="utf-8")
            tree = ast.parse(source)
        except SyntaxError as e:
            errors.append(f"{filename} 语法错误: {e}")
            continue

        func_names = {
            node.name
            for node in ast.walk(tree)
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        }
        for expected in expected_funcs:
            if expected not in func_names:
                errors.append(
                    f"{filename} 缺关键函数 {expected!r}（实际: {sorted(func_names)}）"
                )

    if errors:
        print("FAIL code-understanding 章节级 L1 验证不通过：")
        for e in errors:
            print(f"  - {e}")
        return 1

    print(
        f"OK code-understanding 章节级 L1 验证通过（{len(EXPECTED_FILES_AND_FUNCS)} 个示例文件）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
