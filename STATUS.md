# 项目状态

> 更新: 2026-06-11（V2.3：#51 豁免登记 + #53/#54 更新时间标签 + #52 收束硬闸门 ✅ 交付；#48-#50 待开始；闸门已对 V2.3 生效）

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
| **V2.0.1 启动** | **devguard dogfood (V1.x 范式在自身闭环 8 次拦截 / 全部修复)** | **✅** | **2026-06-08** |
| **V2.1 流程强制化** | **#36-#38 Phase1 汇报强制（commit-msg 三层拦截）** | **✅** | **2026-06-11** |
| | **#39 Phase1 markdownlint 审计 + 分批启用** | **✅** | **2026-06-11** |
| | **#40-#42 Phase2 入口文件 L1（STATUS/CLAUDE/开发清单 + L4 tests）** | **✅** | **2026-06-11** |
| | **#43-#44 Phase3 渲染鲁棒性 + 模板漂移扩展** | **✅** | **2026-06-11** |
| | **#45-#46 Phase4 文件放置 + 收束产物检查** | **✅** | **2026-06-11** |
| **V2.2 启动** | **#47 ai-workflow 旧文件引用语义重映射 + 模板同步**（详见 worklogs/2026-06-11_v2.2-fp47-planning.md） | **⏳ 待开始** | **-** |
| **V2.3 阶段A** | **#51 豁免登记强制化**（meta/豁免清单 + check_exemption_log commit-msg 钩子 + 7 L4，#52/#53 硬拦截前置） | **✅** | **2026-06-11** |
| **V2.3 阶段B** | **#53 更新时间标签强制化**（check_updated_tag commit-msg 硬拦 + PostToolUse 阻断；三层组合样板） | **✅** | **2026-06-11** |
| **V2.3 阶段B+** | **#54 更新标签全仓泛化**（钩子范围 6→全仓 159 在范围 .md + 回填 153 文件（git 末次修改日）+ 排除 templates/worklogs/.github/CHANGELOG + backfill 脚本） | **✅** | **2026-06-11** |
| **V2.3 阶段C** | **#52 收束硬闸门**（check_convergence_gate commit-msg 钩子 + STATUS 机器标记 + 5 L4；软闸门→铁闸门） | **✅** | **2026-06-11** |
| **V2.3 在途** | **#48-#50 约束与模板强化**（HTML 模板族+格式强制 / 基准脚手架 / 交流 agent；阶段C 的 check_doc_sync 拆后续） | **⏳ 待开始** | **-** |

## 累计数据

- **17 规范齐全**（01-08 原始 + 09-17 衍展）
- **16 pre-commit 钩子**（commit-msg 8 个 + pre-commit 8 个，双层；V2.3 #51 exemption-log + #53 updated-tag + #52 convergence-gate）+ **1 个 Claude PostToolUse 钩子**（#53 编辑当下阻断）
- **5 阶段 CI**（lint / test / l4-conventions / compliance / build）
- **103 L4 tests passed**（tests/conventions/，V2.3 #51 test_exemption_log 7 + #53/#54 test_updated_tag 5 + #52 test_convergence_gate 5；旧记的 7 个 ai-workflow 既存失败现已不复现）
- **159 个在范围文档 .md 全部带「更新」标签**（#54 回填 153 + 既有 6；排除 templates/worklogs/.github/CHANGELOG）
- **15 收束报告**（V0.1-V1.5 全部落盘）
- **2 套汇报模板**（markdown 轻量 + final-report-template HTML 高密度）
- **6 ADR 决策**（worklogs/decisions/）
- **97 commits**（5/26 → 6/11 完整链可追）
- **V2.1 新增脚本 11 个**（7 L1 checker + 4 commit-msg hook）
- **V2.3 新增脚本 5 个**（check_exemption_log / check_updated_tag / check_convergence_gate commit-msg hook + hook_updated_tag_posttooluse PostToolUse 护栏 + backfill_updated_tag 回填工具）

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

