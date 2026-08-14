# 设计提案：S-1 临时目录构建 + 原子 rename（setup_scaffold 结构性加固）

> 更新: 2026-08-14 | 状态: ✅ 已实现（993f450 入库，红队矩阵 7 项验收 + 窄修闭环）
> 来源: 红队外源情报 S-1（cookiecutter/scbake 模式）；红队 5 点技术反馈（2026-08-14 收）

## 背景

setup_scaffold 当前直接写入 target + 失败时 `_rollback_writes`（回滚清单）。三轮对抗中"回滚清单漏项"类缺陷反复出现（receipt 漏回滚、venv/git 残留、final verify 未包回滚）——回滚清单是**人肉维护的漏项源**。S-1 从结构上消灭该类：**先构建、后可见**。

## 方案（锚定红队 a-e）

### a. 事务边界
- 空 target：`target 同级/.devguard-staging-<rand>` 完整构建（payload 全部写入 staging）→ 校验通过 → `os.replace(staging, target)` 一次原子提交
- 同文件系统保证：staging 与 target 同级（同一父目录）→ os.replace 跨设备失败不可能
- 非空 target（--force）：保留现有回滚清单路径（owner 既有文件覆盖场景），staging 仅用于空 target

### b. 性能
- `.git` / `.venv` **不进 staging**：rename 成功后原地生成（git init + venv 创建放 rename 之后）
- payload 小文件（23 个 manifest 文件）走 staging——复制成本可忽略

### c. owner 保护（2026-08-14 实现澄清，消除 a/c 矛盾）
- 空 target：payload 全在 staging，任何失败 = 删 staging 归零（**结构性消灭回滚清单**）——已实现
- --force（非空 target）：**不走 staging**（与 a 点一致）——逐文件原子替换 + 回滚清单（previous 备份恢复 owner 文件）——已实现
- 注：c 点旧稿「--force 亦走 staging + rename 前备份」与实际实现不符（rename 无法原子替换非空目录）；已按实现澄清

### d. 失败注入验收（红队将以失败注入攻击验收）
- test_scaffold 新增：ensurepip 预检失败 / staging 写入中途失败 / 校验失败 → target 零残留 + staging 被清理
- 全链路：--install 模式下 rename 后 venv 失败 → target 回滚为"未初始化"状态

### e. Windows 真机验证（R-08 教训：勿只静态论证）
- `os.replace` 在 Windows 对**存在的目标**抛 PermissionError（目标非空目录）——空 target 场景目标不存在 ✓ 原子；但需 pwsh/Windows runner 真机验证空 target 场景
- 验收：GitHub Actions windows-latest 跑 setup_scaffold E2E（test-cross-platform job 已覆盖 test_scaffold）

## 影响范围

scripts/setup_scaffold.py（setup() 主流程）、tests/conventions/test_scaffold.py、scripts/selfcheck.sh（--full 路径不变）

## 验收条件

1. 空 target 全链路（--install）：staging 构建 → rename → venv/hooks 原地生成 → verify 通过
2. 失败注入矩阵（红队执行）：ensurepip/写入/校验/venv/pip/钩子各点注入 → **target 零残留**（空 target 场景）
3. 现有 211 测试全绿 + 新增 staging 测试
4. Windows runner 真机 E2E 通过

## 降级方案（已基本就绪）

「回滚清单由 manifest 自动推导」：written = payloads.keys()（含 receipt，R-03 已实现）——成本约 S-1 全量的 1/10。若 S-1 全量重构风险过高，可先文档化降级方案为已满足态。

## Owner 决策

- [x] 2026-08-14：S-1 全量 staging 重构已实现（签认挂账至收束人审计清单：决策由蓝队依红队建议执行，复核挂账——R5-33/34 追溯）
