#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
hook_updated_tag_posttooluse.py — Claude Code PostToolUse 钩子：编辑当下阻断（V2.3 #53）
============================================================
依据：设计提案-约束与模板强化方案-v2.3 §3.3 阶段B + Owner 决策3（阻断模式）

与 check_updated_tag.py（commit-msg 硬拦）配对的**会话内护栏**：
AI 每次 Edit/Write 受管文件后即时校验「更新」标签是否为今天，
不是则以退出码 2 阻断（stderr 反馈给模型，提示补齐后再继续）。

边界（设计 §1.3 固有限制）：本钩子只对 AI 生效，人手改文件不触发；
真·人机通拦由 commit-msg 钩子在提交时兜底。

输入：stdin 收到 Claude Code 的 PostToolUse JSON（含 tool_input.file_path）。
输出/退出码：
  0 = 放行（非受管文件 / 标签为今天 / 任何解析异常都 fail-open，避免误伤会话）
  2 = 阻断（受管文件缺标签或标签非今天），reason 写 stderr

配置见 .claude/settings.json 的 hooks.PostToolUse。
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_core():
    """复用 check_updated_tag 的 MANAGED 集合与 extract_update_date。"""
    path = REPO_ROOT / "scripts" / "check_updated_tag.py"
    spec = importlib.util.spec_from_file_location("check_updated_tag", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _rel(file_path: str) -> str | None:
    """把工具给的（可能绝对）路径转成 REPO_ROOT 相对的正斜杠路径。"""
    try:
        p = Path(file_path)
        if not p.is_absolute():
            p = REPO_ROOT / p
        return p.resolve().relative_to(REPO_ROOT).as_posix()
    except (ValueError, OSError):
        return None


def main() -> int:
    # fail-open：任何异常都放行，绝不因护栏脚本自身问题卡死会话
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return 0

    file_path = (data.get("tool_input") or {}).get("file_path", "")
    if not file_path:
        return 0

    rel = _rel(file_path)
    if rel is None:
        return 0

    try:
        core = _load_core()
    except Exception:
        return 0

    if not core.in_scope(rel):
        return 0

    abs_path = REPO_ROOT / rel
    if not abs_path.exists():
        return 0

    today = datetime.date.today().isoformat()
    date = core.extract_update_date(abs_path.read_text(encoding="utf-8"))

    if date == today:
        return 0

    if date is None:
        reason = f"受管文件 {rel} 缺 `> 更新: YYYY-MM-DD` 标签。"
    else:
        reason = f"受管文件 {rel} 的「更新」标签是 {date}，未刷新为今天 {today}。"
    print(
        f"[更新时间标签] {reason} 请把顶部 `> 更新:` 改成 {today} 再继续"
        "（豁免须在 meta/豁免清单.md 登记并提交时加 [skip-updated]）。",
        file=sys.stderr,
    )
    return 2


if __name__ == "__main__":
    sys.exit(main())
