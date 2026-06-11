# M3 示例代码（src/）

> devguard 模块设计文档 · v1.0 · 2026-06-10
> 配套文档：[简报.md](简报.md) · [设计.md](设计.md) · [实现计划.md](实现计划.md) · [阅读笔记.md](阅读笔记.md) · [deliverable.md](deliverable.md)
> 更新: 2026-06-11

---

## 三句话读懂

`src/` 是 devguard 的**规范落地态** —— 7 个子目录各对应 1 篇规范的"§二 落地配置"的可运行版本：

1. **7 个子目录** —— 按规范维度分（architecture / coding / git / api / testing / documentation / code-understanding），与 `conventions/01-08` 一一对应
2. **9 个落地配置文件** —— 复制即用的 ruff / pre-commit / pytest / spectral / importlinter 配置，对应规范 §二「落地」段
3. **可运行可阅读** —— 每个子目录有 `README-<维度>示例.md` + 可直接 `python xxx.py` / `pytest` / `uvicorn` 跑通

---

## 文档索引

| 文档 | 读什么 | 适合谁 |
|------|--------|--------|
| **简报.md** | ≤80 行速读 + 7 子目录速览表 + 拓扑 mermaid | 所有人先看 |
| **设计.md** | 模块定位 → 7 子目录详介 → 落地策略 → 互检关系 → 边界 | 所有人细读 |
| **实现计划.md** | V0.x 起步 6 子目录 → V0.x 加 code-understanding → 重构对齐 → 当前状态 | 想理解演进时读 |
| **阅读笔记.md** | 章节导航 + 概念索引 + BDD 清单 + 思考题 + 易踩坑速查 | 深度阅读时打开 |
| **deliverable.md** | 7 件交付物 + 模块本体状态 + 维护清单 | 评审/交付时检查 |
| **设计.html** | 设计.md 的 HTML 渲染版 | 浏览器预览 |
| **实现计划.html** | 实现计划.md 的 HTML 渲染版 | 浏览器预览 |

---

## 快速预览

```
开发者视角                          系统做了什么
────────                          ──────────
"规范怎么落地？"                    src/<维度>/ 演示每篇规范 §二「落地」的可运行版本
"importlinter 怎么写？"             src/architecture/importlinter.ini 复制即用
"ruff 选哪些规则？"                 src/coding/ruff.toml 选 E/F/N/T20/S/PLR0915
"commit message 怎么校验？"         src/git/.pre-commit-config.yaml + commitlint.config.js
"测试覆盖率门禁怎么配？"             src/testing/pytest.ini: --cov-fail-under=80
"API 契约怎么 lint？"               src/api/.spectral.yaml: 路径 kebab-case + 禁动词
"双图谱底层原理是什么？"            src/code-understanding/call_graph_example.py AST 教学
```

---

## 与其他模块的关系

- **被规范驱动**：`conventions/01-08`（M1）的 §二「落地」段每条配置在 `src/<维度>/` 都有对应可运行文件
- **被 `_meta.yaml` 引用**：`conventions/_meta.yaml` 的 `l1_check_path` 字段指向 `src/coding/ruff.toml` / `src/architecture/importlinter.ini` 等
- **被 BDD 验收**：`docs/specs/08-examples.md`（M2）互检本模块
- **被 worklog 引用**：`worklogs/2026-05-27_图谱与代码理解规范v2实施.md` / `2026-05-28_08规范v3.0双图谱重构.md` 等多次提及
- **被模板同步**：`docs/templates/devguard/src/code-understanding/`（V0.x 重构时同步）
