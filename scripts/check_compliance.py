#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_compliance.py — 合规扫描（#10 任务 v2 实现）
============================================================
读 conventions/_meta.yaml 列出所有规范，对每篇做 L1 配置 + L4 测试检查，
输出文本合规报告。CI stage 4（compliance）会跑这个脚本。

退出码:
    0 = 全部合规
    1 = 有 FAIL

用法:
    python scripts/check_compliance.py            # 文本报告到 stdout
    python scripts/check_compliance.py --json     # JSON 报告
"""

from __future__ import annotations

import argparse
import ast
import configparser
import json
import sys
import tomllib
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
META_FILE = REPO_ROOT / "conventions" / "_meta.yaml"

# 每篇规范的 L1 配置检查：id -> [(相对路径, 说明), ...]
L1_CHECKS: dict[str, list[tuple[str, str]]] = {
    "01-architecture": [
        ("importlinter.ini", "01-architecture L1: importlinter 分层契约"),
    ],
    "02-coding": [
        ("src/coding/ruff.toml", "02-coding L1: ruff lint/format"),
        (".pre-commit-config.yaml", "02-coding L1: gitleaks（密钥扫描）"),
    ],
    "03-git": [
        ("commitlint.config.js", "03-git L1: commitlint config（V0.1 配置就位）"),
        (".gitmessage", "03-git §二: 提交模板"),
        (".github/pull_request_template.md", "03-git §二: PR 模板"),
    ],
    "04-api": [
        (".spectral.yaml", "04-api L1: spectral OpenAPI lint"),
        ("src/api/main.py", "04-api §二: 统一响应 + 错误码示例"),
    ],
    "05-testing": [
        ("pyproject.toml", "05-testing L1: pytest 配置"),
    ],
    "06-documentation": [
        (
            ".markdownlint.json",
            "06-documentation L1: markdownlint 配置（V0.1 配置就位）",
        ),
        ("README.md", "06-documentation 红线 1: README 必含"),
        ("CHANGELOG.md", "06-documentation 红线 2: CHANGELOG 必含"),
    ],
    "08-code-understanding": [
        ("src/code-understanding/call_graph_example.py", "08 L1: AST 调用图示例"),
    ],
}

# 每篇规范的 L4 测试文件：id -> 文件名
L4_CHECKS: dict[str, str] = {
    "01-architecture": "test_01_architecture.py",
    "02-coding": "test_02_coding.py",
    "03-git": "test_03_git.py",
    "04-api": "test_04_api.py",
    "05-testing": "test_05_testing.py",
    "06-documentation": "test_06_documentation.py",
    "07-ai-workflow": "test_07_ai_workflow.py",
    "08-code-understanding": "test_08_code_understanding.py",
}


def validate_artifact(path: Path) -> tuple[bool, str]:
    """Validate that one declared artifact is substantive and parseable."""
    if path.is_dir():
        files = [candidate for candidate in path.rglob("*") if candidate.is_file()]
        return (True, f"目录含 {len(files)} 个文件") if files else (False, "目录为空")
    if not path.is_file():
        return False, "文件缺失"
    try:
        raw = path.read_bytes()
    except OSError as error:
        return False, f"无法读取: {error}"
    if not raw.strip():
        return False, "文件为空"
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as error:
        return False, f"不是 UTF-8: {error}"

    suffix = path.suffix.lower()
    try:
        if suffix in {".yaml", ".yml"}:
            if yaml.safe_load(text) is None:
                return False, "YAML 没有有效内容"
        elif suffix == ".json":
            json.loads(text)
        elif suffix == ".toml":
            tomllib.loads(text)
        elif suffix == ".ini":
            parser = configparser.ConfigParser()
            parser.read_string(text)
            if not parser.sections():
                return False, "INI 没有 section"
        elif suffix == ".py":
            compile(text, str(path), "exec")
        elif suffix == ".md" and not any(
            line.lstrip().startswith("#") for line in text.splitlines()
        ):
            return False, "Markdown 缺标题"
    except (ValueError, SyntaxError, configparser.Error, yaml.YAMLError) as error:
        return False, f"解析失败: {error}"
    return True, "非空且语义可解析"


def contains_test_contract(path: Path) -> tuple[bool, str]:
    """Require at least one real pytest-style test definition."""
    valid, detail = validate_artifact(path)
    if not valid:
        return False, detail
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError) as error:
        return False, f"测试文件解析失败: {error}"
    definitions = [
        node
        for node in ast.walk(tree)
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name.startswith("test_")
    ]
    return (
        (True, f"包含 {len(definitions)} 个 test 定义")
        if definitions
        else (False, "没有真实 test_ 定义")
    )


def load_meta() -> dict:
    """读 _meta.yaml（UTF-8 强制）"""
    if not META_FILE.exists():
        print(f"FAIL: {META_FILE} 不存在", file=sys.stderr)
        sys.exit(1)
    with META_FILE.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def check_convention(conv: dict) -> list[dict]:
    """对单篇规范跑 L1 + L4 检查

    返回 [{"target": "L1", "name": "...", "path": "...", "status": "PASS/FAIL", "msg": "..."}, ...]
    """
    cid = conv.get("id", "")
    file_rel = conv.get("file", "")
    results: list[dict] = []

    # 1. 规范文件存在
    if file_rel:
        path = REPO_ROOT / file_rel
        if path.is_dir():
            results.append(
                {
                    "target": "doc",
                    "name": f"{cid} 规范目录",
                    "path": file_rel,
                    "status": "INFO",
                    "msg": "目录型规范（ai-workflow）：分级在 _meta.yaml，文档不渲染",
                }
            )
        elif path.exists():
            valid, detail = validate_artifact(path)
            results.append(
                {
                    "target": "doc",
                    "name": f"{cid} 规范文件",
                    "path": file_rel,
                    "status": "PASS" if valid else "FAIL",
                    "msg": detail,
                }
            )
        else:
            results.append(
                {
                    "target": "doc",
                    "name": f"{cid} 规范文件",
                    "path": file_rel,
                    "status": "FAIL",
                    "msg": "文件不存在",
                }
            )

    # 2. L1 配置检查
    for rel_path, desc in L1_CHECKS.get(cid, []):
        path = REPO_ROOT / rel_path
        valid, detail = validate_artifact(path)
        results.append(
            {
                "target": "L1",
                "name": desc,
                "path": rel_path,
                "status": "PASS" if valid else "FAIL",
                "msg": detail,
            }
        )

    # _meta.yaml is the authoritative declaration. Validate every declared L1
    # path even when it is not part of the older hard-coded compatibility map.
    grade = conv.get("grade") if isinstance(conv.get("grade"), dict) else {}
    declared = grade.get("l1_check_path", [])
    if isinstance(declared, str):
        declared = [declared]
    already_checked = {relative for relative, _description in L1_CHECKS.get(cid, [])}
    for rel_path in declared if isinstance(declared, list) else []:
        if not isinstance(rel_path, str) or rel_path in already_checked:
            continue
        path = REPO_ROOT / rel_path
        valid, detail = validate_artifact(path)
        results.append(
            {
                "target": "L1",
                "name": f"{cid} _meta 声明的 L1 产物",
                "path": rel_path,
                "status": "PASS" if valid else "FAIL",
                "msg": detail,
            }
        )

    # 3. L4 测试文件
    l4_filename = L4_CHECKS.get(cid)
    if l4_filename:
        l4_path = REPO_ROOT / "tests" / "conventions" / l4_filename
        valid, detail = contains_test_contract(l4_path)
        results.append(
            {
                "target": "L4",
                "name": f"{cid} L4 规范测试",
                "path": f"tests/conventions/{l4_filename}",
                "status": "PASS" if valid else "FAIL",
                "msg": detail,
            }
        )

    return results


def run_compliance() -> dict:
    """跑全部合规检查，返回报告 dict"""
    meta = load_meta()
    conventions = meta.get("conventions", [])
    report = {
        "project": meta.get("project", "unknown"),
        "meta_version": meta.get("version", "?"),
        "conventions_total": len(conventions),
        "results": [],
        "summary": {"pass": 0, "fail": 0, "info": 0},
    }
    for conv in conventions:
        cid = conv.get("id", "?")
        title = conv.get("title", "")
        results = check_convention(conv)
        conv_report = {
            "id": cid,
            "title": title,
            "results": results,
            "status": "PASS" if all(r["status"] != "FAIL" for r in results) else "FAIL",
        }
        report["results"].append(conv_report)
        for r in results:
            if r["status"] == "PASS":
                report["summary"]["pass"] += 1
            elif r["status"] == "FAIL":
                report["summary"]["fail"] += 1
            else:
                report["summary"]["info"] += 1
    return report


def print_text_report(report: dict) -> int:
    """打印文本报告，返回退出码"""
    print("=== 合规扫描报告 ===")
    print(f"项目: {report['project']}  _meta.yaml v{report['meta_version']}")
    print(f"扫描: {report['conventions_total']} 篇规范")
    print(
        f"通过: {report['summary']['pass']}  "
        f"失败: {report['summary']['fail']}  "
        f"信息: {report['summary']['info']}"
    )
    print()
    for conv_report in report["results"]:
        status = conv_report["status"]
        marker = "PASS" if status == "PASS" else "FAIL"
        print(f"[{marker}] {conv_report['id']} {conv_report['title']}")
        for r in conv_report["results"]:
            line = (
                f"    {r['target']:4s} {r['name']:50s} {r['path']:55s} {r['status']:5s}"
            )
            if r["status"] == "FAIL":
                print(f"\033[91m{line}\033[0m  ({r['msg']})")
            elif r["status"] == "INFO":
                print(f"\033[90m{line}\033[0m  ({r['msg']})")
            else:
                print(line)
        print()
    if report["summary"]["fail"] > 0:
        print(f"FAIL: {report['summary']['fail']} 项不通过")
        return 1
    print("OK: 全部合规")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(
        description="扫描 conventions/_meta.yaml 跑合规检查"
    )
    parser.add_argument("--json", action="store_true", help="输出 JSON 报告")
    args = parser.parse_args()
    report = run_compliance()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0 if report["summary"]["fail"] == 0 else 1
    return print_text_report(report)


if __name__ == "__main__":
    sys.exit(main())
