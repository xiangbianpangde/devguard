# 项目状态

> 更新: 2026-07-17（审查加固：markdownlint POSIX 门禁修复、render_meta 防截断、ruff 版本真源、脚本镜像漂移防护；#53 final-report 报告格式纳入模板族硬契约）
<!-- devguard-progress: completed=53 total=53 -->
<!-- convergence-gate: nodes=31,35,46,49,52 last_converged_fp=52 -->

## 当前进度

| 阶段 | 功能点 | 状态 | 完成日期 |
|------|--------|------|---------|
| V0.x 起步 | #1-#33 (含 35/35 列表 + 8 规范) | ✅ | 2026-05-26 |
| V0.1 收束 | 9 钩子 + 5 阶段 CI | ✅ | 2026-05-27 |
| V0.2-V0.9 收束 | commitlint / markdownlint / L1 检测 / 章节级 L1 / 模板同步 | ✅ | 2026-06-07 |
| V1.0 收尾 | 12-codeowners + 收束索引 + CHANGELOG | ✅ | 2026-06-07 |
| V1.1 收尾 | 13-changelog + 14-security | ✅ | 2026-06-07 |
| V1.2 收尾 | 15-support + SUPPORT.md | ✅ | 2026-06-07 |
| V1.3 收尾 | 16-license + LICENSE + README 重写 | ✅ | 2026-06-07 |
| V1.4 收尾 | 17-contributing + CONTRIBUTING.md | ✅ | 2026-06-07 |
| V1.5 收尾 | final-report-template 沉淀 + 2 份 V1.x 汇报 HTML + STATUS 滞后修复 + worklog 断档补登 | ✅ | 2026-06-08 |
| P0/P1 强化 | #47 渲染/CI、#48 可测闸门、#49 一键初始化 | ✅ | 2026-07-11 |
| ECC 全项目对标 | #50 分支收敛、#51 能力矩阵与治理对齐、#52 一键初始化 2.0 | ✅ | 2026-07-11 |
| V2.4 增强 | #53 报告格式入族（final-report 契约 + 规范路由澄清） | ✅ | 2026-07-17 |
| **V2.0.1 启动** | **devguard dogfood (V1.x 范式在自身闭环 8 次拦截 / 全部修复)** | **✅** | **2026-06-08** |

## 累计数据

- **17 规范齐全**（01-08 原始 + 09-17 衍展）
- **19 个 pre-commit / commit-msg 钩子**（含 ECC 十域对标硬闸门）
- **5 阶段 CI**（lint / test / l4-conventions / compliance / build）
- **188 tests passed**（tests/conventions/）
- **17 个收束节点**（V0.1-V2.2 全部落盘；本轮机器收束通过）
- **2 套汇报模板**（markdown 轻量 + final-report-template HTML 高密度）
- **8 ADR 决策**（worklogs/decisions/）
- **~50+ commits**（5/26 → 6/8 完整链可追）

## 阻塞项

（无）

## 图例

| 符号 | 含义 |
|------|------|
| ✅ | 已完成 |
| 🔄 | 进行中 |
| ⏳ | 待开始 |
| 🚫 | 阻塞中（需注明等谁/等什么） |

## 收束节点历史

