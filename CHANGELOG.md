# Changelog

所有项目的显著变更都会记录在此。格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)。

## [Unreleased]

### Added
- L1 + L3 双层防御（pre-commit 钩子 + conventions/_meta.yaml 真源）
- 5 阶段 GitHub Actions CI 流水线
- L4 规范测试（tests/conventions/，覆盖 01-architecture 等 5 篇）
- devguard 双轨模板（docs/templates/devguard/）

### Changed
- 整合 10 条用户跨项目偏好到规范（02/05/06/ai-workflow/04/CLAUDE.md）

### Fixed
- 修复 src/api/main.py E402（import 移至顶部）
- 补全 src/coding/ruff.toml per-file-ignores（教学反例豁免）
- 加 src/coding/ruff.toml tests/**/*.py S101 豁免（pytest 用 assert）

### Deprecated
- 暂无

### Removed
- 暂无

### Security
- gitleaks 接入 pre-commit（密钥扫描）
