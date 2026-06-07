#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_meta.py — 把 conventions/_meta.yaml 投射到下游产物
=========================================================
最小版（#1 任务）：只支持 pre-commit-config 渲染和校验
后续任务（#4 / #3 / #2）会扩展支持 convention-grade 渲染（把分级标签
投射到每篇规范顶部的 ## 分级标签 小节）。

用法:
    python scripts/render_meta.py --render                       # 渲染所有产物
    python scripts/render_meta.py --render pre-commit-config     # 只渲染 pre-commit
    python scripts/render_meta.py --check                        # 校验所有产物（CI 用）
    python scripts/render_meta.py --check pre-commit-config      # 校验单个 target

退出码:
    0 = 成功 / 一致
    1 = 渲染失败（_meta.yaml 读不出 / 字段缺失）
    2 = 校验失败（产物与真源不一致）→ CI fail

依赖:
    pip install pyyaml
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: 缺 pyyaml。安装: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

REPO_ROOT = Path(__file__).resolve().parent.parent
META_FILE = REPO_ROOT / "conventions" / "_meta.yaml"
PRE_COMMIT_CONFIG = REPO_ROOT / ".pre-commit-config.yaml"

# 钩子按 source 分组时，pre-commit/pre-commit-hooks 要排在最前（先做最便宜的检查）
HOOK_SORT_PRIORITY = {
    "pre-commit/pre-commit-hooks": 0,
}


def load_meta() -> dict:
    """读 _meta.yaml（UTF-8 强制，避免 Windows ANSI 损坏中文）"""
    if not META_FILE.exists():
        print(f"FAIL: 真源不存在: {META_FILE}", file=sys.stderr)
        sys.exit(1)
    with META_FILE.open(encoding="utf-8") as f:
        meta = yaml.safe_load(f)
    if not isinstance(meta, dict):
        print("FAIL: _meta.yaml 解析后不是字典结构", file=sys.stderr)
        sys.exit(1)
    if "pre_commit" not in meta:
        print("FAIL: _meta.yaml 缺 pre_commit 节", file=sys.stderr)
        sys.exit(1)
    return meta


def render_pre_commit_config(meta: dict) -> str:
    """从 meta['pre_commit'] 渲染 .pre-commit-config.yaml 内容"""
    # 按 source 分组
    repos: dict[str, dict] = {}
    for hook in meta["pre_commit"]:
        if not all(k in hook for k in ("id", "source", "rev")):
            raise ValueError(f"pre_commit 钩子缺字段: {hook.get('id', '<unknown>')}")
        repo_key = hook["source"]
        if repo_key not in repos:
            repos[repo_key] = {
                "repo": f"https://github.com/{repo_key}",
                "rev": hook["rev"],
                "hooks": [],
            }
        hook_def: dict = {"id": hook["id"]}
        for k in ("args", "stages", "config"):
            if k in hook:
                hook_def[k] = hook[k]
        repos[repo_key]["hooks"].append(hook_def)

    # 排序：pre-commit-hooks 优先，其他按字母
    def sort_key(r: dict) -> tuple:
        src = r["repo"].removeprefix("https://github.com/")
        priority = HOOK_SORT_PRIORITY.get(src, 1)
        return (priority, src)

    repo_list = sorted(repos.values(), key=sort_key)

    # 渲染
    lines: list[str] = [
        "# ============================================================",
        "# .pre-commit-config.yaml",
        "# ============================================================",
        "# 渲染产物（DO NOT EDIT） — 由 scripts/render_meta.py 从 conventions/_meta.yaml 自动生成",
        "# 修改流程：改 conventions/_meta.yaml → 跑 render_meta.py --render",
        "# 不要手改本文件！手改会被 render_meta.py --check 检测到（CI fail）",
        "# ============================================================",
        "# 对应规范: 02-coding 红线 1/4/5, 03-git 红线 2",
        "# 安装: pip install pre-commit && pre-commit install --hook-type commit-msg",
        "# ============================================================",
        "repos:",
    ]
    for repo in repo_list:
        lines.append(f"  - repo: {repo['repo']}")
        lines.append(f"    rev: {repo['rev']}")
        lines.append("    hooks:")
        for hook in repo["hooks"]:
            lines.append(f"      - id: {hook['id']}")
            if "args" in hook:
                args_str = ", ".join(f"'{a}'" for a in hook["args"])
                lines.append(f"        args: [{args_str}]")
            if "stages" in hook:
                stages_str = ", ".join(hook["stages"])
                lines.append(f"        stages: [{stages_str}]")
            if "config" in hook:
                lines.append(f"        config: {hook['config']}")
        lines.append("")

    return "\n".join(lines)


