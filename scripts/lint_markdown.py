"""V0.3 markdownlint 包装（06-documentation 红线 L1）

markdownlint-cli 不管传 '**/*.md' 还是 '**'，都把"附加 glob + 默认所有 md-like 文件"一起扫。
绕开这个行为：先在 Python 里列所有 .md 文件，再传给 markdownlint。

排除：
- node_modules/ (.gitignore)
- dashboard.html.lock
- .git/
- 任何 .pre-commit-config.yaml 等非 .md 文件
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {"node_modules", ".git", "__pycache__"}
EXCLUDE_FILES = {"dashboard.html.lock"}


def main() -> int:
    md_files: list[str] = []
    for path in sorted(REPO_ROOT.rglob("*.md")):
        if any(part in EXCLUDE_DIRS for part in path.parts):
            continue
        if path.name in EXCLUDE_FILES:
            continue
        md_files.append(str(path))

    if not md_files:
        print("No .md files found")
        return 0

    print(f"Linting {len(md_files)} .md file(s)")
    # 用 npx 跨平台调用（Windows .cmd shim / Linux 直接 binary 都通）
    cmd = ["npx", "--no", "markdownlint", *md_files]
    result = subprocess.run(cmd, cwd=REPO_ROOT, shell=True)  # noqa: S602
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
