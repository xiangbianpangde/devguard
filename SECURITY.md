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
> 更新: 2026-07-11

## Supported Versions

devguard 项目本身（开发规范模板）不发布生产版本——它是一套规范 + 模板。下表列出版本状态：

| Version | Supported          |
| ------- | ------------------ |
| V1.0+   | :white_check_mark: |
| V0.x    | :x: 已归档        |

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
