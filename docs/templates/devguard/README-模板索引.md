# 模板索引（devguard）

> V0.1 期间已写，V0.2 清理 untracked 后丢失，V8.2 重建
> 维护者: 袁 (xiangbianpangde) | 重建: 2026-06-07

## 模板目录

```
docs/templates/devguard/
├── .github/                  # GitHub Actions workflow 模板（lint + test + ci）
├── .markdownlint.json        # markdownlint 配置（V3.1 启用）
├── .markdownlintignore       # markdownlint 排除（cli 兜底）
├── conventions/              # 8 篇规范模板（01-08 + ai-workflow/）
├── html-report-template/     # 仪表盘模板（render.py + index.html + README）
├── importlinter.ini          # 01-architecture 架构分层契约
├── scripts/                  # L1 检测脚本（V5+ 推广）
│   ├── check_ai_workflow.py  # 07 章节级 L1
│   ├── check_code_understanding.py  # 08 章节级 L1
│   ├── collect_l4_stats.py   # V6.3 L4 自动收集
│   ├── check_worklog_ref.py  # 03-git worklog 引用
│   ├── check_compliance.py   # 阶段 4 合规扫描
│   ├── lint_markdown.py      # V3.1 markdown 包装
│   └── render_meta.py        # 真源 -> 产物渲染
└── src/                      # 示例代码（V0.3 后清理 src/coding/）
    └── coding/ruff.toml      # ruff 全配置（V0.3 同步）
```

## 模板使用流程

1. **复制 `docs/templates/devguard/` 到新项目**
2. **替换真源**：把 `conventions/_meta.yaml` + `STATUS.md` 改成新项目内容
3. **跑渲染**：`python scripts/render_meta.py --render all` 生成 `.pre-commit-config.yaml`
4. **装 hook**：`pre-commit install --hook-type commit-msg`
5. **CI**：把 `.github/workflows/ci.yml` 复制到新项目
6. **L1 检测**：复制 `scripts/check_*.py` 到新项目

## 版本对应

- V0.1 期间：初始 5 个钩子 + 5 阶段 CI + 35 个功能点
- V0.3 重构：8 规范齐全 + 10 钩子 pre-commit
- V0.8 重建：本 README + 11 个 scripts/ 脚本
