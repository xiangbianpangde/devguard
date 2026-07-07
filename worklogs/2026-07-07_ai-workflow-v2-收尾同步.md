# 2026-07-07 · ai-workflow v2.0 重写收尾同步

> 关联：设计提案-devguard一致性修复与工程优化.md（P0）
> Commit：待填入

## 完成了什么

- [x] `conventions/_meta.yaml`：07 recommend 7→9；09/10 file 改目录（避免 render 给流程文档插分级标签）；mem-workflow-001 target → 04-长程开发
- [x] `tests/conventions/test_07_ai_workflow.py`：重写为 9 篇 + README 的 11 个断言
- [x] `scripts/check_ai_workflow.py` + 模板版本：EXPECTED_FILES_AND_KEYWORDS 新 9 篇 §一 关键词
- [x] 19 个文件交叉引用同步（规范正文 01-06,08 + CLAUDE/STATUS/FILE_GRAPH/导航/模板/specs/开发清单）
- [x] `meta/FILE_GRAPH.md` 目录树重写为新 9 篇 + README
- [x] `CLAUDE.md` 工作流程段重写（旧步骤式 → 新双轨制 + 端到端）
- [x] 删除 render 误插入 08-汇报收束.md 的分级标签残留

## 验证

render --check ✅ / pytest 69 passed ✅ / check_ai_workflow 9 篇 ✅ / compliance ✅ / ruff ✅ / markdownlint ✅

## 关键决策

- 09/10 file 改目录（和 07 一致）：仪表盘/模板规范无独立流程文档，由 scripts+templates 承载
- 旧→新映射：04-第二步_迭代开发 → 04-长程开发；06-第三步_收束节点/07-汇报 → 08-汇报收束；05-完整流程与核心原则 → README

## 下一步

- [ ] P1 工程优化（importlinter/spectral/CI/依赖锁/dashboard/钩子警告）
