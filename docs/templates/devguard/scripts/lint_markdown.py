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

import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
EXCLUDE_DIRS = {"node_modules", ".git", "__pycache__", "历史文件"}
EXCLUDE_FILES = {"dashboard.html.lock"}


def _run_batches(
    md_files: list[str],
    *,
    platform: str = sys.platform,
    runner=subprocess.run,
    which=shutil.which,
) -> int:
    """分批调用 markdownlint（Windows 命令行 ~8KB 限制，每批 50 个文件）。

    跨平台纪律：
    - 仅 Windows 用 shell=True（npx 是 .cmd shim，不经 shell 找不到）；
      POSIX 必须列表参数直跑——shell=True + 列表在 POSIX 只执行 args[0]，
      会导致 markdownlint 从未运行却返回 0（门禁空转）。
    - npx 缺失时失败闭合（返回 1 并说明原因），绝不假通过。
    """
    if which("npx") is None:
        print("FAIL: 找不到 npx（先跑 npm ci 或安装 Node.js）", file=sys.stderr)
        return 1
    use_shell = platform == "win32"
    batch_size = 50
    overall_exit = 0
    for i in range(0, len(md_files), batch_size):
        batch = md_files[i : i + batch_size]
        cmd = ["npx", "--no", "markdownlint", *batch]
        try:
            result = runner(cmd, cwd=REPO_ROOT, shell=use_shell)  # noqa: S602,S603
        except FileNotFoundError:
            print("FAIL: npx 无法执行（Node.js 环境损坏？）", file=sys.stderr)
            return 1
        if result.returncode != 0:
            overall_exit = result.returncode
    return overall_exit


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
    return _run_batches(md_files)


if __name__ == "__main__":
    sys.exit(main())
