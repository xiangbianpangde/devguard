# BDD 规格: Git 协作规范

> 对应 `03-Git协作规范.md`

---

## 功能：Git 协作规范文档

### 场景 1：分支策略适配团队规模
- 前置条件：新项目启动，需要选择分支策略
- 操作步骤：
  1. 阅读"分支策略"章节
  2. 根据团队规模选择对应模型
- 预期结果：
  - 提供 Git Flow / GitHub Flow / Trunk-Based 三种选项
  - 每种选项标注适用团队规模
  - 有分支命名规范和示例

### 场景 2：提交信息格式统一
- 前置条件：开发者准备 commit
- 操作步骤：
  1. 阅读"提交规范"章节
  2. 按 Conventional Commits 格式编写 commit message
- 预期结果：
  - 明确 type 字段的 8 种取值（feat/fix/refactor/docs/style/test/chore/perf）
  - 有正确示例和错误示例
  - 规定提交粒度（一次 commit 只做一件事）

### 场景 3：Code Review 流程清晰
- 前置条件：PR 提交后
- 操作步骤：
  1. 阅读"Code Review"章节
  2. 按流程执行 Review
- 预期结果：
  - 有 Review 检查清单
  - 明确 Review 时限（<24h）
  - 明确 Approve 标准（至少 1 人）
