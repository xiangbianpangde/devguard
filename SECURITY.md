## 分级标签

> 本节为**渲染产物**（由 render_meta.py 从 _meta.yaml 自动生成）。
> 修改流程：改 `conventions/_meta.yaml` → 跑 `render_meta.py --render convention-grade`。
> **不要手改本节**（手改会被 `render_meta.py --check` 检测到，CI fail）。

| 级别 | 数量 |
|------|------|
| 红线 | 0 |
| 警告 | 0 |
| 推荐 | 0 |

**L1 检测**：SECURITY.md 存在（V1.1.2 章节级 L1）
**L3 路由**：任务类型=安全报告 → 必读本篇

---
# Security Policy

> V1.1.2 新建
> 维护者: 袁 (xiangbianpangde) | 创建: 2026-06-07
> 更新: 2026-08-13

## Supported Versions

devguard 项目本身（开发规范模板）不发布生产版本——它是一套规范 + 模板。下表列出版本状态：

| Version | Supported          |
| ------- | ------------------ |
| V1.0+   | :white_check_mark: |
| V0.x    | :x: 已归档        |

## 平台层防护验证清单（2026-08-13 红队 N-2 落地）

仓库内闸门（19 钩子 + CI）之外，以下防护属于 **GitHub 设置层**——仓库内无法机器验证，须由维护者配置并定期人工核对。模式对齐微软 Agent Governance Toolkit：「CI 为真闸门 + push protection 带 bypass 豁免审计」，与 `meta/豁免清单.md` 审计账天然对齐。

| # | 防护项 | 期望状态 | 验证方式 | 与仓库机制的关系 |
|---|--------|---------|---------|-----------------|
| 1 | Branch protection（master） | 待 Owner 核对：禁直推 + required checks（红队 API 实测恰 5 个 required contexts，跨平台 job 未直接列入——与本文档 #2 声明有差异，须以平台实际为准） | GitHub Settings → Branches | 本地 `--no-verify` 绕过的兜底真闸门 |
| 2 | Required status checks | lint/test/l4/compliance/build + 跨平台 | PR checks 列表 | CI 5 阶段 + test-cross-platform |
| 3 | Secret scanning push protection | **未验证**（无 token 不可 API 查询；请勿视为已启用——待 Owner 携 admin token 核对） | Settings → Code security | 与 gitleaks（本地+CI）双链路；push 被拦时走 bypass 豁免审计对齐豁免账 |
| 4 | Dependabot alerts | **未验证**（待 Owner 核对） | Settings → Code security | 依赖漏洞（pip/npm audit 的远端兜底） |
| 5 | 默认分支合并方式 | PR 合并（禁 rebase-force） | Settings → Branches | 03-git 规范 main 禁直推 |

**核对频率**：每次收束节点核对一次；变更记录入 worklog。

## Reporting a Vulnerability

**请勿在 GitHub Issues 公开报告安全漏洞**——改为：

1. **私下联系 owner**：@xiangbianpangde（GitHub 私信）
2. **标题前缀**：`[SECURITY]` 便于识别
3. **包含内容**：
   - 漏洞位置（文件路径 + 行号）
   - 复现步骤
   - 影响范围（哪些版本/规范）
   - 修复建议（可选）

**响应 SLA**：
- 24 小时内：确认收到
- 7 天内：评估 + 给出修复计划
- 30 天内：发布修复（critical 优先）

## Security Practices

devguard 自身的安全实践：

- **gitleaks 手动跑**（V3.3）—— 阻止密钥入库
- **gitleaks allowlist**（.gitleaks.toml）—— 教学反例文件豁免
- **dashboard.html CSP**（V5.4）—— `<meta http-equiv="Content-Security-Policy">` 防 XSS
- **commit-msg-worklog-ref**（V0.1）—— 强制 worklog 引用
- **CODEOWNERS**（V1.1）—— GitHub 自动审查分配
- **.markdownlint.json 严格模式**（V3.1）—— Markdown 格式统一

## Out of Scope

- devguard 项目本身无对外 API/服务——所有"漏洞"是规范执行问题
- 报告 V0.x 旧版本问题不修——升级到 V1.0+
- 报告第三方工具（ruff/gitleaks/markdownlint 等）漏洞——找上游

## pre-commit 仓库 tag 钉版的风险决策（2026-08-13 红队 R2-06 回应）

pre-commit 的三个上游仓库（pre-commit-hooks / ruff-pre-commit / gitleaks）rev 使用 release tag（如 `v0.15.20`）——tag 理论上可被上游移动。蓝队评估后的决策：**维持 tag 钉版 + 版本真源校验**，理由：① pre-commit 框架对 tag 有本地缓存（首次解析后固定，环境可复现）；② `check_consistency` 已对 ruff rev 与 toolchain 真源做一致性校验（tag 移动会破坏版本语义而非静默漂移）；③ 改 commit SHA 会破坏 `_meta.yaml` 的版本可读性与 render_meta 渲染链。风险登记入技术债，若红队有 tag 移动攻击的可执行复现，蓝队接受重开。
