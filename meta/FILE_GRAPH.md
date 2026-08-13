# 文件架构图谱 (FILE_GRAPH)

> 本文件是仓库的**文件归类权威**。新增文件前先在此找到对应节点，按节点放置——禁止在仓库根目录随意堆放散文件。
>
> 更新: 2026-08-13 | 维护规则：新增/移动文件或目录时同步更新本图谱。
> 注：规范正文 v2.0 重构（功能点 #34）仅改内容、未增删/移动文件，故本图谱结构不变；conventions/ 各篇现为 ai-workflow 对应步骤的细化，调用图主题统一收拢于 08。

---

## 一、目录树（带职责标注）

```
开发规范/                              # 仓库根：仅放顶层入口文件，不堆散文件
│
├── conventions/                      # 【规范正文】模板核心，开发者日常查阅
│   ├── README-规范导航.md            #   快速索引 + 红线速查（人类入口）
│   ├── CLAUDE-规范导航.md            #   AI 入口：任务→规范定位 + 红线总表 + 去重映射
│   ├── 01-architecture_架构设计规范.md #   分层、依赖、模块边界
│   ├── 02-coding_代码编写规范.md       #   命名、注释、错误处理、安全
│   ├── 03-git_Git协作规范.md          #   分支、提交、PR、合并
│   ├── 04-api_API设计规范.md          #   REST、错误码、版本、安全
│   ├── 05-testing_测试规范.md         #   金字塔、AAA、Mock、覆盖率
│   ├── 06-documentation_文档规范.md   #   README、CHANGELOG、注释
│   └── ai-workflow_AI协作开发流程/  #   方法论（长文拆目录，见 ADR 0005）
│       ├── README.md                 #   文档索引 + 5 条核心原则
│       ├── 01-流程全景.md            #   双轨制两类任务（长程/思考）+ 触发条件
│       ├── 02-模块分类.md            #   工程模块 vs 基础+功能模块
│       ├── 03-设计规范.md            #   设计文件夹 7 件套 + 8 节结构
│       ├── 04-长程开发.md            #   ADR → 预先计划 → 迭代开发 → 验收报告
│       ├── 05-思考设计.md            #   讨论Agent五步法
│       ├── 06-端到端流程.md          #   PRD → BDD+TDD → 技术转换 → 模块划分 → 测试
│       ├── 07-验收交付.md            #   三级验收 + 交付物清单
│       ├── 08-汇报收束.md            #   汇报类型 + 收束节点四阶段
│       └── 09-部署规范.md            #   统一服务器部署全流程
│   └── 08-code-understanding_代码理解与图谱规范.md  #   双图谱：CodeGraph（AI）+ Understand-Anything（人）
│
├── docs/                             # 【文档资产】非规范正文的所有文档
│   ├── plan/                         #   【计划+设计】项目计划与功能设计
│   │   ├── 背景.md                   #     为什么做、设计决策
│   │   ├── 项目介绍-PRD.md           #     ★PRD 不变量：体系全景 + 流程图 + 硬契约（整理/优化验收基准）
│   │   ├── 开发清单.md                #     功能点列表 + BDD 引用 + 依赖
│   │   └── design/                   #     复杂功能设计文档（五段式）
│   │       ├── README-设计文档说明.md #       设计文档索引与模板
│   │       └── 设计提案-图谱与代码理解规范-v2.md
│   ├── reports/                      #   进度汇报（功能点/周期/阶段，从模板生成）
│   ├── research/                     #   调研文档
│   ├── 历史文件/                      #   历史归档（V0 遗留重构笔记 + ai-workflow v1.0 旧版流程，只读保留）
│   ├── specs/                        #   BDD 功能规格（00-10，逐个对应规范/功能点；08-examples 为示例代码规格，与 08 规范双编号系既定例外）
│   └── templates/                    #   ★模板权威来源（新项目从此复制）
│       ├── README-模板索引.md         #     ★模板索引 + 编写规约
│       ├── BDD规格模板.md
│       ├── CLAUDE模板.md
│       ├── README模板.md
│       ├── STATUS模板.md
│       ├── plan背景模板.md
│       ├── plan开发清单模板.md
│       ├── worklog模板.md
│       ├── 汇报模板.md
│       ├── AI审计报告模板.md
│       ├── 人审计签核模板.md
│       ├── 收束报告模板.md
│       ├── AI协作提示词模板.md
│       ├── AI会话启动模板.md
│       ├── 规范文档模板.md
│       └── devguard/                   #     devguard 项目专属资产（新项目只走 scaffold manifest）
│           ├── scaffold/               #       一键初始化权威载荷（core/optional 显式 manifest）
│           │   ├── core/AGENTS.md.tmpl #       Codex 项目入口（skills-first 路由）
│           │   ├── core/.agents/skills/devguard/ # canonical workflow skill + OpenAI 元数据
│           │   ├── core/.codex/config.toml #    credential-free 项目本地安全基线
│           │   └── core/scripts/install_hooks.py # ECC/全局 Hook 与项目 Hook 的可重入组合安装器
│           ├── html-report-template/   #       自动 dashboard 渲染（_meta.yaml + STATUS.md）
│           └── final-report-template/  #       高密度学术风 HTML 报告（Mermaid+Tab+交互，V1.x 收尾定型）
│
├── src/                              # 【示例代码】按规范维度分目录（非产品结构）
│   ├── README-示例代码总览.md        #   组织方式说明（重要：见此文件）
│   ├── architecture/                 #   ← 01 规范：四层架构 + DI
│   ├── coding/                       #   ← 02 规范：命名/错误/安全
│   ├── git/                          #   ← 03 规范：gitignore/hooks 配置
│   ├── api/                          #   ← 04 规范：FastAPI 微服务
│   ├── testing/                      #   ← 05 规范：pytest 单测
│   └── documentation/                #   ← 06 规范：CHANGELOG/docstring
│   └── code-understanding/           #   ← 08 规范：AST 调用图教学示例（真实项目用 CodeGraph + Understand-Anything）
│
├── worklogs/                         # 【工作日志】每个功能点一份 YYYY-MM-DD_描述.md
│   └── decisions/                    #   ADR 架构决策记录（收束节点产出，见 ADR 0006）
│
├── scripts/                          # 【工具脚本】仪表盘启动等辅助脚本
│   ├── install.sh                    #   POSIX 一键引导（探测 Python≥3.10 → 调 setup_scaffold）
│   ├── install.ps1                   #   Windows PowerShell 一键引导（同 install.sh）
│   ├── setup_scaffold.py             #   自包含治理基线一键初始化/复验
│   ├── render_dashboard.py           #   Windows/POSIX 共用 dashboard 渲染入口
│   ├── check_consistency.py          #   一致性事实矩阵（阈值 >=80%）
│   ├── check_enforcement.py          #   隔离 Git 故障注入矩阵（阈值 >=90%）
│   ├── check_ecc_alignment.py        #   ECC 十域能力对标矩阵（阈值 >=80%）
│   ├── check_*_*.py                  #   worklog/STATUS/放置/豁免/日期/同步/收束闸门
│   ├── start_server.py               #   本地预览服务器（dashboard 入口）
│   └── 打开仪表盘.bat                 #   双击启动 dashboard
│
├── meta/                             # 【元信息】描述仓库自身的文件
│   ├── FILE_GRAPH.md                 #   本文件：文件归类权威
│   └── 豁免清单.md                    #   [skip-*] 合法目录与逐次使用账
│
├── architecture.md                   # 顶层：★当前架构总览（组件/依赖/数据流/机制；架构变更必须回写）
├── CLAUDE.md                         # 顶层：AI 项目上下文（仅供 AI 读取，新会话自动加载）
├── README.md                         # 顶层：人类使用指南（仅供人类阅读）
├── STATUS.md                         # 顶层：进度仪表盘数据源（dashboard 解析它）
├── dashboard.html                    # 顶层：可视化进度面板
├── .gitattributes                    # Python 行尾统一 LF，保证 Windows/Ubuntu formatter 同值
└── .gitignore                        # 顶层：忽略规则
```

