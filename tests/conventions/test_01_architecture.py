"""L4 规范测试 — 01-architecture

对照 conventions/01-architecture_架构设计规范.md §一 红线：
1. 禁止循环依赖 — importlinter forbidden 契约
2. 领域层不依赖框架 — importlinter layers + forbidden 契约
3. 禁止跨层调用 — importlinter layers 契约
4. 敏感配置禁止硬编码 — 见 02-coding §一 红线 3（本测试不去重）

检测策略：AST 静态分析（不实际 import 模块，避免 sys.path 问题）
"""

from __future__ import annotations

import configparser
import re
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
ARCH_ROOT = REPO_ROOT / "src" / "architecture"
IMPORTLINTER_INI = REPO_ROOT / "importlinter.ini"

# 领域层禁止的框架/ORM（对照 01-architecture §一 红线 2）
FORBIDDEN_FRAMEWORKS = frozenset(
    {
        "fastapi",
        "sqlalchemy",
        "django",
        "flask",
        "tornado",
        "starlette",
        "pydantic",
        "peewee",  # 严格定义下也视为 ORM 框架依赖
    }
)

# 分层顺序：上层 → 下层（依赖方向单向向下）
LAYER_ORDER = ["presentation", "application", "domain", "infrastructure"]


def _read_imports(py_file: Path) -> list[str]:
    """从 .py 文件提取所有 import 的模块名（不实际 import）"""
    content = py_file.read_text(encoding="utf-8")
    imports = []
    # 匹配 import X / from X import Y
    for match in re.finditer(r"^\s*(?:from|import)\s+([\w.]+)", content, re.MULTILINE):
        imports.append(match.group(1))
    return imports


class TestArchitectureContracts:
    """01-architecture §一 红线的 L4 检测"""

    def test_importlinter_config_exists(self):
        """L1 检测工具 importlinter.ini 必须存在（红线 1/2/3 的载体）"""
        assert (
            IMPORTLINTER_INI.exists()
        ), f"importlinter.ini 缺失（{IMPORTLINTER_INI}）—— 架构分层契约无法自动验证"

    def test_importlinter_layers_contract_defined(self):
        """红线 3：分层单向依赖契约（type=layers）必须定义"""
        config = configparser.ConfigParser()
        config.read(IMPORTLINTER_INI, encoding="utf-8")
        layers_contracts = [
            section
            for section in config.sections()
            if section.startswith("importlinter:contract:")
            and config.get(section, "type", fallback="") == "layers"
        ]
        assert (
            layers_contracts
        ), "importlinter.ini 缺 layers 契约（红线 3 跨层调用无自动检测）"

    def test_importlinter_domain_pure_contract_defined(self):
        """红线 2：领域层不依赖框架（type=forbidden）契约必须定义"""
        config = configparser.ConfigParser()
        config.read(IMPORTLINTER_INI, encoding="utf-8")
        forbidden_contracts = [
            section
            for section in config.sections()
            if section.startswith("importlinter:contract:")
            and config.get(section, "type", fallback="") == "forbidden"
        ]
        assert (
            forbidden_contracts
        ), "importlinter.ini 缺 forbidden 契约（红线 2 领域纯净无自动检测）"

    @pytest.mark.skipif(not ARCH_ROOT.exists(), reason="src/architecture/ 不存在，跳过")
    def test_domain_layer_pure_in_source(self):
        """红线 2：src/architecture/domain/ 实际代码不 import 框架/ORM

        静态分析（不实际 import 模块）—— 即使 src/ 不在 sys.path 也能跑
        """
        domain_dir = ARCH_ROOT / "domain"
        for py_file in domain_dir.rglob("*.py"):
            imports = _read_imports(py_file)
            for imp in imports:
                top_module = imp.split(".")[0]
                if top_module in FORBIDDEN_FRAMEWORKS:
                    pytest.fail(
                        f"{py_file.relative_to(REPO_ROOT)} 引用了禁止模块 "
                        f"'{imp}'（红线 2：领域层不依赖框架）"
                    )

    @pytest.mark.skipif(not ARCH_ROOT.exists(), reason="src/architecture/ 不存在，跳过")
    def test_no_upward_layer_imports(self):
        """红线 3：下层不反向引用上层（domain 不 import application/presentation 等）

        检查 domain/ 和 infrastructure/ 不会 import presentation/ 或 application/
        """
        for layer_name in ("domain", "infrastructure"):
            layer_dir = ARCH_ROOT / layer_name
            if not layer_dir.exists():
                continue
            for py_file in layer_dir.rglob("*.py"):
                imports = _read_imports(py_file)
                for imp in imports:
                    # 检查 imp 是否含 src.architecture.<上层>
                    for upper_layer in ("presentation", "application"):
                        if f"src.architecture.{upper_layer}" in imp or imp.endswith(
                            f".{upper_layer}"
                        ):
                            # 排除同层（domain 引用 domain OK）
                            if upper_layer != layer_name:
                                pytest.fail(
                                    f"{py_file.relative_to(REPO_ROOT)} 引用了上层 "
                                    f"'{imp}'（红线 3：禁止跨层调用 / 反向依赖）"
                                )
