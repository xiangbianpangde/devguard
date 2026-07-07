


## 分级标签

> 本节为**渲染产物**（由 render_meta.py 从 _meta.yaml 自动生成）。
> 修改流程：改 `conventions/_meta.yaml` → 跑 `render_meta.py --render convention-grade`。
> **不要手改本节**（手改会被 `render_meta.py --check` 检测到，CI fail）。

| 级别 | 数量 |
|------|------|
| 红线 | 5 |
| 警告 | 0 |
| 推荐 | 0 |

**L1 检测**：markdownlint-cli + .markdownlint.json
**L3 路由**：任务类型=写文档 → 必读本篇

---
# 文档规范

> **本规范是 ai-workflow 中文档产出环节的细化**：
> - 细化 [第二步 §2.5 更新记录](ai-workflow_AI协作开发流程/04-长程开发.md)（worklog / STATUS / CLAUDE）与 [§2.8 + 07-汇报](ai-workflow_AI协作开发流程/08-汇报收束.md)。
> - 细化交付物文档（README / CHANGELOG / 设计文档）；并支撑[第三步·收束节点](ai-workflow_AI协作开发流程/08-汇报收束.md)的「文档一致性检查」。
>
> **模板权威在 [docs/templates/](../docs/templates/README-模板索引.md)**——本规范只定标准与红线，模板正文不在此重抄。
> **档位裁剪**：轻量（README + worklog）/ 标准（+ CHANGELOG + 设计文档）/ 团队（+ CONTRIBUTING + 代码地图）。

---

## 一、红线（必守）

| # | 红线 | 怎么验证 |
|---|------|---------|
| 1 | 项目根有 README，含「快速开始」（≤5 条命令跑起来） | 新人按 README 能独立启动 |
| 2 | 每次发布更新 CHANGELOG（Keep a Changelog 格式） | 发布检查 |
| 3 | 文档与代码在同一个 PR 中改（不脱节、不分离到 Wiki） | 审查 diff |
| 4 | 公共 API 有 docstring（参数/返回/异常/示例） | 审查 + 文档 lint |
| 5 | 注释与代码行为一致，过时注释立即删 | 审查 |

---

## 二、落地：模板复用 + 文档随码同步

所有文档从 [docs/templates/](../docs/templates/README-模板索引.md) 复制起步，不手搓：

| 要写的文档 | 用哪个模板 |
|-----------|-----------|
| 工作日志 | [worklog模板](../docs/templates/worklog模板.md) |
| 功能点 / 收束汇报 | [汇报模板](../docs/templates/汇报模板.md) |
| README / CHANGELOG / 设计文档 | 见模板索引 |

**docstring 范例（公共 API 必须）：**

```python
def create_order(user_id: str, product_id: str, quantity: int) -> Order:
    """创建订单。
    Args:    quantity: 购买数量，必须 > 0
    Returns: 订单对象，状态 pending
    Raises:  ValueError 库存不足 / UserNotFoundError / ProductNotFoundError
    """
```

**CHANGELOG 六分类**：Added / Changed / Fixed / Deprecated / Removed / Security——用**用户视角**写「这次更新对我有什么影响」，不是 git log 复制。

**中文批处理（Windows PowerShell 5.1 环境）**：批处理中文 markdown 字符串替换必须用 **Python 脚本 + `read_text(encoding='utf-8', errors='replace')`**，**不要在 PowerShell 5.1 里用 `[Console]::OutputEncoding`**——ANSI 编码会静默损坏 UTF-8 多字节字符。典型场景：项目大量文件改名、批量插入章节标题、跨文件字符串同步。

---

## 三、决策表 / 速查

### 何时写设计文档

| 写 | 不写 |
|----|------|
| 需求不清、需多方对齐 | 简单 CRUD |
| 复杂功能（≥3 模块） | 纯 UI 调整 |
| 重大架构变更 | 已有明确方案的小改 |

设计文档五段：背景 / 目标 / 方案（含 Mermaid 图）/ 影响范围 / 风险。放 `docs/plan/design/`。

### 文件命名

| 类型 | 格式 | 示例 |
|------|------|------|
| 普通文档 | kebab-case | `deployment-guide.md` |
| 日期相关 | `YYYY-MM-DD-描述` | `2026-05-26-会议纪要.md` |
| 工作日志 | `YYYY-MM-DD_描述.md` | `2026-05-26_功能A开发.md` |

> 禁空格 / 特殊字符，只允许字母数字 `-` `_` `.`。

### 知识互联（标准/团队档位）

| 规则 | 要点 |
|------|------|
| 文档间双向链接 | 设计文档 ↔ BDD ↔ 规范原文 互相引用 |
| 关键文档入 README 索引 | 超过 5 份文档时必须有分类索引 |

