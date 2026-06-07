# 2026-06-07 添加 markdownlint L1 检测（#7 任务）

## 做了什么

- 06 文档规范加 markdownlint L1 检测（pre-commit 钩子）
- 用 pymarkdownlnt（pip 安装，避免 npm 依赖）
- 配置 `.markdownlint.json`（root 目录）
- render_meta.py 渲染到 .pre-commit-config.yaml
- L4 test_06_documentation.py 加 markdownlint 配置检查

## 验证

- pre-commit 钩子全 Passed
- pytest tests/conventions/ 51 passed
- check_worklog_ref 钩子拦截验证（带/不带 worklog 引用）

## 关键决策

- 用 Python 工具（pymarkdownlnt）而非 Node 工具（markdownlint-cli）—— 避免项目引入 package.json + npm 依赖
- L4 测试验证"配置就位 + 钩子在 .pre-commit-config.yaml"——不强求 markdownlint 真的拦下所有违规

## 交接

- 下一步 #9 html-report-template + dashboard 改造
