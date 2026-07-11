# 设计提案：ECC 全项目对标与一键初始化 2.0

> 更新: 2026-07-11

## 背景

原 DevGuard 已能量化一致性与强制性，但对 ECC 的借鉴主要停留在 Git Hook 兼容。完整 ECC 还包含 skills-first、rules、跨 harness 配置、manifest/profile、安装预演、回滚、安全、CI 与覆盖测试等能力面。

## 目标

- ECC 十域对标得分不低于 80%，且由脚本和测试证明。
- 保持现有一致性不低于 80%、故障注入拦截率不低于 90%。
- 一条命令同时生成 Codex/Claude 可读基线；安装前可预演，中途失败可回滚。
- 不复制 ECC 的 67 agents、448 skill 文件或 94 commands；只吸收适用于“开发规范模板”的机制。

## ECC 十域映射

| ECC 能力面 | DevGuard 落地 | 强制证据 |
|------------|---------------|----------|
| skills-first | `.agents/skills/devguard/` 为 canonical workflow | `check_ecc_alignment.py` + scaffold E2E |
| rules | `conventions/README.md` 单一规则真源 | skill/AGENTS 仅路由，不复制规则 |
| agents/commands | 默认不生成子代理或 legacy commands | `.codex/config.toml` 中 multi_agent=false |
| hooks | 项目 Hook 与 ECC/global Hook 组合 | 真 Git E2E + `--require-hooks` |
| scripts/install | dry-run / install / verify | CLI E2E |
| manifest/profile | core/optional 显式条目 | 源文件、重复目标预检 |
| Codex/MCP | credential-free 项目配置；MCP 保留用户全局配置 | 无 `mcp_servers.*` 与凭据写入 |
| security | gitleaks + ruff + fail-closed verifier | pre-commit 与 CI |
| tests/CI | 治理单测、集成、仓外 E2E | pytest + least-privilege CI |
| rollback/provenance | 原子替换、事务回滚、SHA-256 回执 | 故障注入测试 + receipt verify |

## 方案

1. core manifest 新增 `AGENTS.md`、canonical skill、OpenAI 元数据和安全 Codex 配置。
2. `setup_scaffold.py` 先完整构建载荷，再逐文件原子替换；保存旧字节，任一步失败反向恢复。
3. 新增 `--dry-run`，只执行源文件、重复目标与模板变量预检并列出路径。
4. 新增 ECC 十域事实矩阵，并绑定本仓 pre-commit 与 CI。
5. gitleaks 进入生成项目的核心 pre-commit，不依赖用户全局 ECC 才具备密钥拦截。

## 影响范围

`scripts/`、`docs/templates/devguard/scaffold/`、`docs/specs/00`、`docs/specs/07`、CI、pre-commit、测试、README 与文件图谱。

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| `--force` 覆盖 Owner 文件 | 默认拒绝非空目录；显式 force 仍保留旧字节并回滚 |
| 项目 Codex 配置覆盖用户 MCP | 仅写目标项目新文件；配置无 MCP/凭据，非空目标仍需 force |
| skills 与 conventions 漂移 | skill 只引用规范真源，ECC 对标脚本检查路由关系 |
| “对标分数”沦为存在性计数 | 每域至少绑定内容契约、执行入口或故障注入测试 |

## Owner 决策

| 决策 | Owner 结论 | 状态 |
|------|------------|------|
| 对标范围 | 参考整个 ECC 项目，不只兼容 hooks | 已拍板 |
| 子代理 | 本轮不使用子代理；生成基线也默认 multi_agent=false | 已拍板 |
| 分支 | 拉取并合并其他分支，最终只保留一条分支 | 已拍板 |
| 外部动作 | 最终分支提交；远程删除仅在合并验证后执行 | 已拍板 |

当前无待拍板项。
