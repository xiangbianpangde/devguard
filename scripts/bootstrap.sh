#!/usr/bin/env bash
# DevGuard 开发环境重建（2026-08-13 蓝队大类五：可复现性证明）
#
# 用法：
#   bash scripts/bootstrap.sh            # 重建 .venv + 安装固定依赖 + 测试全绿
#   bash scripts/bootstrap.sh --fingerprint  # 只输出版本指纹（不重建）
#
# 退出码：0=全部通过；1=失败（fail-closed）
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PY="${DEVGUARD_PYTHON:-python3}"

fingerprint() {
    printf '=== DevGuard 版本指纹 ===\n'
    "$PY" --version
    "$REPO_ROOT/.venv/bin/python" -c "
from importlib.metadata import version
try:
    for pkg in ('pre-commit', 'pytest', 'ruff'):
        print(f'{pkg}={version(pkg)}')
except Exception as e:
    print(f'（.venv 未就绪：{e}）')
" 2>/dev/null || printf '（.venv 未就绪，见下方重建步骤）\n'
    grep -E "^(ruff|gitleaks|pre-commit|pytest)==" "$REPO_ROOT/requirements-dev.txt" 2>/dev/null \
        || printf 'requirements-dev.txt 无钉版匹配\n'
    grep -A4 "^toolchain:" "$REPO_ROOT/conventions/_meta.yaml" | head -5
}

if [[ "${1:-}" == "--fingerprint" ]]; then
    fingerprint
    exit 0
fi

section() { printf '\n\033[1;36m== %s ==\033[0m\n' "$*"; }

section "Step 1/3 重建 .venv（隔离环境 + 固定依赖）"
rm -rf "$REPO_ROOT/.venv"
"$PY" -m venv "$REPO_ROOT/.venv"
"$REPO_ROOT/.venv/bin/python" -m pip install -q -r "$REPO_ROOT/requirements-dev.txt"
printf 'venv 重建完成\n'

section "Step 2/3 重装双阶段 hooks（指向 .venv 解释器）"
( cd "$REPO_ROOT" && .venv/bin/python -m pre_commit install-hooks )
printf 'pre-commit 钩子环境就绪\n'

section "Step 3/3 测试全绿"
( cd "$REPO_ROOT" && .venv/bin/python -m pytest tests/ -q --no-header )
printf '\n\033[1;32mDevGuard bootstrap 完成：环境可复现，测试全绿\033[0m\n'
fingerprint
exit 0
