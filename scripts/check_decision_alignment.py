#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_decision_alignment.py — commit-msg 钩子：关键决策未对齐拦开工（V2.3 #50）
============================================================
依据：设计提案-约束与模板强化方案-v2.3 §3.3 阶段E（交流 agent + 强制措施）
      + ai-workflow 05-思考设计（AI 不替人做产品决策；设计经人确认才能开工）。

交流 agent（.claude/agents/liaison.md）产出设计提案 + Owner 决策点清单；
本钩子把「关键决策未对齐则不得开工」从 CLAUDE 规则升级为提交时硬拦：

判定逻辑（commit-msg 钩子，argv[1] = commit_msg_file）：
  1. commit message 含 [skip-align] → 放行（豁免须登记 meta/豁免清单.md）
  2. 本次 staged 的设计提案（docs/plan/design/设计提案-*.md）：
     a. 缺「Owner 决策」节 → FAIL（交流 agent 的产出契约：决策点必须呈交人）
     b. 含「待拍板」→ 仅 WARN（草案可入库）
  3. 拦开工：本次提交把 开发清单.md 中任一功能点行翻为 ✅（staged vs HEAD 比对），
     而任一 staged 设计提案仍含「待拍板」→ FAIL（边拍板边开工）
  4. 无 staged 提案 / 无新交付 → 放行（零摩擦）

附加用法：
  python scripts/check_decision_alignment.py --all   # 全仓提案审计：
      缺「Owner 决策」节 exit 1；遗留「待拍板」仅列出（CI 可见，不阻断）

用法（pre-commit 框架调用）:
    python scripts/check_decision_alignment.py <commit_msg_file>
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

# Windows 中文 stdout 兼容（cp1252 下打印中文会 UnicodeEncodeError）
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_REL = "docs/plan/开发清单.md"
SKIP_MARKER = "[skip-align]"

PROPOSAL_RE = re.compile(r"^docs/plan/design/设计提案-.*\.md$")
# 「Owner 决策」节标题（## 六、Owner 决策 / ## Owner 决策点 等变体）
DECISION_HEADING = re.compile(r"^#{2,3}\s.*Owner\s*决策", re.MULTILINE)
PENDING_MARK = "待拍板"


