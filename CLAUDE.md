# 通用开发规范 — AI 项目上下文

> **⚠️ 仅供 AI Agent 读取**，新会话自动加载。人类请读 `README.md`。
> 每次功能点完成后更新本文件。新增文件前先查 `meta/FILE_GRAPH.md`。
> 更新: 2026-06-11（V2.3 阶段B #53：「更新时间」标签强制化）

---

## 项目概述

纯文档项目（Markdown 规范 + Python 示例），Git 管理。本身就是一套"可复制到新项目"的开发规范模板。49 个功能点全部交付，可投入使用。

**本项目的核心设计**：`conventions/` 里的 6+1 份规范不是孤立文档，而是 `conventions/ai-workflow_AI协作开发流程/` 协作流程各步骤的**细化**——流程讲"什么时候做什么"，规范讲"那一步具体怎么做、红线是什么、配置怎么落地"。

---

## 目录索引

```
开发规范/
├── conventions/                  # 规范正文（01-06,08）+ ai-workflow_*/（流程 7 篇）
│   ├── CLAUDE-规范导航.md         #   AI 入口：任务→规范定位 + 红线总表 + 去重映射
│   └── README-规范导航.md         #   人类入口：快速索引 + 红线速查
├── docs/
│   ├── templates/                # 模板权威来源 → README-模板索引.md
│   ├── specs/                    # BDD 规格（00-10，与规范互检）
│   ├── plan/                     # 背景 + 开发清单 + design/
│   ├── reports/                  # 汇报产出
│   └── research/                 # 调研
├── worklogs/                     # 工作日志 + decisions/（ADR，仅收束节点产出）
├── src/                          # 示例代码（按规范维度分目录）→ README-示例代码总览.md
├── scripts/                      # start_server.py / 打开仪表盘.bat
├── meta/FILE_GRAPH.md            # 文件归类权威（"新文件放哪"决策树）
├── CLAUDE.md                     # 本文件（AI 上下文）
├── README.md                     # 人类使用指南
├── STATUS.md                     # 进度数据源（dashboard 解析它）
└── dashboard.html                # 可视化面板
```

---

## 引用关系（改一处要同步哪些）

```
conventions/ (01-08)  ←互检→  docs/specs/ (01-08)
        │ 细化自                       ↑ 验收
        ↓                              │
conventions/ai-workflow/ (流程)   src/<维度>/（规范 §二落地配置的可运行版）
        │
docs/plan/开发清单.md → STATUS.md → dashboard.html
        ↓ 每功能点
worklogs/ ──收束节点──→ worklogs/decisions/（ADR）
```

---

## 核心规则

1. **文件放置**：新增文件前必查 `meta/FILE_GRAPH.md` 决策树，禁止根目录堆散文件。
2. **改规范** → 同步对应 `docs/specs/` BDD；若动到落地配置，同步 `src/<维度>/` 示例。
3. **新增功能点** → `STATUS.md` + `docs/plan/开发清单.md` 各加一行 + 按需建 BDD。
4. **去重**：同一主题只在一处权威（如密钥→02，调用图/图谱→08），其余引用不复制。
5. **ADR** 仅收束节点产出（`worklogs/decisions/`）；日常取舍记 worklog「关键决策」段。
6. **人读 README，AI 读 CLAUDE**。
7. **严格按既定方法论/规范执行** — 不自创抽象层/流程/术语。原方法论没说清楚的地方，**停下来问**而不是猜。

## AI 协作原则

启动一项工作前，按此顺序对齐：

1. **先对齐需求** — 模糊任务先用 `plan-mode` / `prompt-optimizer` skill 整理，或直接问关键决策点。
2. **先想好再行动** — 任务有歧义 / 多方案 / 改动面大时，先列方案让用户拍板再动代码。
3. **创建团队完成 status 内的任务** — 任务跨 3+ 独立轨道 / 需要独立验证 / 跨工具时，`mavis-team` 编排；单步骤低复杂度任务自己干。
4. **长程 `mavis-team` plan 必须设 `cron self` 监控** — 计划超过 30 分钟或跨 daemon 生命周期时，owner 必须设 self-reminder 防止 daemon 崩溃无人接管。

## 质量验证原则

- **真机 E2E 验证** — 不接受 demo 视频 / 录屏自我证明；前端改动必须真实浏览器渲染并亲眼确认；接口改动必须真实调用并核对返回数据。
- **演示/录屏 = 伪证据** — 对可视化/渲染类功能，HTTP 200 / tsc 0 错误 / 截图都**不能**充当合格证据，必须看到真实功能在真实环境跑通。

---

## 规范速查（每篇细化哪一步 + 红线 + AI 任务路由）

| # | 规范 | 细化的流程环节 | 红线（详见各篇 §一）| AI 任务路由 |
|---|------|---------------|------|------|
| 01 | 架构 | 第一步·设计 | 禁循环依赖 / 领域层不依赖框架 / 禁跨层调用 | 任务类型=架构设计 → 必读本篇 |
| 02 | 代码 | 第二步 §2.1 实现 + §2.3 审查 | 禁 print / SQL 参数化 / 密钥走环境变量 / 禁静默吞异常 / 日志脱敏 | 任务类型=实现 → 必读本篇 |
| 03 | Git | 第二步 §2.6 提交 | main 禁直推 / Conventional Commits / 禁 force push 共享分支 | 任务类型=提交 → 必读本篇 |
| 04 | API | 第二步 §2.1 接口 | 名词复数+kebab-case 无动词 / 统一响应 / 默认认证 / 向后兼容 | 任务类型=接口设计 → 必读本篇 |
| 05 | 测试 | §2.1 TDD + §2.2 验证 | 测试独立 / 只 Mock 外部边界 / 覆盖正常+边界+异常 | 任务类型=实现 → 必读本篇 |
| 06 | 文档 | §2.5 + 08-汇报收束 | 必有 README / 发布更 CHANGELOG / 文档随码同 PR | 任务类型=写文档 → 必读本篇 |
| 08 | 图谱 | 第二步 §2.9 工具增强 | 双图谱：CodeGraph（AI）+ Understand-Anything（人） | 任务类型=图谱生成 → 必读本篇 |