---

## 二、引用关系图谱（谁依赖谁）

```
conventions/规范文档 (01-08)  ←──互检──→  docs/specs/BDD规格 (01-08)
        │                                        │
        │ ai-workflow/08-汇报收束          │ 验收标准
        │ （每 N 个功能点触发闸门）                  │
        │ 落地为示例                              │
        ↓                                        ↓
   src/<维度>/  ──对应──→  docs/specs/08-examples.md
                                                 │
docs/templates/ ──复制为──→ 新项目的 CLAUDE/STATUS/README/plan/worklog
        │
        ↓ 实例化
   docs/plan/开发清单.md ──引用──→ docs/specs/*    （功能点 ↔ BDD）
        ↓ 驱动
   STATUS.md ──被解析──→ dashboard.html ──由──→ start_server.py / 打开仪表盘.bat 启动
        ↓ 每个功能点产出
   worklogs/YYYY-MM-DD_*.md
        ↓ 全局总览
   CLAUDE.md（AI 上下文：目录 + 图谱 + 规则 + 任务指南）  ←── 与本 FILE_GRAPH.md 互为索引
```

**关键约束**（修改时必须同步）：
1. 改 `conventions/` 规范 → 同步对应 `docs/specs/` BDD。
2. 新增功能点 → 同时写入 `docs/plan/开发清单.md` 和 `STATUS.md`。
3. `dashboard.html` 只解析 `STATUS.md` 表格，改表头需同步改解析器。
4. 模板的权威来源是 `docs/templates/`，根目录的 `CLAUDE.md`/`STATUS.md` 等是本仓库的实例。

---

## 三、新增文件放哪？（决策树）

