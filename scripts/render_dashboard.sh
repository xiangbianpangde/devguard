#!/usr/bin/env bash
# ============================================================
# render_dashboard.sh — 渲染 dashboard.html（L4 数字自动收集）
# ============================================================
# 取代 package.json 里写死 --l4-passed/--l4-total 的旧脚本
# L4 统计来源：scripts/collect_l4_stats.py
# 对应规范：09-dashboard-gen
# ============================================================
set -euo pipefail
cd "$(dirname "$0")/.."

L4_STATS=$(python scripts/collect_l4_stats.py 2>/dev/null || echo "L4_STATS=0/0")
L4_PASSED=$(echo "$L4_STATS" | sed 's/L4_STATS=\([0-9]*\)\/\([0-9]*\)/\1/')
L4_TOTAL=$(echo "$L4_STATS" | sed 's/L4_STATS=\([0-9]*\)\/\([0-9]*\)/\2/')
# 防御空字符串（V7.2）
L4_PASSED="${L4_PASSED:-0}"
L4_TOTAL="${L4_TOTAL:-0}"
echo "L4 stats: passed=$L4_PASSED total=$L4_TOTAL"

python docs/templates/devguard/html-report-template/render.py \
  --meta conventions/_meta.yaml \
  --status STATUS.md \
  --out dashboard.html \
  --l4-passed "$L4_PASSED" \
  --l4-total "$L4_TOTAL"