| 节点 | 日期 | 功能点范围 | 整理 | 测试 | AI审计 | 人审计 | 验证 | 遗留问题 |
|------|------|-----------|------|------|--------|--------|------|---------|
| v0.1 | 2026-05-27 | #29-#31 | ✅ | ✅ 13/13 | ✅ 0红线 | ✅ 已签核 | ✅ | 见 人审计签核-v0.1.md |
| v0.2 | 2026-06-07 | V2.1-V2.6 (5 件) | ✅ | ✅ | ✅ 0红线 | ⏳ 待签核 | ✅ | commitlint + 性能基线 |
| v0.3 | 2026-06-07 | V3.1-V3.4 (4 件) | ✅ | ✅ | ✅ 0红线 | ⏳ 待签核 | ✅ | markdownlint + dashboard 切换 |
| v0.4 | 2026-06-07 | V4.1-V4.4 (4 件) | ✅ | ✅ | ✅ 0红线 | ⏳ 待签核 | ✅ | L1 检测完整化 + dashboard 字段 |
| v0.5 | 2026-06-07 | V5.1-V5.5 (5 件) | ✅ | ✅ | ✅ 0红线 | ⏳ 待签核 | ✅ | grade.l1_check_path + 章节级 L1 + CSP |
| v0.6 | 2026-06-07 | V6.1-V6.3 (3 件) | ✅ | ✅ | ✅ 0红线 | ⏳ 待签核 | ✅ | 章节级 L1 入 CI + V6.3 自动收集回退 |
| v0.7 | 2026-06-07 | V7.1-V7.2 (2 件) | ✅ | ✅ | ✅ 0红线 | ⏳ 待签核 | ✅ | 10-templates-reporting + L4 retry 成功 |
| v0.8 | 2026-06-07 | V8.1-V8.2 (2 件) | ✅ | ✅ | ✅ 0红线 | ⏳ 待签核 | ✅ | l1_check_doc + README 重建 |
| v0.9 | 2026-06-07 | V9.1-V9.2 (2 件) | ✅ | ✅ | ✅ 0红线 | ⏳ 待签核 | ✅ | 07 §一 红线扩展 + 11-readme |
| v1.0 | 2026-06-07 | V1.1-V1.4 (4 件) | ✅ | ✅ 65/65 | ✅ 0红线 | ⏳ 待签核 | ✅ | 12-codeowners + INDEX + CHANGELOG |
| v1.1 | 2026-06-07 | V1.1.1-V1.1.2 (2 件) | ✅ | ✅ 65/65 | ✅ 0红线 | ⏳ 待签核 | ✅ | 13-changelog + 14-security |
| v1.2 | 2026-06-07 | V1.2.1 (1 件) | ✅ | ✅ 65/65 | ✅ 0红线 | ⏳ 待签核 | ✅ | 15-support |
| v1.3 | 2026-06-07 | V1.3.1-V1.3.3 (3 件) | ✅ | ✅ 65/65 | ✅ 0红线 | ⏳ 待签核 | ✅ | 16-license + README 重写 |
| v1.4 | 2026-06-07 | V1.4.1-V1.4.2 (2 件) | ✅ | ✅ 65/65 | ✅ 0红线 | ⏳ 待签核 | ✅ | 17-contributing |
| **v1.5** | **2026-06-08** | **V1.5.1 (1 件)** | **✅** | **✅ 65/65** | **✅ 0红线** | **⏳ 待签核** | **✅** | **final-report-template + 2 汇报** |
| **v2.1** | **2026-07-11** | **#47-#49 (3 件)** | **✅** | **✅ 132/132** | **✅ 0 个 P0/P1** | **⏳ 待签核** | **✅** | **一致性 100% + 拦截率 100% + 一键初始化 + 分支保护** |
| **v2.2** | **2026-07-11** | **#50-#52 (3 件)** | **✅** | **✅ 163/163** | **✅ ECC 10/10** | **⏳ 待签核** | **✅** | **全分支历史合入 + skills-first + 原子回滚 + 仓外 E2E** |

> **人审计签核说明**（2026-07-11 核对）：v0.1 已签核（见 `docs/reports/人审计签核-v0.1.md`）；v0.2–v2.2 共 16 个节点尚待 Owner 签核。历史目标日期 2026-06-30 已逾期，不计为已完成。详见 `docs/reports/2026-06-10_强制性约束审查与修复/`。

## 技术债

