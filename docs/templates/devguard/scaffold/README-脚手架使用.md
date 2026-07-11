# 基准约束脚手架 — ECC 对标的一键初始化 2.0

> 复制器：`scripts/setup_scaffold.py`（在本仓运行，把基线写入新项目目录）。
> 区分 **core**（可独立运行）与 **optional**（团队所有权/决策目录）。
> 更新: 2026-07-11

## 一条命令

```powershell
py -3.11 .\scripts\setup_scaffold.py 'C:\dev\my-project' --profile core --project-name 'My Project' --install
```

写入前预演：

```powershell
py -3.11 .\scripts\setup_scaffold.py 'C:\dev\my-project' --profile core --dry-run
```

安装后独立复验：

```powershell
py -3.11 .\scripts\setup_scaffold.py 'C:\dev\my-project' --verify --require-hooks
```

## 必带层（core）

| 类别 | 内容 |
|------|------|
| 跨 Harness | `AGENTS.md` + `CLAUDE.md` + canonical `.agents/skills/devguard/` |
| Codex 安全基线 | credential-free `.codex/config.toml`，multi-agent 默认关闭 |
| 规则真源 | `conventions/README.md`，skill/入口文件只引用不复制 |
| 本地强制 | pre-commit + commit-msg + gitleaks + ruff + fail-closed verify |
| CI | least-privilege GitHub Actions：verify + all hooks + governance tests |
| 可追溯 | `.devguard.json` + SHA-256 receipt + 独立验证器/测试 |

## 可选层（`--profile optional`）

| 类别 | 内容 | 依赖 |
|------|------|------|
| 团队所有权 | `.github/CODEOWNERS` | GitHub 团队协作 |
| 决策与报告目录 | `docs/decisions/`、`docs/reports/` | 需要长期治理记录的项目 |

## 注意

- 默认拒绝非空目录；`--force` 只在 Owner 明确确认后使用。
- 每个受管文件原子替换；写入、receipt 或最终 verify 任一步失败都会回滚。
- 外部 ECC/global hooks 会与项目 hooks 组合，不修改用户全局 Git 配置。
- 项目 `.codex/config.toml` 不预装 MCP 或凭据，用户全局配置保持原样。
