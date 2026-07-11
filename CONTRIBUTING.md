## 分级标签

> 本节为**渲染产物**（由 render_meta.py 从 _meta.yaml 自动生成）。
> 修改流程：改 `conventions/_meta.yaml` → 跑 `render_meta.py --render convention-grade`。
> **不要手改本节**（手改会被 `render_meta.py --check` 检测到，CI fail）。

| 级别 | 数量 |
|------|------|
| 红线 | 0 |
| 警告 | 0 |
| 推荐 | 0 |

**L1 检测**：CONTRIBUTING.md 存在（V1.4 章节级 L1）
**L3 路由**：任务类型=开源贡献 → 必读本篇

---
# Contributing to devguard

> V1.4 新建
> 维护者: 袁 (xiangbianpangde) | 创建: 2026-06-07
> 更新: 2026-07-11

devguard 是一套**开发规范模板**——欢迎任何人在此基础上扩展/改进规范或脚本。

## 行为准则

本项目采用 [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/)。参与即代表你接受该准则。

## 我能贡献什么

| 类型 | 范围 | 难度 |
|------|------|------|
| 规范错误 | 8 篇规范（01-08）内容/L1 检测有误 | 中 |
| 模板改进 | docs/templates/devguard/ 任何模板 | 易 |
| Bug 修复 | scripts/ 任何脚本 | 中 |
| 新规范 | 16 规范之外的（如 CONTRIBUTING）入 _meta.yaml | 中 |
| 文档改进 | CHANGELOG / README / 收束报告 | 易 |
| 示例代码 | src/ 任一维度的 Python 示例 | 中 |

## 提 PR 流程

1. **Fork** 本仓库
2. **新建分支**：`git checkout -b feat/your-feature-name`
3. **写代码**：遵循 `conventions/` 8 篇规范
4. **写测试**：在 `tests/conventions/` 加 L4 套件测试
5. **跑 L4**：`python -m pytest tests/conventions/ -v`
6. **commit**：遵循 commitlint（`feat` / `fix` / `refactor` / `docs` / `test` / `chore`）
7. **push**：`git push origin feat/your-feature-name`
8. **开 PR**：标题 + 描述 + 关联 Issue

## 报告 Issue

提 Issue 时附：

1. **devguard 版本**（CHANGELOG.md 找）
2. **问题描述**（期望 vs 实际）
3. **复现步骤**（具体命令 + 输出）
4. **环境**（OS / PowerShell 版本 / Python 版本）

## 开发流程

devguard 自身遵循 `conventions/ai-workflow_AI协作开发流程/` 9 篇流程文档：

```
双轨制（长程/思考）+ 端到端 7 阶段（每功能点循环）
                              │
                         扫描→实现→可观测→审查→人确认→更新记录→commit
                              │
                         收束节点（人触发）
```

详见 `docs/reports/INDEX.md` 看历史收束报告。

## 编码规范

PR 必须遵循 `conventions/02-coding.md` + `conventions/05-testing.md`：

- 测试独立（不依赖全局状态）
- 只 Mock 外部边界（不 Mock 内部函数）
- 覆盖正常 + 边界 + 异常 3 类
- SQL 参数化（不留 SQL 注入）
- 密钥走环境变量（不硬编码）
- 禁 print（用 logging）
- 禁静默吞异常
- 日志脱敏

## Commit 格式

```
<type>(<scope>): <subject>

<body>

<footer>
```

**type**：feat / fix / refactor / docs / test / style / chore / perf

**scope**（可选）：conventions / scripts / tests / docs / ci / templates

**subject**：中文/英文均可，≤ 72 字符，不大写结尾，不加句号

**body**：为什么改 + 怎么改，每行 ≤ 72 字符

**footer**：关联 Issue + Breaking Change

## 许可

贡献即代表同意按 [MIT License](./LICENSE) 发布你的贡献。
