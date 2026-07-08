# 2026-07-07 · pyproject 依赖声明 + 版本号对齐 V2.0.1

> 关联：工程结构优化 P1-1（依赖声明）
> Commit：待填入

## 完成了什么

- [x] `pyproject.toml` 新增 `[project]` + `[project.optional-dependencies.dev]`（pyyaml 核心依赖 + pytest/pytest-cov/ruff/coverage/pre-commit 开发依赖）
- [x] `package.json` 版本号 `0.1.0 → 2.0.1`，描述对齐"通用开发规范 V2.0.1"
- [x] `requires-python >=3.10`（CI 用 3.11，兼容）

## 关键决策

- **pyyaml 划为核心运行依赖**：`render_meta.py` / `check_compliance.py` 运行时需要
- **pytest/ruff 等划为 dev 可选依赖**：仅开发时需要，`pip install -e ".[dev]"` 装齐
- **版本号对齐**：package.json 历史遗留 V0.1 口径，对齐 README/CLAUDE 的 V2.0.1

## 下一步

- [ ] P1-2：加 `requirements-dev.txt` 锁文件（固定 ruff 等版本，避免本地 0.15 vs CI 0.6 漂移）
- [ ] P1-3：`dashboard.html` 的 L4 硬编码改 `collect_l4_stats.py` 自动收集