def staged_files() -> list[str]:
    try:
        out = subprocess.run(
            ["git", "-c", "core.quotepath=false", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    return [ln.strip().replace("\\", "/") for ln in out.splitlines() if ln.strip()]


def git_show(ref_path: str) -> str | None:
    try:
        return subprocess.run(
            ["git", "show", ref_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=True,
        ).stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def staged_content(path: str) -> str:
    content = git_show(f":{path}")
    if content is not None:
        return content
    fp = REPO_ROOT / path
    return fp.read_text(encoding="utf-8") if fp.exists() else ""


def done_fps(plan_text: str) -> set[int]:
    """开发清单中状态含 ✅ 的功能点编号集合。"""
    done: set[int] = set()
    for line in plan_text.splitlines():
        s = line.strip()
        if not s.startswith("|"):
            continue
        cells = [c.strip() for c in s.strip("|").split("|")]
        if not cells:
            continue
        first = cells[0].strip("*")
        if first.isdigit() and any("✅" in c for c in cells):
            done.add(int(first))
    return done


# R5-33（2026-08-14 红队第三批）：待拍板按行解析——全篇 substring 可被
# 「当前无待拍板项」否定说明或同义改写（待 Owner 复核/事后签认）绕过。
PENDING_PATTERNS = (
    "待拍板",
    "待 Owner",
    "待Owner",
    "待复核",
    "事后签认",
    "Owner 拍板",
    "待拍板：",
    "- [ ]",
)
NEGATION_PATTERNS = ("无待拍板", "已拍板", "已采纳", "已决策", "已签", "已复核")


def _has_pending(decision_section: str) -> bool:
    """决策节内按行判断是否有未决决策点（行级否定语境除外）。

    R5-33 残余（红队第四批复验）：行内否定——「当前无待拍板项。待拍板：选择A」
    同一行既有否定又有真实 pending：按句号切句，否定只作用于其所在句。
    """
    for line in decision_section.splitlines():
        if not any(pat in line for pat in PENDING_PATTERNS):
            continue
        # 按句号/分号切句，逐句判断（否定只豁免其所在句）
        sentences = [s for s in re.split(r"[。；;]", line) if s.strip()]
        for sentence in sentences:
            if not any(pat in sentence for pat in PENDING_PATTERNS):
                continue
            if any(neg in sentence for neg in NEGATION_PATTERNS):
                continue
            return True
    return False


def check_proposal(rel: str, content: str) -> tuple[list[str], bool]:
    """返回 (errors, has_pending)。"""
    errors: list[str] = []
    if not DECISION_HEADING.search(content):
        errors.append(f"{rel}: 缺「Owner 决策」节（交流 agent 产出契约：决策点必须呈交人拍板）")
    else:
        # R5-34（2026-08-14 红队第九轮）：决策节必须含真实决策证据——
        # 拒绝「蓝队自主产出」类自我授权占位（决策审计只验节存在不验真实性）。
        decision_section = content.split(DECISION_HEADING.search(content).group(0), 1)[-1]
        # R5-34（红队第三批）：拒绝「蓝队自主产出」自我授权占位——无论是否拼凑
        # Owner/拍板/签核 等字样（复制授权文本恰好命中关键词豁免即绕过）。
        # 决策节必须含**实质决策记录**（日期 + 具体决策内容 + 执行状态）。
        section_head = decision_section[:400]
        if "蓝队自主产出" in section_head:
            errors.append(
                f"{rel}: Owner 决策节为自我授权占位（含「蓝队自主产出」）——"
                "须改为实质决策记录（日期+决策+状态）"
            )
        elif any(ln.lstrip().startswith("|") for ln in section_head.splitlines()):
            pass  # 表格型决策节（历史提案格式）也是实质记录
        elif not re.search(r"\d{4}-\d{2}-\d{2}[：:]\s*\S", section_head):
            errors.append(f"{rel}: Owner 决策节缺实质决策记录（期望 日期+决策/采用/执行 内容）")
    decision_section = (
        content.split(DECISION_HEADING.search(content).group(0), 1)[-1]
        if DECISION_HEADING.search(content)
        else content
    )
    return errors, _has_pending(decision_section)


def audit_all() -> int:
    base = REPO_ROOT / "docs" / "plan" / "design"
    errors: list[str] = []
    pending: list[str] = []
    n = 0
    if base.exists():
        for fp in sorted(base.glob("设计提案-*.md")):
            rel = fp.relative_to(REPO_ROOT).as_posix()
            n += 1
            errs, has_pending = check_proposal(rel, fp.read_text(encoding="utf-8"))
            errors.extend(errs)
            if has_pending:
                pending.append(rel)
    # R5-33（2026-08-14 红队第九轮）：已执行提案（状态含 ✅/已执行/已实现）带
    # 「待拍板」→ FAIL——边拍板边开工必须可追溯，不能仅 WARN 提示。
    pending_fail: list[str] = []
    if base.exists():
        for fp in sorted(base.glob("设计提案-*.md")):
            content = fp.read_text(encoding="utf-8")
            decision_section = (
                content.split(DECISION_HEADING.search(content).group(0), 1)[-1]
                if DECISION_HEADING.search(content)
                else content
            )
            if _has_pending(decision_section) and re.search(
                r"状态[:：].*(✅|已执行|已实现|已落地)", content
            ):
                pending_fail.append(fp.name)
    for p in pending:
        print(f"WARN {p}: 仍有「待拍板」决策点（开工前须清零）")
    if pending_fail:
        errors.append(
            "以下提案已执行（状态含完成标记）但仍带「待拍板」决策点（边拍板边开工）: "
            + ", ".join(pending_fail)
        )
    if errors:
        print(f"FAIL 设计提案审计（{n} 份）：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        return 1
    print(f"OK 设计提案审计通过（{n} 份；待拍板提示 {len(pending)} 条）")
    return 0


def main() -> int:
    if len(sys.argv) == 2 and sys.argv[1] == "--all":
        return audit_all()

    if len(sys.argv) != 2:
        print(
            "用法: python check_decision_alignment.py <commit_msg_file> | --all",
            file=sys.stderr,
        )
        return 1

    msg = Path(sys.argv[1]).read_text(encoding="utf-8")
    if SKIP_MARKER in msg:
        print("SKIP: commit message 含 [skip-align]，跳过决策对齐检查")
        return 0

    staged = staged_files()
    proposals = [f for f in staged if PROPOSAL_RE.match(f)]

    errors: list[str] = []
    pending_files: list[str] = []
    for rel in proposals:
        errs, has_pending = check_proposal(rel, staged_content(rel))
        errors.extend(errs)
        if has_pending:
            pending_files.append(rel)

    # 拦开工：本次有新交付（✅ 新增）且 staged 提案仍有待拍板
    if pending_files and PLAN_REL in staged:
        staged_done = done_fps(staged_content(PLAN_REL))
        head_done = done_fps(git_show(f"HEAD:{PLAN_REL}") or "")
        newly_done = staged_done - head_done
        if newly_done:
            errors.append(
                f"本次交付功能点 {sorted(newly_done)}，但 staged 设计提案仍有"
                f"「待拍板」：{pending_files}（关键决策未对齐不得开工，"
                f"先用交流 agent 让 Owner 拍板清零）"
            )
        else:
            for p in pending_files:
                print(f"WARN {p}: 含「待拍板」决策点（草案可入库，开工前须清零）")
    elif pending_files:
        for p in pending_files:
            print(f"WARN {p}: 含「待拍板」决策点（草案可入库，开工前须清零）")

    if errors:
        print("FAIL 决策对齐检查不通过：", file=sys.stderr)
        for e in errors:
            print(f"  - {e}", file=sys.stderr)
        print("", file=sys.stderr)
        print(
            "  交流 agent: .claude/agents/liaison.md（需求对齐/决策澄清）",
            file=sys.stderr,
        )
        print("  豁免: 末尾加 [skip-align]（须登记 meta/豁免清单.md）", file=sys.stderr)
        return 1

    if proposals:
        print(f"OK 决策对齐检查通过（{len(proposals)} 份 staged 提案）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
