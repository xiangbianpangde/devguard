#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup_scaffold.py — 基准约束脚手架：一键复制最小约束基线到新项目（V2.3 #49）
============================================================
依据：设计提案-约束与模板强化方案-v2.3 §3.3 阶段E
"让本套强制随项目模板外溢" —— 把 钩子 + CI + _meta.yaml + 模板 打包成可复制基线。

两层（区分"必带"与"可选"，Owner 决策 + 设计 §五 风险缓解）：
  必带（core）   ：真源 _meta.yaml + 渲染器 + 7 个通用流程钩子（worklog 三件 /
                  豁免登记 / 更新标签 / 文件放置 / 四件套同步）+ commitlint /
                  markdownlint / ruff 配置 + CI 流水线 + 基础文档模板 + 豁免清单种子
  可选（optional）：收束硬闸门 / HTML 模板族 + 结构校验 / 决策对齐 + 交流 agent /
                  Claude PostToolUse 护栏（依赖 Claude Code 或项目流程成熟度）

用法:
    python scripts/setup_scaffold.py <target_dir> [--with-optional] [--force]

之后在目标目录:
    1. 编辑 conventions/_meta.yaml（项目名 / 规范列表）
    2. python scripts/render_meta.py --render pre-commit-config
    3. git init && pip install pre-commit
       && pre-commit install && pre-commit install --hook-type commit-msg
    4. 按 docs/templates/ 模板实例化 CLAUDE.md / STATUS.md / docs/plan/开发清单.md
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TPL = "docs/templates"
DEVG = f"{TPL}/devguard"

# ---- 必带层清单：(仓内源路径, 目标相对路径) ----
CORE_MANIFEST: list[tuple[str, str]] = [
    # 真源 + 渲染器（_meta.yaml 的 pre_commit 节复制后由本脚本拼接为 live 版）
    (f"{DEVG}/conventions/_meta.yaml", "conventions/_meta.yaml"),
    ("scripts/render_meta.py", "scripts/render_meta.py"),
    ("scripts/lint_markdown.py", "scripts/lint_markdown.py"),
    # 7 个通用流程钩子（V2.1/V2.3 核心强制）
    ("scripts/check_worklog_ref.py", "scripts/check_worklog_ref.py"),
    ("scripts/check_status_updated.py", "scripts/check_status_updated.py"),
    ("scripts/check_worklog_structure.py", "scripts/check_worklog_structure.py"),
    ("scripts/check_file_placement.py", "scripts/check_file_placement.py"),
    ("scripts/check_exemption_log.py", "scripts/check_exemption_log.py"),
    ("scripts/check_updated_tag.py", "scripts/check_updated_tag.py"),
    ("scripts/check_doc_sync.py", "scripts/check_doc_sync.py"),
    # L1 工具配置
    ("commitlint.config.js", "commitlint.config.js"),
    (".markdownlint.json", ".markdownlint.json"),
    (".markdownlintignore", ".markdownlintignore"),
    (f"{DEVG}/src/coding/ruff.toml", "src/coding/ruff.toml"),
    # CI 流水线（5 阶段）
    (f"{DEVG}/.github/workflows/ci.yml", ".github/workflows/ci.yml"),
    # 基础文档模板（新项目实例化用）
    (f"{TPL}/CLAUDE模板.md", "docs/templates/CLAUDE模板.md"),
    (f"{TPL}/README模板.md", "docs/templates/README模板.md"),
    (f"{TPL}/STATUS模板.md", "docs/templates/STATUS模板.md"),
    (f"{TPL}/worklog模板.md", "docs/templates/worklog模板.md"),
    (f"{TPL}/plan开发清单模板.md", "docs/templates/plan开发清单模板.md"),
    (f"{TPL}/plan背景模板.md", "docs/templates/plan背景模板.md"),
    (f"{TPL}/BDD规格模板.md", "docs/templates/BDD规格模板.md"),
]

