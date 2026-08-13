#!/usr/bin/env bash
# DevGuard 全新环境一键自检（方案④，2026-08-13 蓝队整理新增）
#
# 用法：
#   bash scripts/selfcheck.sh          # 快速自检（自仓健康 + 临时目录初始化/复验）
#   bash scripts/selfcheck.sh --full   # 全链路自检（含 --install：venv + pip + hooks，慢）
#
# 退出码：0=全部通过；1=任一步失败（fail-closed）
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FULL=0
if [[ "${1:-}" == "--full" ]]; then
    FULL=1
fi

PY=""
if [[ -x "$REPO_ROOT/.venv/bin/python" ]]; then
    PY="$REPO_ROOT/.venv/bin/python"
    printf 'DevGuard selfcheck: python=%s (仓内 .venv)\n' "$PY" >&2
elif [[ -n "${DEVGUARD_PYTHON:-}" ]]; then
    PY="$DEVGUARD_PYTHON"
else
    PY="python3"
fi
TMP_ROOT="$(mktemp -d)"
cleanup() {
    rm -rf "$TMP_ROOT"
}
trap cleanup EXIT

section() { printf '\n\033[1;36m== %s ==\033[0m\n' "$*"; }
pass() { printf '\033[1;32mPASS\033[0m %s\n' "$*"; }
fail() { printf '\033[1;31mFAIL\033[0m %s\n' "$*" >&2; exit 1; }

section "Phase 1/3 自仓健康"
( cd "$REPO_ROOT" && "$PY" -m pytest tests/ -q --no-header ) \
    || fail "自仓测试未全绿"
pass "pytest tests/ 全绿"

( cd "$REPO_ROOT" && "$PY" scripts/check_template_drift.py ) \
    || fail "模板漂移检测未通过"
pass "check_template_drift 通过（脚本镜像 + 脚手架镜像）"

( cd "$REPO_ROOT" && "$PY" scripts/check_consistency.py ) \
    || fail "一致性矩阵未通过"
pass "check_consistency 通过"

section "Phase 2/3 临时目录 core 初始化 + 复验"
TARGET="$TMP_ROOT/fresh-project"
( cd "$REPO_ROOT" && "$PY" scripts/setup_scaffold.py "$TARGET" --profile core --project-name "SelfCheck Project" ) \
    || fail "core 初始化失败"
pass "core 初始化（22 文件 payload）"

( cd "$REPO_ROOT" && "$PY" scripts/setup_scaffold.py "$TARGET" --verify ) \
    || fail "--verify 未通过"
pass "--verify 通过（payload 校验）"

section "Phase 2.5/3 dry-run 零写入"
DRY_OUT="$(cd "$REPO_ROOT" && "$PY" scripts/setup_scaffold.py "$TMP_ROOT/dry" --profile core --dry-run 2>&1)" \
    || fail "dry-run 失败"
if [[ -e "$TMP_ROOT/dry" ]]; then
    fail "dry-run 不应创建目标目录"
fi
pass "dry-run 零写入验证"

if [[ "$FULL" -eq 1 ]]; then
    section "Phase 3/3 全链路 --install（venv + pip + hooks）"
    ( cd "$REPO_ROOT" && "$PY" scripts/setup_scaffold.py "$TARGET" --install ) \
        || fail "--install 全链路失败"
    ( cd "$REPO_ROOT" && "$PY" scripts/setup_scaffold.py "$TARGET" --verify --require-hooks ) \
        || fail "--verify --require-hooks 未通过"
    pass "--install 全链路 + --verify --require-hooks 通过"
    "$TARGET/.venv/bin/python" -m pytest "$TARGET/tests/governance" -q --no-header \
        || fail "目标项目自检测试失败"
    pass "目标项目自检测试通过"
else
    section "Phase 3/3 跳过（--full 启用全链路）"
fi

section "全部通过 ✅"
exit 0
