# 项目介绍 · devguard（PRD 不变量）

> **本文档是本项目的 PRD 与整理工作的验收基准（不变量契约）。**
> 更新: 2026-08-13
>
> - 本文档描述 devguard **应当是什么样**（目标态），不是现状快照。现状数据以 `STATUS.md` 为真源。
> - **任何整理、重构、优化工作，不得破坏第五节「不变量清单」中的任何一条**；与不变量冲突的改动需先修订本文档并经 Owner 拍板。
> - 术语与流程定义以 `conventions/ai-workflow_AI协作开发流程/` 为最高依据，本文档只做体系级描述，不重新定义流程。

---

## 一、项目定位

**devguard 是一套"项目开发初始体系"：把通用开发规范、AI 协作流程、可执行治理闸门与一键初始化打包，让任何新项目（或个人/团队）在单条命令内获得一套自洽、可强制、可验证的开发底座。**

它解决四类问题：

| 问题 | devguard 的答案 |
|------|----------------|
| 新项目启动无统一基准，风格靠人记 | 17 篇规范 + 9 篇 AI 协作流程，随项目初始化即自带 |
| 规则写了没人执行，Review 靠人肉 | 19 个提交钩子 + 5 阶段 CI + 故障注入测试，机器拦截 |
| AI 协作无结构，会话记忆不连续 | CLAUDE.md/AGENTS.md 双入口 + skills-first + worklog/STATUS 强制汇报 |
| 模板项目复制靠 cp，夹带垃圾 | 显式 manifest 脚手架 + 事务化原子写入 + dry-run/verify |

---

## 二、体系全景

```mermaid
flowchart TB
    subgraph L1["入口层（双入口）"]
        H1["👤 人类 → README.md"]
        A1["🤖 AI → CLAUDE.md / AGENTS.md"]
    end

    subgraph L2["规范层（说什么）"]
        C1["17 篇规范<br/>01-08 原始 + 09-17 衍展"]
        C2["AI 协作开发流程 9 篇<br/>双轨制：长程任务 / 思考任务"]
        C3["BDD 规格 00-10<br/>规范 ↔ 验收互检"]
    end

    subgraph L3["资产层（用什么）"]
        T1["模板族<br/>docs/templates/"]
        T2["脚手架载荷<br/>scaffold/core + optional<br/>（manifest 显式声明）"]
        T3["可运行示例 src/<br/>按规范维度组织"]
    end

    subgraph L4["治理层（怎么强制）"]
        G1["19 个 pre-commit / commit-msg 钩子"]
        G2["5 阶段 CI<br/>lint→test→l4→compliance→build"]
        G3["check_* 治理脚本 23 个（其中 19 个为 pre-commit/commit-msg 钩子）<br/>一致性 / 拦截率 / 收束闸门"]
        G4["210 tests（tests/conventions/）"]
    end

    subgraph L5["交付层（产出什么）"]
        D1["新项目（一键初始化）"]
        D2["仪表盘 dashboard.html<br/>+ STATUS.md"]
        D3["收束报告 / ADR / worklogs"]
    end

    H1 --> C1
    A1 --> C2
    C1 <--> C3
    C2 --> C3
    C3 --> T1
    C1 --> T2
    C3 --> T3
    T2 --> G1
    C3 --> G3
    G3 --> G2
    G4 --> G2
    G1 --> D1
    G2 --> D1
    G3 --> D2
    G1 --> D3
```

**一句话读图**：入口层决定"谁在看" → 规范层定义"该怎么做" → 资产层提供"可复制的东西" → 治理层用机器保证"不做就拦截" → 交付层产出"新项目与过程证据"。

---

## 三、核心工作流

### 3.1 新项目初始化（易部署性主链路）

```mermaid
flowchart TD
    S["新项目空目录<br/>或已有目录（非空默认拒绝）"] --> B{引导方式}
    B -->|"macOS / Linux"| SH["bash scripts/install.sh"]
    B -->|"Windows"| PS["powershell install.ps1"]
    B -->|"直接调用"| PY["python3 scripts/setup_scaffold.py"]
    SH --> P1["预检：Python ≥3.10<br/>（缺失 → 分平台指引并退出，fail-closed）"]
    PS --> P1
    PY --> P1
    P1 --> P2["定位 devguard 仓<br/>（当前目录 / --repo / DEVGUARD_REPO）"]
    P2 --> MODE{模式}
    MODE -->|"--dry-run"| DR["预演：零写入，输出将写清单"]
    MODE -->|"--verify"| VF["复验既有目标<br/>（--require-hooks 强制钩子在场）"]
    MODE -->|"--install"| IN["读显式 manifest<br/>core 必装 + optional 选装"]
    IN --> AT["逐文件原子替换写入<br/>失败 → 回滚已写文件"]
    AT --> OK["初始化完成：<br/>Git init + 双入口 + skill + 固定依赖<br/>+ 最小 CI + 自检测试 + 19 钩子 + 隔离 .venv"]
```