# ---- 可选层清单 ----
OPTIONAL_MANIFEST: list[tuple[str, str]] = [
    ("scripts/check_convergence_gate.py", "scripts/check_convergence_gate.py"),
    ("scripts/check_html_artifact.py", "scripts/check_html_artifact.py"),
    ("scripts/check_decision_alignment.py", "scripts/check_decision_alignment.py"),
    (
        "scripts/hook_updated_tag_posttooluse.py",
        "scripts/hook_updated_tag_posttooluse.py",
    ),
    (".claude/settings.json", ".claude/settings.json"),
    (".claude/agents/liaison.md", ".claude/agents/liaison.md"),
    (f"{TPL}/汇报模板.html", "docs/templates/汇报模板.html"),
    (f"{TPL}/计划模板.html", "docs/templates/计划模板.html"),
    (f"{TPL}/实施设计模板.html", "docs/templates/实施设计模板.html"),
    (f"{TPL}/绘图素材库模板.html", "docs/templates/绘图素材库模板.html"),
]

# 可选层钩子 id（不带 --with-optional 时从 pre_commit 节过滤掉）
OPTIONAL_HOOK_IDS = {
    "commit-msg-convergence-gate",
    "commit-msg-html-artifact",
    "commit-msg-decision-alignment",
}

# 豁免清单种子：核心标记 / 可选标记
CORE_MARKERS = [
    ("[skip-worklog]", "check_worklog_ref.py", "仅收束节点 / 紧急 hotfix"),
    ("[skip-status]", "check_status_updated.py", "仅纯 worklog 修订"),
    ("[skip-worklog-structure]", "check_worklog_structure.py", "仅历史 worklog 补登"),
    ("[skip-file-placement]", "check_file_placement.py", "仅过渡期，须当轮收口"),
    ("[skip-updated]", "check_updated_tag.py", "仅纯格式 / 回滚类提交"),
    ("[skip-docsync]", "check_doc_sync.py", "仅历史口径修复类提交"),
]
OPTIONAL_MARKERS = [
    ("[skip-gate]", "check_convergence_gate.py", "仅建闸门自身 / 收束过渡提交"),
    ("[skip-html]", "check_html_artifact.py", "仅存量产出物大改造过渡期"),
    ("[skip-align]", "check_decision_alignment.py", "仅与提案无关的紧急交付"),
]

SECTION_RE = re.compile(
    r"(^pre_commit:\n)(.*?)(?=\n# ={20,})", re.MULTILINE | re.DOTALL
)


def extract_pre_commit_section(text: str) -> str:
    """取 _meta.yaml 中 pre_commit: 节的正文（不含节名行）。"""
    m = SECTION_RE.search(text)
    if not m:
        raise ValueError("找不到 pre_commit: 节")
    return m.group(2)


def filter_hooks(section_body: str, exclude_ids: set[str]) -> str:
    """按 '  - id:' 块过滤 pre_commit 节正文。"""
    blocks = re.split(r"\n\n(?=  - id:)", section_body)
    kept = []
    for b in blocks:
        m = re.search(r"-\s*id:\s*([\w-]+)", b)
        if m and m.group(1) in exclude_ids:
            continue
        kept.append(b)
    return "\n\n".join(kept)


def build_meta_yaml(with_optional: bool) -> str:
    """模板 _meta.yaml + live pre_commit 节（按层过滤）。"""
    template = (REPO_ROOT / DEVG / "conventions" / "_meta.yaml").read_text(
        encoding="utf-8"
    )
    live = (REPO_ROOT / "conventions" / "_meta.yaml").read_text(encoding="utf-8")
    live_hooks = extract_pre_commit_section(live)
    if not with_optional:
        live_hooks = filter_hooks(live_hooks, OPTIONAL_HOOK_IDS)
    return SECTION_RE.sub(lambda m: m.group(1) + live_hooks, template, count=1)


