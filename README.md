# {项目名} — 使用指南

> 约 2 分钟读完。本文件夹是通用开发规范的**项目模板**。

---

## 这是什么

一套适用于各类软件项目的通用开发规范 + AI 协作开发流程。克隆/复制本文件夹到你的项目根目录，即可获得：

- `conventions/` — 6 份开发规范 + AI 协作流程，开箱即用
- `docs/templates/` — 所有文件类型的模板（worklog/CLAUDE/STATUS/BDD/...）
- `plan/` — 计划骨架（背景 + 开发清单）
- `STATUS.md` — 项目进度仪表盘
- `dashboard.html` — 可视化进度面板（浏览器打开，60s 自动刷新）
- `CLAUDE.md` — Claude 新会话自动加载的项目上下文

---

## 快速开始（新项目）

### 第一步：复制模板

```bash
# 克隆或复制整个开发规范文件夹到新项目
cp -r 开发规范/ my-new-project/

# 或只复制需要的部分
cp -r 开发规范/conventions/ my-new-project/
cp 开发规范/CLAUDE.md 开发规范/STATUS.md 开发规范/dashboard.html my-new-project/
cp -r 开发规范/docs/templates/ 开发规范/plan/ 开发规范/worklogs/ my-new-project/
```

### 第二步：初始化为你的项目

1. **改项目名**：修改 `CLAUDE.md` 第一行的 `{项目名}`
2. **写背景**：填充 `plan/背景.md`（为什么做、设计决策）
3. **定功能点**：在 `plan/开发清单.md` 中列出你的功能点
4. **选规范**：阅读 `conventions/README.md` 快速索引，确认哪些规范适用
5. **初始化状态**：运行 `git init`，更新 `STATUS.md`

### 第三步：按 AI 协作开发流程推进

阅读 `conventions/07-ai-workflow_AI协作开发流程/` 了解完整流程：
0. 调研 → 1. 计划 → 2. 迭代开发

---

## 文件定制指南

### 必须修改的文件

| 文件 | 修改内容 |
|------|---------|
| `CLAUDE.md` | 项目名、目录结构、模块图谱、关键决策 |
| `plan/背景.md` | 项目背景、设计决策 |
| `plan/开发清单.md` | 功能点列表、BDD 引用、依赖关系 |
| `STATUS.md` | 功能点状态、完成日期 |

### 可选修改的文件

| 文件 | 说明 |
|------|------|
| `conventions/*.md` | 规范内容可根据项目调整（增删规则、修改红线） |
| `dashboard.html` | 颜色/刷新间隔可改 `<meta http-equiv="refresh">` |
| `docs/templates/*` | 模板内容保持通用，需要时修改 |

### 无需修改的文件

- `dashboard.html` 的核心结构（自动解析 STATUS.md）
- `worklogs/` 目录结构（按日期自动生成）

---

## 目录结构

```
my-project/
├── conventions/              # 开发规范（本模板核心）
│   ├── README.md             # 快速索引入口
│   ├── 01-architecture_*.md  # 架构设计规范
│   ├── 02-coding_*.md        # 代码编写规范
│   ├── 03-git_*.md           # Git 协作规范
│   ├── 04-api_*.md           # API 设计规范
│   ├── 05-testing_*.md       # 测试规范
│   ├── 06-documentation_*.md # 文档规范
│   └── 07-ai-workflow_*/     # AI 协作开发流程
├── docs/
│   ├── templates/            # 文件模板
│   ├── research/             # 调研文档（待填充）
│   ├── specs/                # BDD 功能规格（待填充）
│   └── decisions/            # 架构决策记录（待填充）
├── plan/                     # 计划文件
│   ├── 背景.md               # 项目背景
│   └── 开发清单.md            # 功能点列表
├── worklogs/                 # 工作日志
├── src/                      # 源代码
├── STATUS.md                 # 项目状态追踪
├── dashboard.html            # 可视化仪表盘
├── CLAUDE.md                 # Claude 项目上下文
└── README.md                 # 本文件
```

---

## 常见问题

**Q: 规范太严格，能删减吗？**
A: 可以。`conventions/` 中的每条规则都可以调整。建议先完整阅读一遍，标出不适用的规则，然后在团队内讨论确认。

**Q: dashboard.html 打开是白的？**
A: 需要通过 HTTP 服务打开（`python -m http.server` 或 VS Code Live Preview），不能直接用 `file://` 协议。

**Q: 只有我一个人开发，也需要这些吗？**
A: 是的。`CLAUDE.md` 和 `STATUS.md` 让你在不同会话、不同 AI 工具中保持一致性。明天的你不会记得今天为什么做这个决策。

**Q: 怎么更新规范？**
A: 直接修改 `conventions/` 下的对应文件，提交 commit。如果是重大变更，写一份 ADR 到 `docs/decisions/`。
