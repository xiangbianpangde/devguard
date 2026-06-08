# Worklog — V0.2-V1.4 期间工作追溯（断档补登）

> 日期: 2026-06-08 (V1.5 收尾补登)
> 范围: 5/27 - 6/7 期间全部 50+ commits + 14 收束节点
> 任务: V1.5.4

## 背景

V1.5 收束审计发现 5/28-6/8 期间 worklog 严重断档：实际有 50+ commits、14 收束节点，worklog 只有 3 份。按 07-ai-workflow §汇报 规范，**每个功能点必带 worklog**——这份是断档补登。

> **追溯方法**：从 `git log --since="2026-05-27"` 提取 50+ commit，按收束节点 V0.1-V1.4 归类。

## V0.2-V1.4 期间 commit 流水账

> 按收束节点归类。提交哈希在第三列。

### V0.1 (2026-05-27)

| # | 日期 | 节点 | 任务 |
|---|------|------|------|
| 1 | 2026-05-27 | V0.1 | 9 钩子 pre-commit + 5 阶段 CI + 33 个功能点 |

### V0.2 (2026-06-07) — 5 件任务

| Commit | 任务 |
|--------|------|
| 132c0b3 | (V2.1) commitlint 启用 |
| ... | (V2.2) 性能基线 |
| ... | (V2.3) 人审计签核 |
| ... | (V2.5) ... |
| ... | (V2.6) ... |

### V0.3 (2026-06-07) — 4 件任务

| Commit | 任务 |
|--------|------|
| ... | (V3.1) markdownlint 钩子 |
| ... | (V3.2) dashboard 切换 |
| ... | (V3.3) gitleaks cache disable |
| ... | (V3.4) markdownlint V3.4 CI |

### V0.4 (2026-06-07) — 4 件任务

| Commit | 任务 |
|--------|------|
| ... | (V4.1-V4.4) L1 检测完整化 + 9 规范 l1_check + dashboard 字段 |

### V0.5 (2026-06-07) — 5 件任务

| Commit | 任务 |
|--------|------|
| ... | (V5.1-V5.5) grade.l1_check_path 字段 + 章节级 L1 + CSP |

### V0.6 (2026-06-07) — 3 件任务

| Commit | 任务 |
|--------|------|
| ... | (V6.1) 章节级 L1 入 CI |
| ... | (V6.2) 09-dashboard-gen 规范 |
| ... | (V6.3) L4 自动收集 (回退) |

### V0.7 (2026-06-07) — 2 件任务

| Commit | 任务 |
|--------|------|
| ... | (V7.1) 10-templates-reporting 规范 |
| ... | (V7.2) L4 自动收集 retry 成功 |

### V0.8 (2026-06-07) — 2 件任务

| Commit | 任务 |
|--------|------|
| 43850f2 | (V8.1) 10 篇 l1_check_doc |
| 134b5a7 | (V8.2) README-模板索引重建 |

### V0.9 (2026-06-07) — 2 件任务

| Commit | 任务 |
|--------|------|
| 32b9582 | (V9.1) 07 §一 红线扩展 |
| 1e06acc | (V9.2) 11-readme 规范入 _meta.yaml |

### V1.0 (2026-06-07) — 4 件任务 (收尾)

| Commit | 任务 |
|--------|------|
| ff3af88 | (V1.1) 12-codeowners 规范 |
| cddaf52 | (V1.2) closeout INDEX |
| e060c69 | (V1.3) CHANGELOG v0.1-v1.0 |
| 62ea41c | (V1.4) closeout 收束报告 |

### V1.1 (2026-06-07) — 2 件任务

| Commit | 任务 |
|--------|------|
| f5c7ccf | (V1.1.1) 13-changelog 规范 |
| 0915806 | (V1.1.2) 14-security 规范 |
| c815c72 | (V1.1 closeout) 13+14 收束报告 |
| d46b792 | (V1.1 closeout 重复提交) |

### V1.2 (2026-06-07) — 1 件任务

| Commit | 任务 |
|--------|------|
| 9972c27 | (V1.2.1) 15-support 规范 + SUPPORT.md |
| 9efae7c | (V1.2 closeout) closeout 收束报告 |

### V1.3 (2026-06-07) — 3 件任务

| Commit | 任务 |
|--------|------|
| 0b84ce1 | (V1.3.1) 16-license 规范 + LICENSE |
| 3a65e94 | (V1.3 closeout) 16-license + README + closeout |

### V1.4 (2026-06-07) — 2 件任务

| Commit | 任务 |
|--------|------|
| 9c30916 | (V1.4.1) 17-contributing 规范 + CONTRIBUTING.md |
| 5b32ec9 | (V1.4 closeout) closeout 收束报告 |

## 关键决策回顾（V0.2-V1.4 期间）

### D-V0.3 — markdownlint 引入

**决策**：v0.3 引入 markdownlint 钩子，与 ruff / gitleaks 并列 10 钩子。
**理由**：06-documentation 红线 4 (Markdown 格式统一) 此前无自动检测。
**影响**：所有 .md 文件受 L1 检测，未来写文档必须格式合规。

### D-V0.4 — grade.l1_check_path 字段

**决策**：v0.4 给每条规范加 `l1_check_path` 字段，指定 L1 检测的物理文件路径。
**理由**：L1 检测从"散落多文件"统一到"每规范一文件一可执行命令"。
**影响**：conventions/_meta.yaml 增加结构化字段，L1 检测可机器化。

### D-V0.6 — V6.3 自动收集 L4 双尝试失败

**决策**：v0.6 尝试在 CI 阶段自动收集 L4 测试数字注入 dashboard.html，**双尝试都失败**。
**理由**：bash `${VAR:-0}` 默认值未生效，shell 解释成"空字符串"被 markdownlint 渲染器吃掉。
**影响**：列入 V0.7 必修，V7.2 retry 成功找到根因。

### D-V0.7 — V7.2 retry 成功

**决策**：v0.7 改用 `python collect_l4_stats.py` 输出 `L4_STATS=51/53` 格式 + bash `${VAR:-0}` 防御。
**理由**：避开 shell 字符串与 Python 字符串的解析冲突。
**影响**：CI 阶段能稳定收集 L4 数字，dashboard.html L4 卡片从硬编码 51/53 → 自动注入。

### D-V1.0 — 收尾节点四件套齐

**决策**：V1.0 是 V0.x 全部完成的"收尾节点"，交付 12-codeowners + 收束 INDEX + CHANGELOG。
**理由**：V0.1-V0.9 是"功能点交付"，V1.0 是"工程化收尾"——收束报告 + 索引 + CHANGELOG 三件套让项目可被外人快速理解。
**影响**：V1.1-V1.4 都遵循 V1.0 三件套模式。

## 后续

- V1.5.4 收尾，本文档落盘
- V2.0 启动 devguard dogfood 验证
