"""L4 规范测试 — 04-api

对照 conventions/04-api_API设计规范.md §一 红线 1-7：
1. 资源用名词复数 + kebab-case → spectral
2. 响应统一 code/message/data → 响应拦截器
3. HTTP 状态码与 body code 一致 → 审查
4. 错误码唯一、废弃不复用 → 错误码表
5. 默认认证 → 中间件
6. 输入严格校验 → pydantic / zod
7. 向后兼容（不删/不重命名字段）→ spectral diff
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
SPECTRAL = REPO_ROOT / ".spectral.yaml"
API_MAIN = REPO_ROOT / "src" / "api" / "main.py"
CONV_04 = REPO_ROOT / "conventions" / "04-api_API设计规范.md"


class TestApiContracts:
    """04-api §一 红线 1-7 的 L4 检测"""

    def test_spectral_config_exists(self):
        """红线 1/7：.spectral.yaml 必须存在（OpenAPI lint 工具配置）"""
        assert SPECTRAL.exists(), f".spectral.yaml 缺失（{SPECTRAL}）"

    def test_spectral_rule_path_kebab(self):
        """红线 1：spectral 必须含 path-kebab-case 规则（kebab-case 路径）"""
        content = SPECTRAL.read_text(encoding="utf-8")
        assert "path-kebab-case" in content, ".spectral.yaml 缺 path-kebab-case 规则（红线 1）"

    def test_spectral_rule_no_verb(self):
        """红线 1：spectral 必须含 no-verb-in-path 规则（URL 无动词）"""
        content = SPECTRAL.read_text(encoding="utf-8")
        assert (
            "no-verb-in-path" in content
        ), ".spectral.yaml 缺 no-verb-in-path 规则（红线 1：URL 不含动词）"

    def test_spectral_rule_response_data(self):
        """红线 2：spectral 必须有响应必含 data 字段的规则（统一响应结构）"""
        content = SPECTRAL.read_text(encoding="utf-8")
        assert (
            "data" in content
        ), ".spectral.yaml 缺 data 字段强制（红线 2：统一响应 code/message/data）"

    @pytest.mark.skipif(not API_MAIN.exists(), reason="src/api/main.py 不存在")
    def test_unified_response_shape_in_code(self):
        """红线 2：src/api/main.py 必须演示统一响应结构（code/message/data）"""
        content = API_MAIN.read_text(encoding="utf-8")
        # 检查 ApiResponse 模型含 code/message/data
        assert (
            "code" in content and "message" in content and "data" in content
        ), "src/api/main.py 缺统一响应结构演示（红线 2：code/message/data）"
        # 检查 pydantic BaseModel
        assert "BaseModel" in content, "src/api/main.py 应使用 pydantic BaseModel 演示响应结构"

    @pytest.mark.skipif(not API_MAIN.exists(), reason="src/api/main.py 不存在")
    def test_error_code_pattern_in_code(self):
        """红线 3/4：src/api/main.py 应演示错误码体系（40401 / 40001 / 40901 等）"""
        content = API_MAIN.read_text(encoding="utf-8")
        # 5 位错误码（项目/模块/序号）
        assert re.search(r"\b\d{5}\b", content), "src/api/main.py 应演示 5 位错误码体系（红线 3/4）"

    def test_backward_compat_in_spec(self):
        """红线 7：04 §二 落地必须提到向后兼容（spectral diff + 审查）"""
        content = CONV_04.read_text(encoding="utf-8")
        assert (
            "向后兼容" in content or "不删" in content or "不重命名" in content
        ), "04 §二 落地缺向后兼容指引（红线 7）"