```
要新增一个文件，它是……
│
├─ 规范正文（某个开发维度的"应该怎么做"）？
│     → conventions/NN-<name>_<中文名>.md（单文件 > 300 行则拆为目录，见 ADR 0005）
│
├─ 某规范/功能点的验收标准（BDD）？
│     → docs/specs/NN-<name>.md（编号与功能点对齐）
│
├─ 架构总览 / 组件关系 / 依赖方向（持续维护的“当前架构是什么”）？
│     → docs/architecture.md（架构变更必须回写，与实现同 PR）
│
├─ 架构/技术选型决策（为什么选 A 不选 B）？
│     → worklogs/decisions/NNNN-<标题>.md（ADR，仅收束节点产出，见 ADR 0006）
│
├─ 项目计划与功能点清单？
│     → docs/plan/背景.md + docs/plan/开发清单.md
│
├─ 复杂功能的设计文档（背景/目标/方案/影响/风险）？
│     → docs/plan/design/设计文档-<功能名>.md
│
├─ 进度汇报（功能点完成 / 收束报告）？
│     → docs/reports/...（模板见 docs/templates/汇报模板.md）
│
├─ 调研笔记？
│     → docs/research/<主题>.md
│
├─ 可复用的文件模板？
│     → docs/templates/<类型>模板.md（并登记到 docs/templates/README-模板索引.md 索引）
│
├─ 规范的可运行示例代码？
│     → src/<对应规范维度>/...（每维度一个子目录 + README-<维度>示例.md）
│
├─ 一次功能点的开发记录？
│     → worklogs/YYYY-MM-DD_<简短描述>.md
│
├─ 工具/辅助脚本（构建、启动、部署）？
│     → scripts/<name>.py|.bat|.sh
│
├─ 描述仓库自身的元信息（图谱、约定）？
│     → meta/<name>.md
│
└─ 项目级入口（每个项目仅一份）？
      → 根目录：CLAUDE.md / README.md / STATUS.md / dashboard.html 等
      ⚠️ 除这些既定入口外，根目录不接受新散文件。
```

---

## 四、命名规约（方案 ⑨，2026-08-12 蓝队整理新增）

> 适用于**新建**文件/目录；存量文件不强制重命名（git 历史追踪成本高于收益）。

| 前缀模式 | 用途 | 示例 |
|---------|------|------|
| `NN-`（编号） | 规范 / 流程文档序号 | `01-architecture_架构设计规范.md` |
| `YYYY-MM-DD_`（日期） | 按日期的产出（worklog / 审查 / 报告） | `worklogs/2026-08-12_红蓝对抗-协作基线.md` |
| `README-` | 目录说明 / 工具使用说明 | `README-模板索引.md` |
| `设计提案-` / `设计文档-` | 设计文档（plan/design/） | `设计提案-整理大类一-文件体系与资产整理.md` |
| `check_*` / `render_*` | 治理脚本（scripts/） | `check_consistency.py` |

**规则**：
1. 分隔符：编号前缀用 `-`；日期前缀内日期用 `-`、日期与主题间用 `_`；主题内不出现空格与全角括号。
2. 中文命名允许（本仓既定风格，约 51% 文件含中文），但同目录内保持同风格（不混用纯英文与中英混合）。
3. 新增文件必须登记 FILE_GRAPH（见 §一）与对应索引（模板→模板索引、报告→reports/INDEX）。

**权限规约**（方案 ⑩，2026-08-12 蓝队整理新增）：
- shell 脚本（.sh）→ `100755`（可执行）
- 解释器调用类（.py 用 `python3 x.py` 调用、.ps1 用 `powershell -File` 调用）→ `100644`
- 文件模式一致性由 `git ls-files -s` 校验（CI compliance 阶段人工核对项；异常模式会被 pre-commit 的 check 类钩子捕获）

## 五、归档纪律（方案 ④⑥，2026-08-12 蓝队整理新增）

1. **归档必须登记**：任何文件/目录移入 `docs/历史文件/`，须在 `docs/历史文件/README.md`（归档索引）登记一行：`日期 | 归档对象 | 原因 | 负责人`。
2. **归档须附摘要**：目录类归档（如旧版流程整套）压缩为一份摘要文档，原文件可删除；单文件归档直接保留。
3. **季度清理检查**：每季度（收束节点时）检查归档索引，超过 1 年无引用的归档对象由 Owner 拍板是否删除；AI 负责在收束报告提示，不替人删除。
4. **产出登记强制**：HTML/报告等产出物验收后必须登记对应索引（docs/reports/INDEX.md 等），未登记视为未完成（对应方案 ⑤）。
5. **堆积收敛**：worklogs 按年归档（`worklogs/archive/YYYY/`）；reports 按版本收敛合并；research 完工后封存（对应方案 ⑪）。

## 六、入口扩展规则（方案 ⑦，2026-08-12 蓝队整理新增）

- 项目级入口目录（根目录 + `AGENTS.md` / `CLAUDE.md` / `.codex/` / `.agents/`）**允许按工具扩展**：新增 AI 工具接入时，在根目录并列放置其入口文件（如 `GEMINI.md`），并在 CLAUDE.md「跨 Harness」小节登记一行。
- 规则：入口文件只做**路由**（指向规范/流程），不复制规范内容；新入口须同步 `conventions/_meta.yaml` 的 `l3_route` 路由表。
- 设计意图：双入口 → N 入口的扩展位已预留，避免每次新工具接入都要改目录结构。
