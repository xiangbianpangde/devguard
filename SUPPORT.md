# Support

> V1.2 新建
> 维护者: 袁 (xiangbianpangde) | 创建: 2026-06-07

## 项目性质

devguard 是**开发规范模板**——不是产品。所以"支持"指：

- **规范问题**：8 规范内容/L1 检测有疑问
- **模板使用**：复制 docs/templates/devguard/ 到新项目后怎么用
- **Bug 反馈**：CI 脚本/check_* 脚本有 bug

## 获取帮助

| 渠道 | 场景 | 响应时间 |
|------|------|----------|
| GitHub Issues | 规范/模板/Bug | 7 天内 |
| GitHub Discussions | 一般问题讨论 | 不保证 |
| 私信 @xiangbianpangde | 安全问题（私密） | 24 小时内 |

## 报告 Bug

提交 Issue 时附：

1. **devguard 版本**（V0.x / V1.0 / V1.1 / V1.2 等）
2. **问题描述**（期望 vs 实际）
3. **复现步骤**（具体命令 + 输出）
4. **环境**（Windows/PowerShell 5.1 vs Linux/bash；Python 版本）

## FAQ

**Q: devguard 可以商用吗？**
A: 可以——本项目 MIT License，复制修改随便用。

**Q: 我想用部分规范 + 部分新规范，怎么混？**
A: 直接修改 _meta.yaml——只保留你需要的规范 l1_check + 删除其他。

**Q: 怎么从 V0.x 升级到 V1.0？**
A: 看 CHANGELOG.md——V1.0 改的 9 hooks + 5 阶段 CI + 12 规范 + 65 L4 tests。

**Q: 哪里找最新版本？**
A: 看 docs/reports/INDEX.md + CHANGELOG.md。

## Out of Scope

- **非 devguard 项目的问题**——devguard 不替其他项目 debug
- **教学**——devguard 假定用户已会基础开发流程
- **生产环境部署**——devguard 是规范模板，不是部署工具