| # | 项目 | 收束节点 | 备注 |
|---|------|----------|------|
| 1 | `docs/重构笔记-使用开发规范重构项目指南.md` | 待用户决定 | V0 遗留 untracked |
| 2 | commitlint "config" 警告噪音 | V2.0+ | 钩子不阻断但污染输出 |
| 3 | 18-章外规范入 _meta.yaml | V2.0+ | 已无明显遗漏 |
| 4 | devguard 自身 dogfood | V2.0+ | 用 V1.x 约束开发规范项目本身 |
| 5 | CI 跨平台测试 | V2.0+ | PowerShell vs bash 兼容 |

---

## 详细功能点列表（V0.x-V1.5）

| # | 功能点 | BDD | 状态 | 完成日期 |
|---|--------|-----|------|---------|
| 1 | 架构设计规范 (01) | specs/01-architecture.md | ✅ 已完成 | - |
| 2 | 代码编写规范 (02) | specs/02-coding.md | ✅ 已完成 | - |
| 3 | Git 协作规范 (03) | specs/03-git.md | ✅ 已完成 | - |
| 4 | API 设计规范 (04) | specs/04-api.md | ✅ 已完成 | - |
| 5 | 测试规范 (05) | specs/05-testing.md | ✅ 已完成 | - |
| 6 | 文档规范 (06) | specs/06-documentation.md | ✅ 已完成 | - |
| 7 | AI 协作开发流程 (07) | specs/07-ai-workflow.md | ✅ 已完成 | - |
| 8 | 项目基础设施搭建 | specs/00-infrastructure-template.md | ✅ 已完成 | 2026-05-26 |
| 9 | 统一模板 + BDD 规格 | specs/00-infrastructure-template.md | ✅ 已完成 | 2026-05-26 |
| 10 | 01-架构 模板改造 | specs/01-architecture.md | ✅ 已完成 | 2026-05-26 |
| 11 | 02-代码 模板改造 | specs/02-coding.md | ✅ 已完成 | 2026-05-26 |
| 12 | 03-Git 模板改造 | specs/03-git.md | ✅ 已完成 | 2026-05-26 |
| 13 | 04-API 模板改造 | specs/04-api.md | ✅ 已完成 | 2026-05-26 |
| 14 | 05-测试 模板改造 | specs/05-testing.md | ✅ 已完成 | 2026-05-26 |
| 15 | 06-文档 模板改造 | specs/06-documentation.md | ✅ 已完成 | 2026-05-26 |
| 16 | 示例代码库 | specs/08-examples.md | ✅ 已完成 | 2026-05-26 |
| 17 | 仪表盘自动生成 | specs/09-dashboard-gen.md | ✅ 已完成 | 2026-05-26 |
| 18 | 基础设施修正（审查修复） | - | ✅ 已完成 | 2026-05-26 |
| 19 | 二轮审查修复（全量复查） | - | ✅ 已完成 | 2026-05-26 |
| 20 | 文件图谱 + 仪表盘优化 | specs/09-dashboard-gen.md | ✅ 已完成 | 2026-05-26 |
| 21 | 统一模板规约 + 汇报模板 | specs/10-templates-reporting.md | ✅ 已完成 | 2026-05-26 |
| 22 | 5处现有规范增强（图谱v2第一步） | specs/01-06-07 | ✅ 已完成 | 2026-05-27 |
| 23 | 第08号规范初稿（图谱v2第二步） | specs/08-code-understanding.md | ✅ 已完成 | 2026-05-27 |
| 24 | BDD规格：现有规范增强 + 08规范 | specs/01-08 | ✅ 已完成 | 2026-05-27 |
| 25 | 示例代码：src/code-understanding/ | - | ✅ 已完成 | 2026-05-27 |
| 26 | 交叉引用更新：FILE_GRAPH + README + CLAUDE | - | ✅ 已完成 | 2026-05-27 |
| 27 | 文件夹重整：提取模板+补齐AI模板+消除重叠 | specs/10-templates-reporting.md | ✅ 已完成 | 2026-05-27 |
| 28 | 合并 plan/ + design/ → docs/plan/ | - | ✅ 已完成 | 2026-05-27 |
| 29 | decisions 移入 worklog + 约束节点决策总结规则 | - | ✅ 已完成 | 2026-05-27 |
| 30 | CLAUDE.md ↔ README 角色分离（13 个 README 更新） | - | ✅ 已完成 | 2026-05-27 |
| 31 | 汇报体系纳入 ai-workflow（新建 08-汇报收束.md + 流程集成） | specs/10-templates-reporting.md | ✅ 已完成 | 2026-05-27 |
| 32 | 汇报与收束定义修正（CLAUDE/06/07 三文件对齐） | - | ✅ 已完成 | 2026-05-27 |
| 33 | ai-workflow 流程修订（角色/收束闸门/可观测/档位）+ README 命名规范化 + 收束术语统一 | specs/07-ai-workflow.md | ✅ 已完成 | 2026-05-27 |
| 34 | 规范正文 v2.0 重构（01-06/08 细化挂接+红线自动检测+去重+图谱收拢）+ 7 份 BDD realign + src 落地配置(5) + CLAUDE 三件套(根/模板/导航) + 汇报定义澄清 | specs/01-08 | ✅ 已完成 | 2026-05-27 |
| 35 | 第08号规范 v3.0 重构（双图谱范式：CodeGraph + Understand-Anything） | specs/08-code-understanding.md | ✅ 已完成 | 2026-05-28 |
| 36 | 09-dashboard-gen 规范入真源 + dashboard 自动渲染 | specs/09-dashboard-gen.md | ✅ 已完成 | 2026-06-07 |
| 37 | 10-templates-reporting 规范入真源 + 模板规约 | specs/10-templates-reporting.md | ✅ 已完成 | 2026-06-07 |
| 38 | 11-readme 规范入真源 + README 双件套分离 | specs/07-ai-workflow.md | ✅ 已完成 | 2026-06-07 |
| 39 | 12-codeowners 规范入真源 + CODEOWNERS | specs/03-git.md | ✅ 已完成 | 2026-06-07 |
| 40 | 13-changelog 规范入真源 + CHANGELOG | specs/06-documentation.md | ✅ 已完成 | 2026-06-07 |
| 41 | 14-security 规范入真源 + SECURITY + gitleaks | specs/02-coding.md | ✅ 已完成 | 2026-06-07 |
| 42 | 15-support 规范入真源 + SUPPORT | specs/06-documentation.md | ✅ 已完成 | 2026-06-07 |
| 43 | 16-license 规范入真源 + MIT LICENSE | specs/06-documentation.md | ✅ 已完成 | 2026-06-07 |
| 44 | 17-contributing 规范入真源 + CONTRIBUTING | specs/03-git.md | ✅ 已完成 | 2026-06-07 |
| 45 | final-report-template 高密度 HTML 模板 | specs/10-templates-reporting.md | ✅ 已完成 | 2026-06-08 |
| 46 | V1.x 收尾汇报 HTML 两份 | specs/10-templates-reporting.md | ✅ 已完成 | 2026-06-08 |
| 47 | P0：渲染器、CI 与原生文件语义修复 | specs/03-git.md | ✅ 已完成 | 2026-07-11 |
| 48 | P0：可测一致性与强制性故障注入闸门 | specs/07-ai-workflow.md | ✅ 已完成 | 2026-07-11 |
| 49 | P1：自包含一键初始化与跨平台仪表盘 | specs/00-infrastructure-template.md | ✅ 已完成 | 2026-07-11 |
| 50 | 分支历史与独有能力收敛 | specs/03-git.md | ✅ 已完成 | 2026-07-11 |
| 51 | ECC 全项目能力矩阵与治理对齐 | specs/07-ai-workflow.md | ✅ 已完成 | 2026-07-11 |
| 52 | ECC 对标的一键初始化 2.0 与最终收束 | specs/00-infrastructure-template.md | ✅ 已完成 | 2026-07-11 |
| 53 | 报告格式入族（final-report 契约 + 规范路由澄清） | specs/10-templates-reporting.md | ✅ 已完成 | 2026-07-17 |
