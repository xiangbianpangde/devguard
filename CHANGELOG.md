# Changelog

All notable changes to devguard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [V1.0] - 2026-06-07

### Added

- **12-codeowners 规范入 _meta.yaml**（V1.1）—— GitHub 自动审查分配
- **10 篇 l1_check_doc 字段**（V8.1）—— 每篇规范指向 L1 tool 官方文档 URL
- **11-readme 规范入 _meta.yaml**（V9.2）—— README 章节级 L1
- **10-templates-reporting 规范入 _meta.yaml**（V7.1）—— 模板 + reports/ 目录
- **09-dashboard-gen 规范入 _meta.yaml**（V6.2）—— 仪表盘模板 + 渲染脚本
- **grade.l1_check_path 字段**（V5.1）—— 6 篇规范 + L4 自动验证
- **章节级 L1 钩子**（V5.2 + V5.3）—— check_ai_workflow.py + check_code_understanding.py
- **dashboard.html CSP**（V5.4）—— `<meta http-equiv="Content-Security-Policy">` 防 XSS
- **render-mtime 自我刷新标识**（V5.5）—— `<meta name="render-mtime">` 字段
- **L4 元一致性测试**（V4.4）—— test_meta_l1_check.py 10 tests
- **L4 性能基线**（V2.5）—— test_perf_baseline.py 2.69s × 1.5 容忍
- **dashboard 字段同步**（V4.2）—— 53/53 实际值
- **markdownlint 钩子**（V3.1）—— 10 钩子 pre-commit
- **dashboard.html 整体切换**（V3.2）—— 100% (35/35) + 32 红线
- **gitleaks 手动跑**（V3.3）—— 绕开 v2 cache drift
- **commitlint 启用**（V2.3 / V0.2）—— npm @commitlint/cli
- **end-of-file-fixer**（V2.1）—— 统一 LF newline
- **render_meta.py 双轨同步**（V2.1）—— 模板版与主仓同步
- **core.autocrlf=false**（V2.1）—— 跨平台 newline 一致
- **src/coding/ruff.toml per-file-ignores**（V2.1）—— 测试 + 工具脚本豁免
- **scripts/check_worklog_ref.py**（V0.1）—— commit-msg worklog 引用强制

### Fixed

- **render.py 数据 bug**（V3.2）—— BDD 字符串 check 误跳数据行 + 跨节表格错收
- **render_date 跨平台**（V3.3）—— 改 static `latest` 彻底幂等
- **render.py 写文件强制 LF**（V3.3）—— CRLF→LF 跨平台一致
- **L4 自动收集 L4 数字**（V6.3 + V7.2 retry）—— V6.3 失败 + V7.2 找到 bash `VAR=空变无参` 根因
- **07-ai-workflow §一 红线扩展**（V9.1）—— 7 篇每篇 §一 红线验证
- **02-第零步_调研.md §一 红线缺口**（V9.1）—— 补"调研 4 问"段
- **docs/templates/devguard/README-模板索引.md 重建**（V8.2）—— V0.2 清理后丢失
- **dashboard.html 53/53 硬编码 → 真实值**（V4.2）
- **commitlint subject-case**（V0.2）—— L1 → l1
- **commit-msg-worklog-ref**（V0.2+）—— 强制 worklog 引用
- **render.py ruff S603/S607**（V0.2 修订）—— 豁免
- **render.py 缺 import subprocess**（V0.3 修订）—— 加 import
- **render.py 缺 subprocess 真实 import**（V0.3）—— 验证 sys.path

### Changed

- **dashboard.html 渲染模板**（V0.1 → V1.0）—— 从手写硬编码到模板化渲染
- **CI 5 阶段流水线**（V0.1）—— lint / test / l4-conventions / compliance / build
- **9 钩子 → 10 钩子**（V0.1 → V0.3）—— 加 markdownlint
- **8 规范 → 12 规范**（V0.1 → V1.0）—— 累计加 09/10/11/12
- **L4 套件 53 → 65 tests**（V0.1 → V0.9）

### Removed

- 无（V0.1 → V1.0 纯增量演进）

### Security

- **dashboard.html CSP**（V5.4）—— `<meta http-equiv="Content-Security-Policy">` 防 XSS
- **gitleaks 手动跑**（V3.3）—— 绕开 v2 cache drift 误报
- **CODEOWNERS**（V1.1）—— GitHub 自动审查分配

## [V0.1] - 2026-05-27

### Added

- 8 规范（01-08）+ ai-workflow 7 篇流程文档
- 9 钩子 pre-commit（trim whitespace / end-of-file-fixer / yaml / json / large files / ruff / ruff-format / gitleaks / commit-msg-worklog-ref）
- 5 阶段 CI（lint / test / l4-conventions / compliance / build）
- 35 个功能点 + 32 红线
- 33 L4 套件（初版）
- importlinter.ini（01-architecture 架构分层契约）
- scripts/check_compliance.py（合规扫描）
- scripts/render_meta.py（真源 → 产物渲染）
- 33 功能点
- docs/templates/devguard/ 双轨模板（html-report-template + importlinter + scripts）

### Security

- gitleaks 钩子（v0.1 用 gitleaks-action@v2）
- 教学反例 allowlist（src/coding/security_demo.py 等）
- commit-msg-worklog-ref 强制 worklog 引用

[V1.0]: ./收束报告-v1.0.md（待写）
[V0.1]: ./收束报告-v0.1.md
