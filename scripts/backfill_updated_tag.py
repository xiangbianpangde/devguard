#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
backfill_updated_tag.py — 为在范围文档 .md 回填「更新」标签（V2.3 #54）
============================================================
依据：用户 2026-06-11 澄清——所有文档类 .md 都要有「更新」标签，改动后刷新，
便于日后文档整理。本脚本是一次性迁移工具（也可对新增缺标签文件复跑）。

范围 = git 跟踪的 *.md，排除：docs/templates/ / worklogs/ / .github/ / CHANGELOG.md
       （模板与历史日志冻结，见 meta/豁免清单.md / 设计 §阶段B）。
回填日期 = 每个文件 git 最后一次提交日期（真实"上次更新"），取不到则今天。

插入位置：第一个 H1 之后——
  - 若 H1 后已有 blockquote 块 → 把 `> 更新: <date>` 追加进该块
  - 否则在 H1 后另起一个 `> 更新: <date>` blockquote（前后各一空行）

用法:
    python scripts/backfill_updated_tag.py --dry-run   # 只打印将改什么，不写盘
    python scripts/backfill_updated_tag.py --apply      # 实际写入
    python scripts/backfill_updated_tag.py --refresh-staged
        # 仅刷新本次暂存且在范围内的 Markdown；缺标签时补今天，旧标签改为今天
"""

from __future__ import annotations

import datetime
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
UPDATE_TAG = re.compile(r"^>\s*更新[:：]\s*\d{4}-\d{2}-\d{2}", re.MULTILINE)
H1 = re.compile(r"^#\s")


def in_scope(rel: str) -> bool:
    if not rel.endswith(".md"):
        return False
    if rel.startswith(("docs/templates/", "worklogs/", ".github/")):
        return False
    if rel == "CHANGELOG.md":
        return False
    return True


def tracked_md() -> list[str]:
    out = subprocess.run(
        ["git", "-c", "core.quotepath=false", "ls-files", "*.md"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout
    return [ln.strip() for ln in out.splitlines() if ln.strip()]


def staged_md() -> list[str]:
    """Return staged, non-deleted Markdown paths using stable UTF-8 Git output."""
    out = subprocess.run(
        [
            "git",
            "-c",
            "core.quotepath=false",
            "diff",
            "--cached",
            "--name-only",
            "--diff-filter=ACMR",
            "--",
            "*.md",
        ],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=True,
    ).stdout
    return [ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()]


def git_last_date(rel: str) -> str:
    """文件 git 最后提交日期 YYYY-MM-DD；取不到则今天。"""
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short", "--", rel],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout.strip()
    except subprocess.CalledProcessError:
        out = ""
    return out or datetime.date.today().isoformat()


def insert_tag(content: str, date: str) -> str | None:
    """返回插入「更新」标签后的内容；已有标签则返回 None（跳过）。"""
    if UPDATE_TAG.search(content):
        return None
    lines = content.split("\n")
    tag = f"> 更新: {date}"

    h1 = next((i for i, ln in enumerate(lines) if H1.match(ln)), None)
    if h1 is None:
        # 无 H1：置顶插入
        return "\n".join([tag, ""] + lines)

    # H1 后跳过空行，看是否紧跟 blockquote
    j = h1 + 1
    while j < len(lines) and lines[j].strip() == "":
        j += 1
    if j < len(lines) and lines[j].lstrip().startswith(">"):
        # 追加进现有 blockquote 块末尾
        k = j
        while k < len(lines) and lines[k].lstrip().startswith(">"):
            k += 1
        lines.insert(k, tag)
    else:
        # 另起 blockquote：去掉 H1 后既有空行，统一插入 ['', tag, '']
        del lines[h1 + 1 : j]
        lines[h1 + 1 : h1 + 1] = ["", tag, ""]
    return "\n".join(lines)


def refresh_tag(content: str, date: str) -> str | None:
    """Refresh the first tag or insert one; return None when already current."""
    if UPDATE_TAG.search(content):
        refreshed = UPDATE_TAG.sub(f"> 更新: {date}", content, count=1)
        return None if refreshed == content else refreshed
    return insert_tag(content, date)


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) == 2 else ""
    if mode not in ("--dry-run", "--apply", "--refresh-staged"):
        print(
            "用法: python scripts/backfill_updated_tag.py "
            "--dry-run|--apply|--refresh-staged",
            file=sys.stderr,
        )
        return 1

    files = [
        f
        for f in (staged_md() if mode == "--refresh-staged" else tracked_md())
        if in_scope(f)
    ]
    changed = 0
    skipped = 0
    for rel in files:
        path = REPO_ROOT / rel
        content = path.read_text(encoding="utf-8")
        date = (
            datetime.date.today().isoformat()
            if mode == "--refresh-staged"
            else git_last_date(rel)
        )
        new = (
            refresh_tag(content, date)
            if mode == "--refresh-staged"
            else insert_tag(content, date)
        )
        if new is None:
            skipped += 1
            continue
        changed += 1
        if mode == "--dry-run":
            print(f"+ {rel}  →  > 更新: {date}")
        else:
            path.write_text(new, encoding="utf-8", newline="\n")
    print(
        f"\n在范围 {len(files)} 个；将回填 {changed}，已有标签跳过 {skipped}（{mode}）"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
