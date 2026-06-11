# M7 根目录顶层入口（root top-level entry）

> devguard 模块设计文档 · v1.0 · 2026-06-10
> 配套文档：[简报.md](简报.md) · [设计.md](设计.md) · [实现计划.md](实现计划.md) · [阅读笔记.md](阅读笔记.md) · [deliverable.md](deliverable.md)

---

## 三句话读懂

`根目录顶层入口`是 devguard 与外部世界对话的**9 张脸**——9 个固定入口文件、缺一不可、互不重位：

1. **5 + 4 配置** —— GitHub 标准件 5（README/CHANGELOG/SECURITY/SUPPORT/LICENSE）+ 项目特色 4（CLAUDE/STATUS/dashboard/CONTRIBUTING）
2. **人 vs AI 双入口** —— 顶层首条铁律"人读 README、AI 读 CLAUDE.md"是整套范式的精神起点（worklog 2026-05-27）
3. **真源单向流** —— STATUS.md → dashboard.html 一条解析链；其他文件之间不互相"准源"

---

## 文档索引

| 文档 | 读什么 | 适合谁 |
|------|--------|--------|
| **简报.md** | ≤80 行速读 + 9 文件角色矩阵 + 关系拓扑 mermaid | 所有人先看 |
| **设计.md** | 9 文件逐个介绍 + 真源关系 + 边界 + 验收 | 所有人细读 |
| **实现计划.md** | V0.x 起步即建立四件套 → V1.x 逐步补齐 5+4 全套 | 想理解"什么时候加哪个"时读 |
| **阅读笔记.md** | 章节导航 + 概念索引 + 思考题 | 深度阅读时打开 |
| **deliverable.md** | 8 件交付物清单 + 维护清单 | 评审/交付时检查 |
| **设计.html** | 设计.md 的 HTML 渲染版（占位） | 浏览器预览 |
| **实现计划.html** | 实现计划.md 的 HTML 渲染版（占位） | 浏览器预览 |

---

## 快速预览

```
访客视角                          系统做了什么
────────                          ──────────
"人类第一次来仓库"               读 README.md → 知道项目是啥 + 怎么用
"想看进度"                       读 STATUS.md 或打开 dashboard.html（HTTP 启动）
"想报告安全漏洞"                 读 SECURITY.md → 私信 owner
"AI Agent 新会话自动加载"        读 CLAUDE.md → 获得完整项目上下文
"想贡献代码"                     读 CONTRIBUTING.md → 走 PR 流程
"想知道许可"                     读 LICENSE
"找支持渠道"                     读 SUPPORT.md
"看版本变更"                     读 CHANGELOG.md
```

---

## 与其他模块的关系

- **导航到 conventions/**（M1）—— `CLAUDE.md` 的"规范速查"直接引自 M1 的 `CLAUDE-规范导航.md`
- **解析 STATUS.md**（M5）—— `dashboard.html` 由 `scripts/render_meta.py` + `render.py` 渲染
- **真源在 M1** —— 本模块的 9 文件**自身**不产生真源（dashboard 是渲染产物，STATUS 是数据源），但承载了"项目门面"
- **FILE_GRAPH.md**（M6）"项目级入口"节明确禁止根目录堆散文件 —— 9 文件之外不能再加