def render_convention_grade_section(conv: dict) -> str:
    """生成单篇规范的 ## 分级标签 小节（markdown 块）

    插入位置：每篇规范第一个 # 标题之前
    渲染纪律：本节由 render_meta.py 维护，手改会被 --check 检测到（CI fail）
    """
    grade = conv.get("grade", {})
    l1_check = conv.get("l1_check", "")
    l3_route = conv.get("l3_route", "")

    lines: list[str] = [
        "## 分级标签",
        "",
        "> 本节为**渲染产物**（由 render_meta.py 从 _meta.yaml 自动生成）。",
        "> 修改流程：改 `conventions/_meta.yaml` → 跑 `render_meta.py --render convention-grade`。",
        "> **不要手改本节**（手改会被 `render_meta.py --check` 检测到，CI fail）。",
        "",
        "| 级别 | 数量 |",
        "|------|------|",
        f"| 红线 | {grade.get('red_line', 0)} |",
        f"| 警告 | {grade.get('warning', 0)} |",
        f"| 推荐 | {grade.get('recommend', 0)} |",
        "",
    ]
    if l1_check:
        lines.append(f"**L1 检测**：{l1_check}")
    if l3_route:
        lines.append(f"**L3 路由**：{l3_route}")
    lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def _strip_existing_grade_section(content: str) -> tuple[str, bool]:
    """如果原文件已有 ## 分级标签 小节，先剥离（幂等渲染）"""
    marker = "## 分级标签"
    if marker not in content:
        return content, False
    # 找到 marker 位置
    idx = content.index(marker)
    # 找到 marker 之后第一个 `---` 分隔符
    after_marker = content[idx:]
    sep_idx = after_marker.find("\n---\n")
    if sep_idx == -1:
        return content[:idx], True
    # 剥离从 marker 到 --- 结束的部分（包含 --- 之后的一个空行）
    end = idx + sep_idx + len("\n---\n")
    return content[:idx] + content[end:], True


def render_convention_grade(meta: dict) -> list[Path]:
    """对每篇规范渲染 ## 分级标签 小节，in-place 写回

    返回写入的文件路径列表
    """
    written: list[Path] = []
    for conv in meta.get("conventions", []):
        file_rel = conv.get("file", "")
        if not file_rel:
            continue
        path = REPO_ROOT / file_rel
        if path.is_dir():
            # 目录型规范（如 ai-workflow）：分级存在 _meta.yaml 即可，文档不渲染
            print(f"SKIP 目录型规范（分级在 _meta.yaml，文档不渲染）: {file_rel}")
            continue
        if not path.exists():
            print(f"SKIP 规范文件不存在: {file_rel}", file=sys.stderr)
            continue
        content = path.read_text(encoding="utf-8")
        # 幂等：先剥离已有的
        content, _ = _strip_existing_grade_section(content)
        # 找到第一个 # 标题（顶级标题）位置
        lines = content.splitlines()
        insert_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("# ") and not line.startswith("#!"):
                insert_idx = i
                break
        # 生成新小节
        new_section = render_convention_grade_section(conv)
        new_lines = lines[:insert_idx] + new_section.splitlines() + lines[insert_idx:]
        new_content = "\n".join(new_lines)
        # 写回（newline="\n" 统一为 LF，避免 Windows CRLF 影响 check 一致性）
        path.write_text(new_content, encoding="utf-8", newline="\n")
        written.append(path)
    return written


def render_target(target: str, meta: dict) -> list[Path] | None:
    """渲染指定 target，返回写入的文件路径列表；不支持的 target 返回 None"""
    if target == "pre-commit-config":
        content = render_pre_commit_config(meta)
        PRE_COMMIT_CONFIG.write_text(content, encoding="utf-8")
        return [PRE_COMMIT_CONFIG]
    if target == "convention-grade":
        return render_convention_grade(meta)
    return None


