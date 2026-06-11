# M5 工作日志（worklogs/）

> devguard 模块设计文档 · v1.0 · 2026-06-10
> 配套文档：[简报.md](简报.md) · [设计.md](设计.md) · [实现计划.md](实现计划.md) · [阅读笔记.md](阅读笔记.md) · [deliverable.md](deliverable.md)

---

## 三句话读懂

`worklogs/` 是 devguard 的**过程证据库** —— 把"每个功能点做了什么、踩了什么坑、做了什么取舍"沉淀成可追溯的日流，并由此升格出跨批次的架构决策记录（ADR）：

1. **31 份 worklog** —— `YYYY-MM-DD_<描述>.md` 命名，覆盖 2026-05-26 ~ 2026-06-10 全周期
2. **6 份 ADR** —— `decisions/0001-0006`，仅在收束节点（人触发）从 worklog 升格而来
3. **强制引用闭环** —— `scripts/check_worklog_ref.py` 拦 commit-msg，每个 commit 必须带 worklog 引用（红线 6）

---

## 文档索引

| 文档 | 读什么 | 适合谁 |
|------|--------|--------|
| **简报.md** | ≤80 行速读 + 类型速览 + 生命周期 mermaid | 所有人先看 |
| **设计.md** | 模块定位 / 命名规约 / 五段式 / ADR 设计 / 强制引用 / 与汇报关系 / 边界 | 所有人细读 |
| **实现计划.md** | V0.x 起步 → V1.5 五阶段演进路径 | 想理解"为什么是 31+6"时读 |
| **阅读笔记.md** | 章节导航 + 概念索引 + BDD 清单 + 思考题 | 深度阅读时打开 |
| **deliverable.md** | 7 件交付物清单 + 维护清单 | 评审/交付时检查 |
| **设计.html** | 设计.md 的 HTML 渲染版 | 浏览器预览 |
| **实现计划.html** | 实现计划.md 的 HTML 渲染版 | 浏览器预览 |

---

## 快速预览

```
开发者视角                          系统做了什么
────────                          ──────────
"完成一个功能点"                    worklogs/YYYY-MM-DD_<描述>.md
"做了一个跨批次的决策"               worklog 「关键决策」段（不立 ADR）
"到收束节点了"                      人触发 → 回溯 worklog → 升格 ADR
"git commit"                       check_worklog_ref.py 拦：未引 worklog 不放过
"汇报在哪？"                        功能点级 → 对话内联；收束报告 → docs/reports/
```

---

## 与其他模块的关系

- **被强制引用**：`conventions/03-git` §一（红线 6）+ `scripts/check_worklog_ref.py` 兜底
- **被采集**：`scripts/collect_l4_stats.py` 统计 worklog 数量 → 仪表盘数据
- **被升格**：`worklogs/decisions/`（本模块子集）作为 ADR 唯一落点（ADR 0006）
- **与汇报**：`docs/reports/` 仅收束报告落盘；功能点汇报走对话内联（CLAUDE.md 工作流程）
- **与 STATUS**：`STATUS.md` 每个功能点一行 + worklog 路径互引
