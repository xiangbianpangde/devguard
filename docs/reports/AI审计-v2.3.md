# AI 审计报告 — 收束节点 v2.3

> 更新: 2026-08-13
> 审计时间: 2026-08-13 | 审计范围: 红蓝对抗整理周期（大类一~六 + 21 项对抗修复）+ #53/#55 交付物
> 审计方式: 模式化扫描（红线/中风险/低风险）+ check_* 全家桶 + 对抗变异验证（ADR 0009）
> 扫描文件: 476 个 tracked（34 个治理脚本）

## 红线违规（🔴 必须修）

**无。** 扫描结论：

| 检查项 | 结果 |
|--------|------|
| 调试 print | 0（治理脚本 CLI 输出合法） |
| TODO/FIXME/XXX | 0 |
| 硬编码密钥 | 0（gitleaks 208 规则 + 故障注入 11/11 拦截） |
| 裸 except | 0（全部带异常类型） |
| SQL 拼接 | 0（无 SQL） |
| 密钥进版本库 | 0（gitleaks pre-commit + CI 双链路） |

## 中风险（🟡 建议修）

| # | 位置 | 事项 | 依据 | 建议 |
|---|------|------|------|------|
| 1 | meta/豁免清单.md | append-only 已由 set 差集校验，但无行级哈希（可构造同长度行替换） | C6 | 列入技术债 #8 一并处理 |
| 2 | scripts/check_enforcement.py | gitleaks 注入依赖本机二进制探测（无二进制时 MISSED 但不 fail） | S3 | 环境缺二进制时降级为警告并注明（CI 恒有）——现状可接受，列入观察 |

## 低风险（🟢 知晓即可）

| # | 位置 | 事项 |
|---|------|------|
| 1 | worklogs/ | 70+ 份日志当年保留（FILE_GRAPH §五.5 原路径不动规则），归档动作当年无需执行 |
| 2 | docs/reports/ | 07-21 HTML demo 2 份价值待 Owner 拍板去留 |
| 3 | .pre-commit-config.yaml | 钩子注册三处同步（_meta/配置/ci.yml）靠纪律——技术债 #8 待立项 |

## 对抗变异验证（ADR 0009 首次执行）

| 闸门 | 变异方向 | 预期 | 实测 |
|------|---------|------|------|
| check_consistency | _meta ruff→9.9.9 | rc=1 | ✅ rc=1 硬失败 |
| check_consistency | _meta pytest→9.9.9 | rc=1 | ✅ rc=1 硬失败 |
| check_consistency | _meta pre-commit→9.9.9 | rc=1 | ✅ rc=1 硬失败 |
| check_template_drift | scaffold rev→v8.99.9 | FAIL | ✅ FAIL |
| check_coverage_matrix | 矩阵 01→16 变异 | FAIL | ✅ FAIL |
| gitleaks | 高熵 PAT 注入 | rc=1 | ✅ rc=1（×3 稳定） |

## 审计结论

机器审计 **0 红线**；中风险 2 项（豁免哈希、注入环境降级）列入技术债/观察；对抗变异 6 项全通过。本报告只标记疑点，最终判定与人审计由 Owner 执行。