### 3.2 双轨任务流程（AI 协作主链路）

```mermaid
flowchart TD
    TASK["新任务"] --> J{"任务类型？"}
    J -->|"长程任务（代码产出）"| L1["AI 决策（ADR）"]
    L1 --> L2["预先计划"]
    L2 --> L3["迭代开发：<br/>扫描 → 实现 TDD → 验证 → 审查 → commit"]
    L3 --> R1["【AI 汇报】必做：<br/>worklog + STATUS 更新"]
    J -->|"思考任务（方案设计）"| S1["讨论 Agent 五步法<br/>笔记 → 引导 → 设计 → HTML 汇报 → 记录整理"]
    S1 --> R1
    R1 --> G{"收束节点到点？<br/>（默认每 3 功能点）"}
    G -->|"否"| L3
    G -->|"是"| C["【人触发】四阶段收束<br/>整理 → 测试 → 审计（AI+人）→ 验证"]
    C --> ADR["ADR + 收束报告落盘"]
    ADR --> L3
```

### 3.3 治理强制链（强制约束性主链路）

```mermaid
flowchart LR
    E["编辑文件"] --> C1["git commit"]
    C1 --> H1["pre-commit 19 钩子<br/>格式/安全/一致性/文件放置/豁免/同步"]
    H1 -->|"拦截 ✋"| E
    H1 -->|"通过 ✓"| H2["commit-msg<br/>Conventional Commits"]
    H2 -->|"拦截 ✋"| E
    H2 -->|"通过 ✓"| P["git push"]
    P --> CI["5 阶段 CI<br/>lint → test → l4-conventions → compliance → build"]
    CI -->|"失败 ✋"| E
    CI -->|"通过 ✓"| M["PR 合入 master<br/>（main 禁直推）"]
    M --> CONV["收束闸门：<br/>到点未收束 → 拒绝启动新功能点"]
```

### 3.4 真源数据流（稳定性主链路）

```mermaid
flowchart LR
    SRC["conventions/_meta.yaml<br/>（真源：分级 / 工具链版本 / 路由）"] --> RM["scripts/render_meta.py"]
    RM --> R1["规范顶部「分级标签」"]
    RM --> R2["根 .pre-commit-config.yaml"]
    RM --> R3["README 分级表"]
    SRC --> CK["check_consistency.py<br/>+ check_enforcement.py<br/>（故障注入 ≥10 项）"]
    R1 --> CK
    R2 --> CK
    R3 --> CK
    CK -->|"一致 ✓ / 拦截率 ≥90% ✓"| CI["CI compliance 阶段"]
    CK -->|"漂移 ✋"| FIX["修复漂移 → 回到 SRC"]
```

**真源原则**：`_meta.yaml` 是唯一手维护源头；渲染产物（分级标签、pre-commit 配置、README 表）禁止手改；漂移由 CI 与故障注入测试兜底。

---

## 四、目录体系

```
devguard/
├── conventions/            # 规范正文：17 篇 + ai-workflow 流程 9 篇 + 双导航
├── docs/
│   ├── plan/               # 计划：背景 + 开发清单 + design/ + 本 PRD
│   ├── specs/              # BDD 规格 00-10
│   ├── templates/          # ★模板权威（含 scaffold 一键初始化载荷）
│   ├── reports/            # 收束报告 / 验收报告
│   ├── research/           # 调研产出
│   └── 历史文件/            # 只读归档（v1.0 旧版流程等）
├── src/                    # 可运行示例（按规范维度）
├── scripts/                # 治理脚本 + 渲染器 + 安装器
├── tests/                  # 210 测试（一致性 / 强制力 / 性能基线）
├── worklogs/               # 工作日志 + decisions/（ADR）
├── meta/FILE_GRAPH.md      # ★文件放置权威（新文件先查决策树）
├── CLAUDE.md               # AI 入口（本仓实例）
├── README.md               # 人类入口（本仓实例）
├── STATUS.md               # 进度数据源（dashboard 解析）
└── dashboard.html          # 可视化面板
```

> 文件放置以 `meta/FILE_GRAPH.md` 决策树为唯一权威；本图只做概览，不替代决策树。

---

## 五、不变量清单（PRD 硬契约）

> 整理/优化工作的验收基准。**破坏任意一条 = 未通过**。
> 每条附「验证方式」，优先自动化；无法自动化的为人工检查项。

### A. 易部署性