def check_target(target: str, meta: dict) -> tuple[bool, str]:
    """校验指定 target 与 _meta.yaml 一致；返回 (ok, msg)"""
    if target == "pre-commit-config":
        if not PRE_COMMIT_CONFIG.exists():
            return False, f"{PRE_COMMIT_CONFIG.name} 不存在（跑 --render 生成）"
        try:
            expected = render_pre_commit_config(meta)
            actual = PRE_COMMIT_CONFIG.read_text(encoding="utf-8")
            if expected != actual:
                return False, (
                    f"{PRE_COMMIT_CONFIG.name} 与 _meta.yaml 不一致。"
                    f"修复: python scripts/render_meta.py --render pre-commit-config"
                )
            return True, f"{PRE_COMMIT_CONFIG.name} 与 _meta.yaml 一致"
        except Exception as e:
            return False, f"渲染真源失败: {e}"
    if target == "convention-grade":
        mismatches: list[str] = []
        for conv in meta.get("conventions", []):
            file_rel = conv.get("file", "")
            if not file_rel:
                continue
            path = REPO_ROOT / file_rel
            if path.is_dir():
                continue
            if not path.exists():
                mismatches.append(f"规范文件不存在: {file_rel}")
                continue
            content = path.read_text(encoding="utf-8")
            content_stripped, _ = _strip_existing_grade_section(content)
            expected_section = render_convention_grade_section(conv)
            lines = content_stripped.splitlines()
            insert_idx = 0
            for i, line in enumerate(lines):
                if line.startswith("# ") and not line.startswith("#!"):
                    insert_idx = i
                    break
            expected_full = "\n".join(
                lines[:insert_idx] + expected_section.splitlines() + lines[insert_idx:]
            )
            if content != expected_full:
                mismatches.append(
                    f"{path.relative_to(REPO_ROOT)} 的 ## 分级标签 与 _meta.yaml 不一致"
                )
        if mismatches:
            return False, (
                "; ".join(mismatches)
                + " 修复: python scripts/render_meta.py --render convention-grade"
            )
        return True, "所有规范的 ## 分级标签 与 _meta.yaml 一致"
    return False, f"未知 target: {target}"


def main() -> int:
    parser = argparse.ArgumentParser(
        description="把 conventions/_meta.yaml 投射到下游产物（pre-commit-config 等）"
    )
    parser.add_argument(
        "--render",
        nargs="?",
        const="all",
        help="渲染产物（默认 all；可指定 target 名，如 pre-commit-config）",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="校验产物是否与 _meta.yaml 一致（CI 用）",
    )
    args = parser.parse_args()

    if not args.render and not args.check:
        parser.print_help()
        return 1

    try:
        meta = load_meta()
    except yaml.YAMLError as e:
        print(f"FAIL: _meta.yaml YAML 解析失败: {e}", file=sys.stderr)
        return 1

    # 确定要处理的 target 列表
    if args.render:
        if args.render == "all":
            targets = ["pre-commit-config"]  # 后续 #4 / #3 会加 convention-grade
        else:
            targets = [args.render]
        exit_code = 0
        for target in targets:
            try:
                paths = render_target(target, meta)
            except Exception as e:
                print(f"FAIL 渲染 {target} 失败: {e}", file=sys.stderr)
                exit_code = 1
                continue
            if paths is None:
                print(f"SKIP 未实现的 target: {target}", file=sys.stderr)
                continue
            for path in paths:
                try:
                    rel = path.relative_to(REPO_ROOT)
                except ValueError:
                    rel = path
                print(f"OK 渲染 → {rel}")
        return exit_code

    if args.check:
        targets = ["pre-commit-config", "convention-grade"]  # 加 convention-grade 校验
        ok_count = 0
        for target in targets:
            ok, msg = check_target(target, meta)
            if ok:
                print(f"OK {msg}")
                ok_count += 1
            else:
                print(f"FAIL {msg}", file=sys.stderr)
        if ok_count == len(targets):
            return 0
        return 2

    return 1


if __name__ == "__main__":
    sys.exit(main())
