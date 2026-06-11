# M7 根目录顶层入口 · 交付物清单

> 版本: v1.0 · 2026-06-10
> 状态: 设计文档已交付（模块本身已 49/49 完成）
> 更新: 2026-06-11

---

## 8 件交付物

| # | 文件 | 状态 | 说明 |
|---|------|:---:|------|
| 1 | 简报.md | ✅ | ≤ 80 行 + 9 文件角色矩阵 + 关系拓扑 mermaid |
| 2 | 设计.md | ✅ | 9 文件总览 + 逐个介绍 + 双入口决策 + 边界 + 验收 |
| 3 | 实现计划.md | ✅ | V0.x 起步 4 件 → V1.4 完整 9 件 + dogfood 验证 |
| 4 | 阅读笔记.md | ✅ | 章节导航 + 概念索引 + BDD 清单 + 思考题 + 易踩坑速查 |
| 5 | README.md | ✅ | 文件夹索引 |
| 6 | deliverable.md | ✅ | 8 件交付物清单 + 维护清单 |
| 7 | 设计.html | ⬜ 待生成 | 设计.md 的 HTML 渲染版（占位） |
| 8 | 实现计划.html | ⬜ 待生成 | 实现计划.md 的 HTML 渲染版（占位） |

---

## 模块本体的交付状态

| 子项 | 状态 | 数量 |
|------|:---:|:---:|
| 9 顶层文件 | ✅ | 9/9 |
| GitHub 标准件 5 | ✅ | README + CHANGELOG + SECURITY + SUPPORT + LICENSE + CONTRIBUTING |
| 项目特色件 4 | ✅ | CLAUDE + STATUS + dashboard + CONTRIBUTING（**注**：CONTRIBUTING 既是 GitHub 标准也是项目特色） |
| 治理类规范（11-17） | ✅ | 6/6 入 `_meta.yaml` |
| 双入口分离 | ✅ | worklog 2026-05-27 已落规 |
| dashboard 渲染 | ✅ | HTTP 启动可用，CSP 头 + render mtime 标识 |
| L4 测试 | ✅ | 65/65 passed（间接覆盖 README 链接、STATUS 表格 schema） |

---

## 维护清单（持续）

- [ ] 改 `CLAUDE.md` → 同步 `docs/templates/devguard/CLAUDE模板.md`（模板版本）
- [ ] 改 `README.md` → 同步 `docs/templates/devguard/README模板.md`（模板版本）
- [ ] 改 `STATUS.md` 表头 → 同步 `scripts/render.py` 解析器
- [ ] 改治理文件（SECURITY/SUPPORT/CONTRIBUTING/LICENSE）→ 极低频，1 次写好后几乎不动
- [ ] dashboard 渲染 → 改 STATUS.md 触发 `render.py` 重生成
- [ ] 9 文件名保持拼写稳定（`LICENSE` 无后缀、`CODEOWNERS` 大写）

---

## Owner 决策点（针对未来扩展）

- [ ] 是否补 `CODE_OF_CONDUCT.md`（社区准则）作为第 10 文件？—— 当前在 CONTRIBUTING.md 中通过 Contributor Covenant 引用
- [ ] 是否把 `CODEOWNERS` 从 `.github/` 移到根目录？—— GitHub 都支持，移与不移是风格选择
- [ ] dashboard 是否改为 SPA（点卡片跳转）？—— 当前纯静态够用，引入框架增加维护成本
- [ ] STATUS.md 是否改名为 PROGRESS.md？—— 不建议，名称稳定利于 dashboard 解析
- [ ] 是否引入 `RELEASES.md` / `MIGRATION.md`？—— 当前归入 CHANGELOG.md（CHANGELOG 不只列变更也列迁移指南）
- [ ] 双入口分离是否仍维持？—— 是；worklog 2026-05-27 决策无反例

---

## 与其他模块的引用关系

| 引用 | 方向 | 文件 |
|------|------|------|
| 规范速查表 | M1 → M7 | `conventions/_meta.yaml` 的 17 条目 → `CLAUDE.md` 速查表（人工同步） |
| STATUS 解析 | M7 → M4 | `STATUS.md` → `dashboard.html`（render.py 渲染） |
| 模板复制 | M7 → M2 | `docs/templates/devguard/CLAUDE模板.md` ← `CLAUDE.md`（手工维护） |
| 11-17 规范元数据 | M1 → M7 | `conventions/_meta.yaml` → 9 文件中的 6 个治理文件存在性 |
| 收束报告 | M7 → M2 | `docs/reports/INDEX.md` → 各收束节点报告 |
| worklog 引用 | M7 → M5 | 本模块文档引用 `worklogs/2026-05-27_CLAUDE与README角色分离.md` |
