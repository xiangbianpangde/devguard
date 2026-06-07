"""L4 规范测试 — _meta.yaml 元一致性

验证 conventions/_meta.yaml 里所有 8 规范都有 l1_check 字段且非空。
V4.1 启用：扩展 L1 检测配置到所有规范后必须保留非空 l1_check 字段。
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
META = REPO_ROOT / "conventions" / "_meta.yaml"

# 9 篇规范期望 ID（与 _meta.yaml 一致，V6.2 加 09-dashboard-gen）
EXPECTED_IDS = {
    "01-architecture",
    "02-coding",
    "03-git",
    "04-api",
    "05-testing",
    "06-documentation",
    "07-ai-workflow",
    "08-code-understanding",
    "09-dashboard-gen",
    "10-templates-reporting",
}


class TestMetaL1Check:
    """_meta.yaml §1 conventions 列表的 L1 检测字段一致性"""

    def _load(self) -> dict:
        return yaml.safe_load(META.read_text(encoding="utf-8"))

    def test_meta_yaml_loads(self):
        """_meta.yaml 必须能解析为 YAML"""
        meta = self._load()
        assert "conventions" in meta, "_meta.yaml 缺 conventions 字段"
        assert isinstance(meta["conventions"], list)
        assert (
            len(meta["conventions"]) >= 8
        ), f"conventions 数量 < 8（实际 {len(meta['conventions'])}）"

    def test_every_convention_has_l1_check(self):
        """红线：每篇规范必须有 l1_check 字段（V4.1 强制）"""
        meta = self._load()
        for c in meta["conventions"]:
            cid = c.get("id", "?")
            assert "l1_check" in c, f"规范 {cid} 缺 l1_check 字段（V4.1 红线）"
            value = c["l1_check"]
            assert isinstance(value, str), f"规范 {cid} l1_check 非字符串"
            assert value.strip(), f"规范 {cid} l1_check 为空（V4.1 红线）"

    def test_convention_ids_complete(self):
        """所有 8 篇规范 ID 必须齐全"""
        meta = self._load()
        actual_ids = {c.get("id") for c in meta["conventions"]}
        missing = EXPECTED_IDS - actual_ids
        assert not missing, f"缺规范: {missing}"

    def test_l1_check_no_placeholder(self):
        """l1_check 字段不能是 TODO/FIXME/待定等占位符"""
        placeholders = {"todo", "fixme", "tbd", "待定", "待补", "占位", "n/a"}
        meta = self._load()
        for c in meta["conventions"]:
            cid = c.get("id", "?")
            value = c.get("l1_check", "").strip().lower()
            assert (
                value not in placeholders
            ), f"规范 {cid} l1_check 是占位符 {value!r}（V4.1 强制：必须有真实 tool）"

    def test_l1_check_doc_url_format(self):
        """V8.1 增强：l1_check_doc 是 URL（https:// 开头）—— V8.1 增强可发现性"""
        meta = self._load()
        for c in meta["conventions"]:
            cid = c.get("id", "?")
            if "l1_check_doc" not in c:
                continue  # 可选字段（V8.1 试点 6 篇已加，其他 4 篇后续推广）
            url = c["l1_check_doc"]
            assert isinstance(url, str), f"规范 {cid} l1_check_doc 非 str"
            assert url.startswith(
                "https://"
            ), f"规范 {cid} l1_check_doc={url!r} 不以 https:// 开头"

    @pytest.mark.parametrize(
        "conv_id,expected_tool_substr",
        [
            ("01-architecture", "importlinter"),
            ("02-coding", "ruff"),
            ("03-git", "commitlint"),
            ("04-api", "spectral"),
            ("05-testing", "pytest"),
            ("06-documentation", "markdownlint"),
        ],
    )
    def test_l1_check_contains_expected_tool(self, conv_id, expected_tool_substr):
        """关键规范的 l1_check 字段必须含期望的 L1 tool 名称（V4.1 一致性）"""
        meta = self._load()
        c = next((x for x in meta["conventions"] if x.get("id") == conv_id), None)
        assert c is not None, f"规范 {conv_id} 不在 _meta.yaml"
        value = c.get("l1_check", "")
        assert (
            expected_tool_substr in value
        ), f"规范 {conv_id} l1_check={value!r} 不含 {expected_tool_substr!r}"

    def test_l1_check_path_is_optional(self):
        """V5.1 增强：grade.l1_check_path 是可选字段（V5.1 推广中），缺失不报错"""
        # 现状：01-architecture 已加 l1_check_path；其他 6 篇未加（V5.x 逐步推广）
        # 字段存在时必须为 list[str] + 所有路径实际存在；字段缺失则跳过
        meta = self._load()
        for c in meta["conventions"]:
            cid = c.get("id", "?")
            grade = c.get("grade", {})
            if "l1_check_path" not in grade:
                continue  # 可选字段
            paths = grade["l1_check_path"]
            assert isinstance(paths, list), f"规范 {cid} l1_check_path 非 list"
            for p in paths:
                assert isinstance(p, str), f"规范 {cid} l1_check_path 元素非 str"
                target = REPO_ROOT / p
                assert target.exists(), f"规范 {cid} l1_check_path 路径 {p!r} 不存在"
