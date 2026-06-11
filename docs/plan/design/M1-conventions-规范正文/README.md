# M1 规范正文（conventions/）

> devguard 模块设计文档 · v1.0 · 2026-06-10
> 配套文档：[简报.md](简报.md) · [设计.md](设计.md) · [实现计划.md](实现计划.md) · [阅读笔记.md](阅读笔记.md) · [deliverable.md](deliverable.md)
> 更新: 2026-06-11

---

## 三句话读懂

`conventions/` 是 devguard 的**规则源** —— 整套规范的真源（single source of truth）：

1. **17 篇规范** —— 01-08 有正文（每篇约 165 行），09-17 仅以元数据形态登记在 `_meta.yaml` 中
2. **10 篇 AI 协作流程** —— `ai-workflow_AI协作开发流程/` v2.0 引入双轨制（研究 vs 工程）+ 部署规范
3. **一个真源** —— `_meta.yaml` 通过 `scripts/render_meta.py` 渲染出钩子配置 / 仪表盘 / CI 范围

---

## 文档索引

| 文档 | 读什么 | 适合谁 |
|------|--------|--------|
| **简报.md** | ≤80 行速读 + 规范关系拓扑 mermaid | 所有人先看 |
| **设计.md** | 设计意图 → 真源策略 → 红线机制 → 路由表 → 边界 | 所有人细读 |
| **实现计划.md** | V0.1 → V2.0.1 演进路径 + 17 规范增量 | 想理解"为什么是 17 篇"时读 |
| **阅读笔记.md** | 章节导航 + 概念索引 + 思考题 | 深度阅读时打开 |
| **deliverable.md** | 7 件交付物清单 + 维护清单 | 评审/交付时检查 |
| **设计.html** | 设计.md 的 HTML 渲染版 | 浏览器预览 |
| **实现计划.html** | 实现计划.md 的 HTML 渲染版 | 浏览器预览 |

---

## 快速预览

```
开发者视角                          系统做了什么
────────                          ──────────
"写代码前看哪份规范？"              CLAUDE-规范导航.md 路由：任务类型→对应规范
"红线有哪些？"                     README-规范导航.md 红线速查 + 各篇 §一
"改了 _meta.yaml"                  render_meta.py 自动同步：分级标签+pre-commit+dashboard
"新写一篇规范"                     _meta.yaml 加一条 + 写正文 + 加 BDD + 加 L1 检测脚本
```

---

## 与其他模块的关系

- **被验收**：`docs/specs/`（M2 子模块）逐篇 BDD 互检
- **驱动**：`scripts/render_meta.py`（M4）→ `.pre-commit-config.yaml` + `dashboard.html`（M7）
- **示例**：`src/<规范维度>/`（M3）为每篇规范的可运行配置
- **导航**：根目录 `CLAUDE.md`（M7）速查表来自本模块的 `CLAUDE-规范导航.md`