<!-- convergence-gate: last_converged_fp=46 threshold=3 -->
> **收束闸门**（V2.3 #52）：`last_converged_fp` = 上次收束覆盖到的最大功能点编号；`threshold` = 允许的未收束已完成功能点上限。`check_convergence_gate.py` 在提交把该数推过阈值时拦截。人触发收束后上调本标记即释放。

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
| **v2.1** | **2026-06-11** | **#36-#46 (11 件)** | **✅** | **✅ 68/75 (7 既存)** | **✅ 0红线** | **⏳ 待签核** | **✅** | **AI-workflow 7 既存失败待修 / STATUS-开发清单 功能点数口径差异 (WARN)** |

> **人审计签核说明**（2026-06-10 补）：v0.1 已签核（见 `docs/reports/人审计签核-v0.1.md`）；v0.2–v1.5 共 13 个节点为单人项目延后签核，目标 **2026-06-30** 前补齐。详见 `docs/reports/2026-06-10_强制性约束审查与修复/`。

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

> **口径**：行尾带 fp 标签（`fp` HTML 注释）的行 = 与 `开发清单.md` 对齐的 **46 个编号功能点**（#1–#46）。
> 表中另含 **11 行 V0.6–V1.5「衍展规范」**（09-dashboard…17-contributing + final-report-template + 汇报HTML×2）——这些在 STATUS 留档但从未进开发清单，**未打标、不计入 46**。`check_plan.py` 只数 fp 标签做跨文件一致性校验。