def build_exemption_registry(with_optional: bool) -> str:
    """生成目标项目的豁免清单种子（§二 标记目录 + §三 空账）。"""
    rows = CORE_MARKERS + (OPTIONAL_MARKERS if with_optional else [])
    lines = [
        "# 豁免清单（Exemption Registry）",
        "",
        "> 更新: YYYY-MM-DD（脚手架初始化）",
        "> 本文件是仓库**豁免使用的唯一登记账**。commit message 用 `[skip-*]` 必须",
        "> 在本次提交中同时修改本文件（追加使用记录），否则 `check_exemption_log.py` 拦截。",
        "",
        "## 一、为什么有这份账",
        "",
        "豁免一旦散落、零登记，强制就名存实亡——本账把豁免变成显式留痕 + 可审计。",
        "本账自身**不可被豁免**。",
        "",
        "## 二、已登记豁免标记（合法标记目录）",
        "",
        "| 豁免标记 | 适用钩子 | 含义 / 何时允许 |",
        "|---------|---------|----------------|",
    ]
    lines += [f"| `{m}` | {hook} | {note} |" for m, hook, note in rows]
    lines += [
        "",
        "## 三、豁免使用记录（每次用豁免追加一行）",
        "",
        "| 日期 | 文件 / 范围 | 钩子 | 豁免标记 | 申请人 | 为何 |",
        "|------|-----------|------|---------|--------|------|",
        "",
    ]
    return "\n".join(lines)


def setup(target: Path, with_optional: bool, force: bool) -> list[str]:
    """执行复制，返回写出的目标相对路径列表。"""
    if target.exists() and any(target.iterdir()) and not force:
        raise SystemExit(
            f"目标目录非空：{target}（用 --force 仍写入，已有同名文件会被覆盖）"
        )
    manifest = CORE_MANIFEST + (OPTIONAL_MANIFEST if with_optional else [])
    written: list[str] = []
    for src_rel, dst_rel in manifest:
        src = REPO_ROOT / src_rel
        if not src.exists():
            raise SystemExit(f"清单源文件缺失：{src_rel}（脚手架与仓库脱钩，先修清单）")
        dst = target / dst_rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        written.append(dst_rel)

    # _meta.yaml：模板骨架 + live 钩子节（按层过滤）
    meta_dst = target / "conventions" / "_meta.yaml"
    meta_dst.write_text(build_meta_yaml(with_optional), encoding="utf-8")

    # 豁免清单种子
    reg = target / "meta" / "豁免清单.md"
    reg.parent.mkdir(parents=True, exist_ok=True)
    reg.write_text(build_exemption_registry(with_optional), encoding="utf-8")
    written.append("meta/豁免清单.md")
    return written


def main() -> int:
    ap = argparse.ArgumentParser(description="复制基准约束基线到新项目")
    ap.add_argument("target", help="目标项目根目录")
    ap.add_argument(
        "--with-optional", action="store_true", help="附带可选层（闸门/模板族/agent）"
    )
    ap.add_argument("--force", action="store_true", help="目标非空也写入")
    args = ap.parse_args()

    target = Path(args.target).resolve()
    written = setup(target, args.with_optional, args.force)

    layer = "必带 + 可选" if args.with_optional else "必带"
    print(f"OK 脚手架已写入 {target}（{layer} 层，共 {len(written)} 个文件）")
    print("")
    print("下一步：")
    print("  1. 编辑 conventions/_meta.yaml（项目名 / 规范列表）")
    print("  2. python scripts/render_meta.py --render pre-commit-config")
    print("  3. git init && pip install pre-commit && pre-commit install")
    print("     && pre-commit install --hook-type commit-msg")
    print("  4. 按 docs/templates/ 模板实例化 CLAUDE.md / STATUS.md / 开发清单.md")
    print("  5. commitlint 需 npm i -D @commitlint/cli @commitlint/config-conventional")
    return 0


if __name__ == "__main__":
    sys.exit(main())
