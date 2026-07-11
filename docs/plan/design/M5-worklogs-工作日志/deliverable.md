# M5 工作日志 · 交付物清单

> 版本: v1.0 · 2026-06-10
> 状态: 设计文档已交付（模块本身已 31+6 完成）
> 更新: 2026-07-11

---

## 7 件交付物

| # | 文件 | 状态 | 说明 |
|---|------|:---:|------|
| 1 | 简报.md | ✅ | ≤ 80 行 + 类型速览 + 命名规约 + 6 ADR + 生命周期 mermaid |
| 2 | 设计.md | ✅ | 模块定位·命名规约·五段式·ADR 设计·commit-msg 强引·与汇报关系·边界 |
| 3 | 实现计划.md | ✅ | V0.x 起步 → V1.5 五阶段历史演进路径 + 断档补登教训 |
| 4 | 阅读笔记.md | ✅ | 章节导航·概念索引·BDD 清单·思考题·易踩坑速查 |
| 5 | README.md | ✅ | 文件夹索引 |
| 6 | 设计.html | ⬜ 待生成 | 设计.md 的 HTML 渲染版 |
| 7 | 实现计划.html | ⬜ 待生成 | 实现计划.md 的 HTML 渲染版 |

---

## 模块本体的交付状态

| 子模块 | 状态 | 数量 |
|--------|:---:|:---:|
| worklog 文件 | ✅ | 31 份（2026-05-26 ~ 2026-06-10） |
| 收束节点 worklog | ✅ | 6 份（V1.5 集中产出 + 1 份断档补登） |
| ADR 文件 | ✅ | 6 份（0001-0006） |
| worklog 模板 | ✅ | 1 份（`docs/templates/worklog模板.md`） |
| commit-msg 强引工具 | ✅ | 1 份（`scripts/check_worklog_ref.py`） |
| 仪表盘统计 | ✅ | 31 份接入 `collect_l4_stats.py` |

---

## 维护清单（持续）

- [ ] 新功能点 → 创建 `worklogs/YYYY-MM-DD_<描述>.md` + git commit 引用
- [ ] 收束节点 → 回顾 worklog「关键决策」段 → 升格为 ADR（`worklogs/decisions/NNNN-*.md`）
- [ ] 命名规约 → 全量匹配 `YYYY-MM-DD_<描述>.md` 正则
- [ ] 模板合规 → 必填段（做了什么 / 验证结果）齐全
- [ ] ADR 路径 → 6 份全部在 `worklogs/decisions/`，不在 `docs/decisions/`
- [ ] ADR 编号 → 0001-0006 连续无跳号
- [ ] 收束报告 → 落盘 `docs/reports/`，不在 worklog 内
- [ ] `[skip-worklog]` 豁免 → 季度审计，避免滥用
- [ ] `check_worklog_ref.py` → 在 pre-commit 中跑
- [ ] 断档补登 → V1.5 已执行，未来不允许再积压

---

## Owner 决策点（针对未来扩展）

- [ ] worklog 数量超 100 份时是否按月归档（如 `worklogs/archive/2026-05/`）？
- [ ] ADR 编号超 9999 时是否改用日期前缀（YYYYMMDD-NNN）？
- [ ] `decisions/` 是否按主题再分（`decisions/architecture/`、`decisions/process/`）？
- [ ] 是否增加 worklog 模板合规自动检测（当前仅人工审阅）？
- [ ] 是否增加"必填段缺失"拦截（强化红线 6）？
- [ ] `[skip-worklog]` 豁免是否要求人审批后才生效？
- [ ] 同日多份 worklog 是否允许简化为"日合并 worklog"（如 `_daily-summary.md`）？
- [ ] worklog 跨条目反向链接：是否自动从 git log 反向生成 commit → worklog 索引？