> 每篇结构：§一红线（配自动检测）→ §二落地配置（复制即用）→ §三决策表 → 反模式 → 检查清单。
> AI 任务路由来自 `conventions/_meta.yaml` 的 `l3_route` 字段；改 _meta.yaml 后请同步本表。

---

## 工作流程

> 流程全文见 `conventions/ai-workflow_AI协作开发流程/`（01-07 共 7 篇）。

```
第零步 调研 ──→ 第一步 计划（含预设收束节点）──→ 第二步 迭代开发（每功能点循环）
                                                       │
                                              扫描仓库→实现(TDD自检)→可观测验证
                                              →审查 diff→人确认→更新记录→commit
                                                       │
                                              【AI 汇报】必做，不可跳过
                                                       │
                                              【收束节点】人触发，AI 到闸门拦截
                                              四阶段：整理→测试→审计→验证 → ADR + 收束报告
```

| 项 | 说明 |
|------|------|
| **汇报（AI 必做）** | 每功能点完成更新 `worklogs/YYYY-MM-DD_*.md` + `STATUS.md`（必做）；功能点级汇报**默认对话内联、不落盘**，只有收束报告落盘 `docs/reports/`（详见 `08-汇报收束.md`）|
| **收束节点（人触发）** | 计划时预设（默认每 3 功能点）写入 `开发清单.md` 头部成硬闸门。**到点未收束时 AI 拒绝开始下一功能点**并提醒；AI 不替人做收束 |
| **核心原则** | 不越界 / 不黑盒 / 不断档 / 不拖欠 / 不积压（见 `ai-workflow_AI协作开发流程/README.md`） |

---

## 当前状态

- **进度**：46/46 ✅（35 原始 + 11 V2.1 流程强制化）全部交付；**V2.3 进行中**：#51 豁免登记 + #53/#54 更新时间标签（全仓 159 文档回填）✅（#48-#50/#52 待开始，见 `docs/plan/design/设计提案-约束与模板强化方案-v2.3.md`）
- **规范版本**：01-06 升至 **v2.0**，08 升至 **v3.0**（双图谱范式：CodeGraph + Understand-Anything）；`src/<维度>/` 配有对应的可运行落地配置
- **ADR**：6 个（`worklogs/decisions/0001-0006`）
- **收束节点**：v0.1–v2.1 共 15 个节点已执行；其中 **v0.1 已人审计签核**，v0.2–v2.1（14 个）人审计仍 ⏳ 待签核
- **V2.1 流程强制化**：11 个功能点 #36-#46 全部交付。**pre-commit 钩子从 10 增至 13**（新增 4 个 commit-msg hook：worklog 存在性验证 #36、worklog↔STATUS 同步 #37、worklog 结构校验 #38、文件放置检查 #45），**CI 新增 5 个 check step**（STATUS/CLAUDE/开发清单 章节级 L1 + 模板漂移 + 收束产物），**L4 测试从 65 增至 68**（+test_status/test_claude/test_plan）
- **V2.3 约束与模板强化（进行中）**：#51 豁免登记（`meta/豁免清单.md` + `check_exemption_log.py`，用 `[skip-*]` 必须登记并同步暂存账，本钩子不可豁免）+ #53 更新时间标签（`check_updated_tag.py` commit-msg 硬拦 + `hook_updated_tag_posttooluse.py` PostToolUse 阻断 + `.claude/settings.json`，受管文档提交须刷新 `> 更新:` 为今天；#54 把范围从 6 入口泛化到全仓 159 在范围 .md 并回填 153 文件，排除 templates/worklogs/.github/CHANGELOG）。**pre-commit 钩子从 13 增至 15**（commit-msg 7 个）+ **1 PostToolUse 钩子**，**L4 测试 98 passed**（+test_exemption_log 7 + test_updated_tag 5）
- **遗留问题**：`render_meta.py --check` 的 convention-grade 对 09-17 非 md 衍展规范（LICENSE/CODEOWNERS 等）无法注入分级表（独立技术债，#51 未触及）；STATUS/开发清单功能点数口径差异（WARN 级，方案风险章节允许）

---

## 常见任务速查

| 用户说 | AI 做什么 |
|--------|----------|
| "修改规范" | 改 `conventions/NN-*.md` → 同步 `docs/specs/` →（动配置则同步 `src/<维度>/`）→ 汇报 |
| "新增功能点" | `STATUS.md` + `开发清单.md` 加行 → 按需建 BDD → 汇报 |
| "新增模板" | `docs/templates/` 新建 → 登记 `README-模板索引.md` → 更新 FILE_GRAPH → 汇报 |
| "汇报" | 更新 worklog + STATUS（必做）→ 功能点汇报直接对话里说（不落盘）；仅收束报告或人要求留档时才写 `docs/reports/` 文档 |
| "收束" | 由**人触发**执行四阶段；到达预设收束节点未收束时 **AI 主动拦截**。人确认后按 `08-汇报收束.md` 执行 → ADR + 收束报告 |
| "新增/移动文件" | 先查 `meta/FILE_GRAPH.md` 决策树 → 操作 → 同步 FILE_GRAPH → 汇报 |
