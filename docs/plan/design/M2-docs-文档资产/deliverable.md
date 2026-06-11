# M2 文档资产 · 交付物清单

> 版本: v1.0 · 2026-06-10
> 状态: 设计文档已交付（模块本身已 49/49 完成）

---

## 7 件交付物

| # | 文件 | 状态 | 说明 |
|---|------|:---:|------|
| 1 | 简报.md | ✅ | ≤ 80 行 + 子模块关系拓扑 mermaid |
| 2 | 设计.md | ✅ | 模块定位·五子模块·模板真源·BDD 互检·计划链路·汇报体系·边界 |
| 3 | 实现计划.md | ✅ | V0.x 起步 → V2.0.1 五阶段历史演进路径 |
| 4 | 阅读笔记.md | ✅ | 章节导航·概念索引·BDD 清单·思考题·易踩坑速查 |
| 5 | README.md | ✅ | 文件夹索引 |
| 6 | 设计.html | ⬜ 待生成 | 设计.md 的 HTML 渲染版 |
| 7 | 实现计划.html | ⬜ 待生成 | 实现计划.md 的 HTML 渲染版 |

---

## 模块本体的交付状态

| 子模块 | 状态 | 数量 |
|--------|:---:|:---:|
| 模板库 `docs/templates/` | ✅ | 14 通用模板 + 5 件 final-report-template（template/render/data/README/demo） |
| devguard 专属 `docs/templates/devguard/` | ✅ | 含 conventions/ + scripts/ + src/ + html-report-template/ + final-report-template/ |
| BDD 规格 `docs/specs/` | ✅ | 12 份（00-10） |
| 项目计划 `docs/plan/` | ✅ | 背景.md + 开发清单.md + design/（含 M1/M2 设计目录） |
| 进度汇报 `docs/reports/` | ✅ | INDEX + README-汇报说明 + 14 收束报告 + 1 人审计签核 + 2 阶段汇报 + 3 HTML 报告 + 1 审查报告目录 |
| 调研 `docs/research/` | ✅ | 1 简短调研 + 1 深度研究目录（report.md + tree/N1-N6 共 13 文件） |

### 关键数字

| 指标 | 数值 |
|------|------|
| 通用模板数 | 14（BDD/CLAUDE/README/STATUS/plan/worklog/汇报/审计/收束/ADR/AI 提示词/AI 会话启动/规范文档） |
| devguard 专属模板 | final-report-template 5 件（template + render.py + example-data.json + README + demo.html） |
| BDD 文件数 | 12（00-10，含 08-examples + 08-code-understanding 两个分支） |
| 收束报告数 | 14（v0.1-v1.5） |
| 人审计签核 | 1 件（v0.1 已签核）+ 13 件待签核 |
| HTML 报告 | 3 件（V1.5/V1.x 收尾 × 2 + V2.0 合并） |
| 调研子模块 | 2 主题（开发规范 + 图谱与代码理解工具） |
| 调研 N 级文件 | 13（tree/N1-N6，含命名变体） |

---

## 维护清单（持续）

- [ ] 改规范 → 同步对应 `docs/specs/` BDD（PR-09）
- [ ] 改规范 → 同步 `docs/templates/devguard/conventions/`（10 规范）
- [ ] 新增模板 → 登记 `docs/templates/README-模板索引.md`
- [ ] 新增功能点 → `docs/plan/开发清单.md` + `STATUS.md` 同步加行
- [ ] 收束节点 → 必产 `docs/reports/收束报告-vX.Y.md`
- [ ] final-report-template render → 跑通 `python render.py --data example-data.json --out demo.html`，残留占位符 = 0
- [ ] 新增调研 → 落 `docs/research/<主题>/report.md` + `tree/N*.md`（按需）
- [ ] `render_meta.py --check` 必须在 pre-commit 中跑

---

## Owner 决策点（针对未来扩展）

- [ ] research 子模块的命名变体（N1-...构建方法.md / N1-...的构建方法.md）是否合并去重？
- [ ] final-report-template 是否升 v1.1（增加 5 类新占位符 + Mermaid 块可达 15）？
- [ ] 收束报告是否自动从 `_meta.yaml` 生成（避免手工 v0.1-v1.5 编号）？
- [ ] 模板规约（10 规范）是否升级为"内容质量"校验（当前只校验"登记 + 路径"）？
- [ ] 调研子模块是否要求所有决策显式 `<!-- ref: docs/research/... -->` 引用？