### 收束时的文档维护

| 规则 | 要点 |
|------|------|
| 收束节点检查文档一致性 | 逐份对照代码现状（[第三步](ai-workflow_AI协作开发流程/08-汇报收束.md)） |
| 过时文档移 `archive/`，标废弃日期 | `> ⚠️ 已废弃: YYYY-MM-DD，替代: xxx` |

### 配图规约（学术论文场景 — 触发时启用）

**触发场景**：做学术论文配图（CHI / FAccT / JAMIA / NeurIPS 等期刊/会议 figure）时。

**风格**：期刊式学术风格（与思维导图 / 流程图 / 系统架构图区分）。

**高信息密度原则**——每张图至少 2-3 个 SVG 视觉元素，不是单图标点缀。

| 反例（被否决）| 正例（通过）|
|----------|----------|
| "3 栏 + 每栏 6 字段 + 文字描述" 字典式布局——文字堆叠，无视觉锚点 | **Hero data-flow 图**：横向 swimlane 卡片 + 多色箭头 + 真实示例数据 |
| "4 架构对比表" 用 6×4 文字 cell——全部 dim/partial/full 文字，看不出差异 | **DB schema 框图**：3 table box + 列名 + PK 高亮 + 红色 trigger 印章 + syntax-highlighted SQL |
| 任何"大量小字段 + 大量描述文字"的设计 | **视觉对比矩阵**：4 架构 × 6 维度，单元格用 ✓ (绿) / ◐ (amber 半圆) / ✗ (灰)，ours 列 teal 背景高亮 |

**实现细节**：
- 用 SVG 内联画图（data flow 横向 swimlane 卡片、schema 表格、icon symbols），**不要用 chart 库**
- KaTeX 渲染数学符号但要节省：标题/公式用，字段描述用普通文字
- 字段类型用 monospace 简短标识（`text` / `int[]` / `jsonb` / `timestamptz`）一字符就够
- 配色：ours 列用 teal 背景高亮；✓ 绿 / ◐ amber / ✗ 灰 三色语义清晰

---

## 四、反模式（保留文档独有）

### ❌ README 有名无实
`# my-project / A cool project. / Usage: See code.` → 读者连项目做什么都不知道。
✅ 30 秒内回答 5 问：做什么 / 怎么跑 / 有什么功能 / 技术栈 / API 在哪。

### ❌ CHANGELOG 是 git log 复制
`- feat: add avatar / - chore: update deps / - refactor: clean up` → 用户不关心重构和依赖。
✅ 按 Added/Fixed/Security 写用户能感知的影响。

### ❌ 注释与代码不符
`"""通过用户名查询"""` 但实际查 `id` → 读者不知信注释还是信代码，比没注释更危险。
✅ 改代码同步改注释，参数名 / 字段名 / 行为描述三者一致。

---

## 五、检查清单

- [ ] 根目录有 README，含「快速开始」（拷贝即跑）
- [ ] CHANGELOG 按 Keep a Changelog 维护，发布即更新
- [ ] 公共 API 有完整 docstring
- [ ] 注释与代码行为一致，无过时注释
- [ ] 文件命名 kebab-case，无空格 / 特殊字符
- [ ] 复杂功能（≥3 模块）有五段设计文档
- [ ] 文档间双向链接（设计 ↔ BDD ↔ 规范）
- [ ] 过时文档已更新或归档
- [ ] 中大型项目有代码地图（见 08）

---

## 六、关联

| 方向 | 链接 |
|------|------|
| 细化自 | [§2.5 更新记录](ai-workflow_AI协作开发流程/04-长程开发.md) · [07-汇报](ai-workflow_AI协作开发流程/08-汇报收束.md) |
| 模板权威 | [docs/templates/](../docs/templates/README-模板索引.md) |
| 验收标准 | [docs/specs/06-documentation.md](../docs/specs/06-documentation.md) |
| 代码地图 CODE_MAP / 知识图谱 | [08-代码理解与图谱规范](08-code-understanding_代码理解与图谱规范.md) |
| 文档一致性检查时机 | [第三步·收束节点](ai-workflow_AI协作开发流程/08-汇报收束.md) |

---

## 更新记录

| 日期 | 版本 | 变更说明 |
|------|------|---------|
| 2026-05-27 | v2.0 | 重构为文档产出环节的细化；模板正文改为链接 docs/templates/；红线配验证；§2.9 代码地图移交 08 |
| 2026-05-27 | v1.1 | 新增 §2.8 知识互联 + §2.9 代码地图 |
| 2026-05-26 | v1.0 | 按统一模板改造 |
