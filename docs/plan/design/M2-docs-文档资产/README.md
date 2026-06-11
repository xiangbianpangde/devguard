# M2 文档资产（docs/）

> devguard 模块设计文档 · v1.0 · 2026-06-10
> 配套文档：[简报.md](简报.md) · [设计.md](设计.md) · [实现计划.md](实现计划.md) · [阅读笔记.md](阅读笔记.md) · [deliverable.md](deliverable.md)
> 更新: 2026-06-11

---

## 三句话读懂

`docs/` 是 devguard 的**文档资产仓库** —— 除规范正文以外的所有文档都在此：

1. **模板权威源** —— `docs/templates/` 是新项目复制的源头（14+ 模板 + `devguard/` fork 整组复制）
2. **BDD 验收源** —— `docs/specs/` 与 `conventions/` 一一互检，确保规范有验收
3. **项目内务文档** —— `plan/`（背景+清单+设计）/ `reports/`（汇报+收束）/ `research/`（调研）

---

## 文档索引

| 文档 | 读什么 | 适合谁 |
|------|--------|--------|
| **简报.md** | ≤80 行速读 + 文档子模块拓扑 mermaid | 所有人先看 |
| **设计.md** | 五子模块定位 → 模板真源策略 → BDD 互检 → 计划/汇报关系 | 所有人细读 |
| **实现计划.md** | 五子模块的建立历程 + 模板沉淀路径 | 想理解"为什么 templates/ 有 devguard 子目录"时读 |
| **阅读笔记.md** | 章节导航 + 概念索引 + 思考题 | 深度阅读时打开 |
| **deliverable.md** | 7 件交付物清单 | 评审/交付时检查 |
| **设计.html** | 设计.md 的 HTML 渲染版 | 浏览器预览 |
| **实现计划.html** | 实现计划.md 的 HTML 渲染版 | 浏览器预览 |

---

## 快速预览

```
开发者视角                          系统做了什么
────────                          ──────────
"新项目要复制什么"                  cp -r docs/templates/devguard/ 到新仓库
"我的功能怎么验收"                  写 docs/specs/NN-<name>.md BDD
"复杂功能要写设计"                  docs/plan/design/<功能名>/ 五段式
"收束节点的产物去哪"                docs/reports/收束报告-vX.Y.md
"调研笔记放哪"                     docs/research/<主题>/
```

---

## 与其他模块的关系

- **验收**：`specs/` 与 `conventions/`（M1）双向互检
- **复制源**：`templates/devguard/` → 新项目根目录
- **驱动**：`plan/开发清单.md` → `STATUS.md`（M7）→ `dashboard.html`
- **沉淀**：`reports/` 接收收束节点产出 + `templates/devguard/final-report-template/` 为高密度学术风模板
