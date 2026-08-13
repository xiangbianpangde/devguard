#!/usr/bin/env bash
# DevGuard 一键安装引导（POSIX）。
#
# 用法：
#   bash scripts/install.sh <目标目录> [setup_scaffold.py 参数...]
#   curl -fsSL <raw-url>/scripts/install.sh | bash -s -- <目标目录> [参数...]
#
# 职责：探测 Python >= 3.10 → 定位 devguard 仓 → 原样透传参数调用
# scripts/setup_scaffold.py。失败闭合：不自动安装 Python、不静默降级、
# 不自动 clone 仓库。
#
# devguard 仓定位顺序：
#   1. --repo <路径>（安装器自身参数，会被消费、不透传）
#   2. 环境变量 DEVGUARD_REPO
#   3. 脚本所在目录的上一级（本地执行时）
#   4. 当前工作目录
#
# Python 探测顺序：DEVGUARD_PYTHON（若设置，强制使用）→ python3 → python。
set -euo pipefail

MIN_MAJOR=3
MIN_MINOR=10

die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

python_guidance() {
    printf '%s\n' \
        '未找到 Python >= 3.10。请先安装再重试（安装器不会自动安装 Python）：' \
        '  - macOS:        brew install python@3.12   或 https://www.python.org/downloads/' \
        '  - Ubuntu/Debian: sudo apt-get install python3 python3-venv' \
        '  - Fedora:       sudo dnf install python3' \
        '  - Arch:         sudo pacman -S python' \
        '  - Windows:      使用 scripts/install.ps1（irm | iex）' \
        >&2
}

repo_guidance() {
    printf '%s\n' \
        '未找到 devguard 仓（缺少 scripts/setup_scaffold.py）。请任选其一：' \
        '  1. git clone https://github.com/xiangbianpangde/devguard.git' \
        '     然后在仓内执行：bash scripts/install.sh <目标目录> [参数...]' \
        '  2. 指定既有仓路径：bash install.sh --repo <devguard 路径> <目标目录> [参数...]' \
        '     或设置环境变量 DEVGUARD_REPO=<devguard 路径>' \
        >&2
}

# 解析安装器自身参数（--repo / -h），其余全部透传给 setup_scaffold.py
REPO=""
PASSTHROUGH=()
while (($#)); do
    case "$1" in
        --repo)
            (($# >= 2)) || die "--repo 需要路径参数"
            REPO="$2"
            shift 2
            ;;
        --repo=*)
            REPO="${1#--repo=}"
            shift
            ;;
        -h | --help)
            printf '%s\n' \
                '用法: bash scripts/install.sh [--repo <devguard 路径>] <目标目录> [参数...]' \
                '      curl -fsSL <raw-url>/scripts/install.sh | bash -s -- <目标目录> [参数...]' \
                '环境变量: DEVGUARD_REPO（仓路径）/ DEVGUARD_PYTHON（指定解释器）' \
                '透传参数（原样交给 scripts/setup_scaffold.py）：' \
                '  <目标目录> [--profile {core,optional}] [--project-name 名称]' \
                '  [--force] [--install] [--dry-run] [--verify] [--require-hooks]'
            exit 0
            ;;
        *)
            PASSTHROUGH+=("$1")
            shift
            ;;
    esac
done

# 1) 探测 Python >= 3.10
version_ok() {
    # $1 = 解释器命令；打印 "major.minor"，不可执行时返回非零
    "$1" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")' 2>/dev/null
}

PY=""
if [[ -n "${DEVGUARD_PYTHON:-}" ]]; then
    ver="$(version_ok "$DEVGUARD_PYTHON")" || ver=""
    [[ -n "$ver" ]] || die "DEVGUARD_PYTHON=$DEVGUARD_PYTHON 不可执行或不是 Python"
    major="${ver%%.*}"
    minor="${ver##*.}"
    if ((major > MIN_MAJOR || (major == MIN_MAJOR && minor >= MIN_MINOR))); then
        PY="$DEVGUARD_PYTHON"
    else
        die "DEVGUARD_PYTHON=$DEVGUARD_PYTHON 版本为 ${ver}，需要 >= ${MIN_MAJOR}.${MIN_MINOR}"
    fi
else
    for cand in python3 python; do
        command -v "$cand" >/dev/null 2>&1 || continue
        ver="$(version_ok "$cand")" || continue
        major="${ver%%.*}"
        minor="${ver##*.}"
        if ((major > MIN_MAJOR || (major == MIN_MAJOR && minor >= MIN_MINOR))); then
            PY="$cand"
            break
        fi
    done
    if [[ -z "$PY" ]]; then
        python_guidance
        exit 1
    fi
fi

# 1.5) ensurepip 预检（2026-08-13 蓝队方案③：fail-closed，提前报错而非 venv 创建后报错滞后）
if ! "$PY" -m ensurepip --version >/dev/null 2>&1; then
    printf '%s\n' \
        'ERROR: ensurepip 不可用（无法创建带 pip 的虚拟环境）。请先修复：' \
        '  - Ubuntu/Debian: sudo apt-get install python3-venv' \
        '  - Fedora:        sudo dnf install python3-pip' \
        '  - 其他:         参考 https://pip.pypa.io/en/stable/installation/' \
        >&2
    exit 1
fi

# 2) 定位 devguard 仓
if [[ -z "$REPO" && -n "${DEVGUARD_REPO:-}" ]]; then
    REPO="$DEVGUARD_REPO"
fi
if [[ -z "$REPO" ]]; then
    script_src="${BASH_SOURCE[0]:-}"
    if [[ -n "$script_src" && "$script_src" != "bash" && -e "$script_src" ]]; then
        script_dir="$(cd "$(dirname "$script_src")" && pwd)"
        if [[ -f "$script_dir/../scripts/setup_scaffold.py" ]]; then
            REPO="$(cd "$script_dir/.." && pwd)"
        fi
    fi
fi
if [[ -z "$REPO" && -f "$PWD/scripts/setup_scaffold.py" ]]; then
    REPO="$PWD"
fi
if [[ -z "$REPO" || ! -f "$REPO/scripts/setup_scaffold.py" ]]; then
    repo_guidance
    exit 1
fi

# 3) 透传调用
printf 'DevGuard installer: python=%s repo=%s\n' "$PY" "$REPO" >&2
exec "$PY" "$REPO/scripts/setup_scaffold.py" "${PASSTHROUGH[@]}"