| ID | 不变量 | 验证方式 |
|----|--------|---------|
| D1 | 全新环境单命令可初始化出可用项目（bash / PowerShell / 直接调用三路等价） | `setup_scaffold.py --dry-run` 零写入预演 + 真机 E2E 演示 |
| D2 | 初始化载荷由显式 manifest（core/optional）声明，**禁止夹带** devguard 自身资产（worklogs、node_modules、.venv 等） | manifest 清单比对 + E2E 产物 diff |
| D3 | 初始化具备事务语义：任何一步失败回滚已写文件，目标目录不留半成品 | 故障注入测试（中断写入 → 校验目录） |
| D4 | 预检 fail-closed：Python 缺失/版本不足、仓定位失败时给出明确指引并退出，不静默降级 | E2E 注入缺失场景 |
| D5 | 提供 `--verify` 复验能力，`--require-hooks` 强制钩子在场 | E2E 复验既有目标 |
| D6 | 不修改用户全局 Git 配置；与既有 ECC/全局 hooksPath 可共存（串联而非覆盖） | E2E 双钩子场景 |

### B. 强制约束性

| ID | 不变量 | 验证方式 |
|----|--------|---------|
| C1 | 每篇规范有对应自动检测（L1 检测），规范 ↔ BDD ↔ 闸门一一可追溯 | `render_meta.py --check` + specs/ 互检 |
| C2 | 提交前拦截完整：19 个钩子（格式/安全/一致性/提交格式/worklog/STATUS/文件放置/豁免/同步/收束）全部在场且可执行 | `pre-commit run --all-files` + `check_enforcement.py` |
| C3 | 提交后拦截完整：5 阶段 CI（lint/test/l4-conventions/compliance/build）全部在 .github/workflows/ 且与本地闸门同源 | CI 配置比对 + 故障注入 |
| C4 | 收束闸门硬执行：到点未收束，AI 拒绝开始新功能点 | `check_convergence_gate.py` |
| C5 | 密钥/敏感信息在提交前被拦截（gitleaks） | pre-commit 故障注入 |
| C6 | 豁免（exemption）可审计：每一次破例有记录、有所有者、有到期 | `check_exemption_log.py` |

### C. 稳定性

| ID | 不变量 | 验证方式 |
|----|--------|---------|
| S1 | 工具链版本单一真源：`_meta.yaml` 与 CI、pre-commit、requirements、pyproject、脚手架载荷**全部一致**，零漂移 | `check_consistency.py`（一致性事实矩阵 ≥95%） |
| S2 | 测试基线可复现：全新 `.venv` 按固定依赖安装后 210 tests 全绿 | 自举重建脚本 + `pytest tests/` |
| S3 | 强制力有量化的故障注入证明：隔离 Git 故障注入拦截率 ≥90% | `check_enforcement.py` |
| S4 | 渲染产物禁止手改：分级标签/README 分级表/pre-commit 配置漂移即 CI fail | `render_meta.py --check` 入 CI |
| S5 | 文档与代码同 PR：改规范必须同步 BDD，动落地配置必须同步 src/ 示例 | `check_doc_sync.py` |
| S6 | 汇报必做：每功能点 worklog + STATUS 更新，无断档 | `check_worklog_ref.py` + `check_status.py` |
| S7 | 进度数据单真源：STATUS.md → dashboard 自动渲染，不手改 HTML | `render_dashboard.py` + 渲染产物比对 |

### D. 通用（贯穿三特性）

| ID | 不变量 | 验证方式 |
|----|--------|---------|
| G1 | 人/AI 双入口持续有效：README（人）与 CLAUDE/AGENTS（AI）角色分离、互不替代 | `check_claude.py` |
| G2 | 术语与流程不漂移：任何体系描述不得重新定义 ai-workflow 既有术语（双轨制/收束节点/真源等） | 人工检查（文档审查） |
| G3 | 新增/移动文件必须先查 `meta/FILE_GRAPH.md` 决策树，并同步更新图谱 | `audit_file_placement.py` |
| G4 | ADR 仅收束节点产出，日常决策记 worklog「关键决策」段 | 人工检查（收束审计） |
| G5 | 技术债有登记、有归属节点、不无限积压 | STATUS.md 技术债表 |

---

## 六、与现状的对照（整理路线）

> 本 PRD 落盘后，按以下顺序开展整理。每阶段完成时对照第五节逐条验收。

| 阶段 | 工作 | 主要验收不变量 |
|------|------|--------------|
| 1 整理 | 未提交改动合规入库；历史文件去留拍板；.workbuddy 清理；FILE_GRAPH 同步 | G3, C2, S6 |
| 2 修复 | venv 可复现重建；ruff 钉版对齐；install.sh 健壮性（ensurepip 预检/失败清理） | S2, S1, D4, D3 |
| 3 优化 | 一键自检脚本；约束覆盖率矩阵；版本真源校验入 CI；跨平台 CI | D1-D6, B 全部, S1-S4 |

> 现状详情（测试数、钩子数、阻塞项、技术债）以 `STATUS.md` 为真源，此处不复制。

---

**维护者**：袁 (xiangbianpangde) ｜ **版本**：PRD v1.0 ｜ **许可**：MIT License
