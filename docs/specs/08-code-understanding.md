# BDD 规格: 代码理解与图谱规范

> 对应 `08-code-understanding_代码理解与图谱规范.md`（v3.0：双图谱——CodeGraph 给 AI + Understand-Anything 给人）

---

## 功能：代码理解与图谱规范文档

### 场景 1：声明两种图谱的定位与启用门槛
- 前置条件：无
- 操作步骤：
  1. 打开 `08-code-understanding_代码理解与图谱规范.md`
  2. 阅读引言 + 启用门槛
- 预期结果：
  - 明确声明"不是一套图谱，是两套"：AI vs 人
  - 对比表含「怎么读 / 粒度 / 更新频率 / 交互方式 / 核心指标」五行
  - 启用门槛分两条线：CodeGraph 的触发条件（>10 模块 / >5 万行）和 Understand-Anything 的触发条件（只要有代码）
  - 不出现图数据库（Neo4j/KuzuDB）选型表或 Cypher 查询示例

### 场景 2：AI 图谱 — CodeGraph 完整可执行
- 前置条件：读者是 AI 助手的使用者
- 操作步骤：
  1. 阅读 §一 AI 图谱
- 预期结果：
  - 含原理流程图（tree-sitter → SQLite+FTS5 → MCP Server）
  - 含 7 个 MCP 工具速查表（工具名 + 用途 + 何时用）
  - 含 benchmark 数据表（7 个代码库，token 节省 / tool call 减少）
  - 含部署命令（curl / npm 一键安装 + `codegraph init -i`）
  - 含"为什么是 SQLite 不是图数据库"的对比说明

### 场景 3：人的图谱 — Understand-Anything 完整可执行
- 前置条件：读者是团队成员或新人
- 操作步骤：
  1. 阅读 §二 人的图谱
- 预期结果：
  - 含原理说明（tree-sitter 确定性 + LLM 语义 → JSON → Dashboard）
  - 含多 Agent 流水线表（6 个 Agent + 职责）
  - 含功能速查表（结构图/域视图/导览/搜索/差异影响/分层着色/语言概念）
  - 含团队共享说明（JSON 入 Git + `--auto-update`）
  - 含"为什么是 Dashboard 不是手写 Mermaid"的对比说明
  - 含部署命令（插件安装 + `/understand` + `/understand-dashboard`）

### 场景 4：两种图谱的协同
- 前置条件：读者同时考虑引入两个工具
- 操作步骤：
  1. 阅读 §三 协同
- 预期结果：
  - 含分工对照图（ASCII 流程图：代码库 → CodeGraph / Understand-Anything → 各自的消费者）
  - 明确"AI 不打 Dashboard，人不写 Cypher"
  - 含轻量项目退路（CALL_GRAPH.md + @entrypoint/@callers/@calls 标注）
  - 退路标注为"一旦规模增长立即切换到工具"

### 场景 5：检查清单可操作
- 前置条件：图谱实施中
- 操作步骤：
  1. 逐项核对 §四 检查清单
- 预期结果：
  - 分三组：CodeGraph（7 项） / Understand-Anything（7 项） / 协同（3 项）
  - 首项分别为规模门槛判断
  - 不少于 15 项

### 场景 6：不包含已删除的内容
- 前置条件：读者从旧版规范迁移而来
- 操作步骤：
  1. 阅读全文
- 预期结果：
  - 不出现 Cypher 查询语句（MATCH ... RETURN）作为推荐使用方式
  - 不出现存储选型表（SQLite+KuzuDB+Neo4j 三档）
  - 不出现 CODE_MAP.md 的手写要求（Mermaid 全景图 + 关键入口表 + 手写维护流程）
  - 不出现"增量优于全量 / 全量重建兜底"等构建策略（工具内置）
  - 不出现"12 种关系类型"的枚举表格（工具内部处理）

### 场景 7：交叉引用指向一致
- 前置条件：从 01/02/05/06 规范跳转而来
- 操作步骤：
  1. 检查 §五 关联表
- 预期结果：
  - 含 01-架构 / 02-代码 / 05-测试 / 06-文档 / ai-workflow 的链接
  - 含调研数据来源链接
  - 含两个工具的 GitHub 链接
  - 更新记录含 v3.0 行，说明范式重构