| 功能点 | BDD | 状态 | 完成日期 |
|--------|-----|------|---------|
| 架构设计规范 (01) | specs/01-architecture.md | ✅ 已完成 | - <!-- fp --> |
| 代码编写规范 (02) | specs/02-coding.md | ✅ 已完成 | - <!-- fp --> |
| Git 协作规范 (03) | specs/03-git.md | ✅ 已完成 | - <!-- fp --> |
| API 设计规范 (04) | specs/04-api.md | ✅ 已完成 | - <!-- fp --> |
| 测试规范 (05) | specs/05-testing.md | ✅ 已完成 | - <!-- fp --> |
| 文档规范 (06) | specs/06-documentation.md | ✅ 已完成 | - <!-- fp --> |
| AI 协作开发流程 (07) | specs/07-ai-workflow.md | ✅ 已完成 | - <!-- fp --> |
| 项目基础设施搭建 | specs/00-infrastructure-template.md | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 统一模板 + BDD 规格 | specs/00-infrastructure-template.md | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 01-架构 模板改造 | specs/01-architecture.md | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 02-代码 模板改造 | specs/02-coding.md | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 03-Git 模板改造 | specs/03-git.md | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 04-API 模板改造 | specs/04-api.md | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 05-测试 模板改造 | specs/05-testing.md | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 06-文档 模板改造 | specs/06-documentation.md | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 示例代码库 | specs/08-examples.md | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 仪表盘自动生成 | specs/09-dashboard-gen.md | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 基础设施修正（审查修复） | - | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 二轮审查修复（全量复查） | - | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 文件图谱 + 仪表盘优化 | specs/09-dashboard-gen.md | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 统一模板规约 + 汇报模板 | specs/10-templates-reporting.md | ✅ 已完成 | 2026-05-26 <!-- fp --> |
| 5处现有规范增强（图谱v2第一步） | specs/01-06-07 | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| 第08号规范初稿（图谱v2第二步） | specs/08-code-understanding.md | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| BDD规格：现有规范增强 + 08规范 | specs/01-08 | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| 示例代码：src/code-understanding/ | - | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| 交叉引用更新：FILE_GRAPH + README + CLAUDE | - | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| 文件夹重整：提取模板+补齐AI模板+消除重叠 | specs/10-templates-reporting.md | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| 合并 plan/ + design/ → docs/plan/ | - | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| decisions 移入 worklog + 约束节点决策总结规则 | - | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| CLAUDE.md ↔ README 角色分离（13 个 README 更新） | - | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| 汇报体系纳入 ai-workflow（新建 07-汇报.md + 流程集成） | specs/10-templates-reporting.md | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| 汇报与收束定义修正（CLAUDE/06/07 三文件对齐） | - | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| ai-workflow 流程修订（角色/收束闸门/可观测/档位）+ README 命名规范化 + 收束术语统一 | specs/07-ai-workflow.md | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| 规范正文 v2.0 重构（01-06/08 细化挂接+红线自动检测+去重+图谱收拢）+ 7 份 BDD realign + src 落地配置(5) + CLAUDE 三件套(根/模板/导航) + 汇报定义澄清(功能点级内联不落盘，9 处文档对齐) | specs/01-08 | ✅ 已完成 | 2026-05-27 <!-- fp --> |
| 第08号规范 v3.0 重构（双图谱范式：CodeGraph + Understand-Anything 替代图数据库+Cypher+Mermaid） | specs/08-code-understanding.md | ✅ 已完成 | 2026-05-28 <!-- fp --> |
| 09-dashboard-gen 规范入 _meta.yaml + dashboard.html 自动渲染 | specs/09-dashboard-gen.md | ✅ 已完成 | 2026-06-07 (V0.6) |
| 10-templates-reporting 规范入 _meta.yaml + 模板规约 | specs/10-templates-reporting.md | ✅ 已完成 | 2026-06-07 (V0.7) |
| 11-readme 规范入 _meta.yaml + README 双件套分离 | specs/07-ai-workflow.md | ✅ 已完成 | 2026-06-07 (V0.9) |
| 12-codeowners 规范入 _meta.yaml + .github/CODEOWNERS | - | ✅ 已完成 | 2026-06-07 (V1.0) |
| 13-changelog 规范入 _meta.yaml + CHANGELOG.md | - | ✅ 已完成 | 2026-06-07 (V1.1) |
| 14-security 规范入 _meta.yaml + SECURITY.md + gitleaks | - | ✅ 已完成 | 2026-06-07 (V1.1) |
| 15-support 规范入 _meta.yaml + SUPPORT.md | - | ✅ 已完成 | 2026-06-07 (V1.2) |
| 16-license 规范入 _meta.yaml + LICENSE (MIT) | - | ✅ 已完成 | 2026-06-07 (V1.3) |
| 17-contributing 规范入 _meta.yaml + CONTRIBUTING.md | - | ✅ 已完成 | 2026-06-07 (V1.4) |
| **final-report-template 沉淀**（高密度学术风 HTML 模板：11 Mermaid + 3 Tab + 5 进度条 + 2 数字滚动 + 1 模拟器） | - | **✅ 已完成** | **2026-06-08 (V1.5)** |
| **V1.x 收尾汇报 HTML × 2**（原始版 + render.py 渲染版） | - | **✅ 已完成** | **2026-06-08 (V1.5)** |
| #36 增强 check_worklog_ref.py（worklog 文件存在性验证） | - | ✅ 已完成 | 2026-06-11 (V2.1) <!-- fp --> |
| #37 🆕 check_status_updated.py（worklog ↔ STATUS 同步钩子） | - | ✅ 已完成 | 2026-06-11 (V2.1) <!-- fp --> |
| #38 🆕 check_worklog_structure.py（worklog 内容结构校验） | - | ✅ 已完成 | 2026-06-11 (V2.1) <!-- fp --> |
| #39 markdownlint 规则审计 + 分批启用（MD001/MD012/MD031/MD047/MD058；MD022/MD032 延后） | - | ✅ 已完成 | 2026-06-11 (V2.1) <!-- fp --> |
| #40 🆕 check_status.py（STATUS.md 章节级 L1）+ test_status.py L4 | - | ✅ 已完成 | 2026-06-11 (V2.1) <!-- fp --> |
| #41 🆕 check_claude.py（CLAUDE.md 章节级 L1）+ test_claude.py L4 | - | ✅ 已完成 | 2026-06-11 (V2.1) <!-- fp --> |
| #42 🆕 check_plan.py（开发清单.md 章节级 L1 + STATUS 交叉校验）+ test_plan.py L4 | - | ✅ 已完成 | 2026-06-11 (V2.1) <!-- fp --> |
| #43 dashboard 渲染 strict 模式（safe_substitute→substitute + parse_status warn + status_pre_check） | - | ✅ 已完成 | 2026-06-11 (V2.1) <!-- fp --> |
| #44 🆕 check_template_drift.py（5 类入口文件章节存在性对比） | - | ✅ 已完成 | 2026-06-11 (V2.1) <!-- fp --> |
| #45 🆕 check_file_placement.py（新文件 vs FILE_GRAPH 决策树，commit-msg hook） | - | ✅ 已完成 | 2026-06-11 (V2.1) <!-- fp --> |
| #46 🆕 check_convergence_artifacts.py（收束节点 ADR + 收束报告存在性 CI 检查） | - | ✅ 已完成 | 2026-06-11 (V2.1) <!-- fp --> |
| #47 ai-workflow 旧文件引用语义重映射 + 模板同步（conventions/01-08 + docs/templates/ 12+ 处死链语义重映射；模板 `docs/templates/devguard/scripts/check_ai_workflow.py` V1.0 旧 7 篇硬编码 → 新 9 篇） | - | ⏳ 待开始 | - |
| #48 统一 HTML 模板族 + 格式强制措施（汇报 / 计划 / 实施设计 / 绘图素材库 四套权威 HTML 模板沉淀进 docs/templates/ + 登记 README-模板索引/FILE_GRAPH；并为这些产出物建章节/结构校验钩子，对标 #40-#42 章节级 L1） | - | ⏳ 待开始 | - |
| #49 基准约束脚手架（可一键复制到新项目的最小约束基线：钩子 + CI + _meta.yaml + 模板的脚手架打包） | - | ⏳ 待开始 | - |
| #50 交流 agent + 对应强制措施（需求对齐 / 决策澄清的协作 agent 定义 + 其落地的强制措施） | - | ⏳ 待开始 | - |
| #51 豁免登记强制化（meta/豁免清单.md 账 + check_exemption_log.py commit-msg 钩子：用 [skip-*] 必须登记+同步暂存账，否则拦截；--audit 审计；7 L4） | - | ✅ 已完成 | 2026-06-11 (V2.3) |
| #52 长程任务流程强制规范操作（长程任务的 cron self 监控 / 收束闸门 / 断档防护等流程从自律升级为工具强制） | - | ⏳ 待开始 | - |
| #53 「更新时间」标签强制化（补全 CLAUDE/README 缺失标签 + check_updated_tag.py commit-msg 硬拦 + hook_updated_tag_posttooluse.py PostToolUse 阻断 + .claude/settings.json + 4 L4） | - | ✅ 已完成 | 2026-06-11 (V2.3) |
| #54 更新标签全仓泛化（钩子范围 6→全仓 159 在范围 .md；backfill_updated_tag.py 回填 153 文件取 git 末次修改日；排除 templates/worklogs/.github/CHANGELOG；全仓 markdownlint 通过） | - | ✅ 已完成 | 2026-06-11 (V2.3) |
| #52 收束硬闸门（check_convergence_gate.py commit-msg 钩子 + STATUS 机器标记 last_converged_fp/threshold；交付提交把未收束完成数推过阈值时拒提交，staged vs HEAD 比对不冻结非交付提交；豁免 [skip-gate]；5 L4） | - | ✅ 已完成 | 2026-06-11 (V2.3) |
