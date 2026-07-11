# DevGuard 模板索引

> 更新: 2026-07-11

## 可部署入口（权威）

不要再把 `docs/templates/devguard/` 整目录复制到新项目。该目录还保存仪表盘、
最终报告和历史兼容素材，整目录复制不等于依赖闭包。

新项目只通过显式 manifest 初始化：

```powershell
py -3.11 scripts\setup_scaffold.py C:\path\to\new-project --profile core --project-name "My Project" --install
```

这一条命令会创建实例化后的 `README.md`、`STATUS.md`、`CLAUDE.md`、计划文档、
最小 CI、固定版本依赖与本地虚拟环境，并安装 `pre-commit` 和 `commit-msg` 两种
hook。初始化结束前会执行 fail-closed 自检；任一文件、依赖或 hook 缺失都会返回
非零退出码。

机器已有 ECC/其他全局 `core.hooksPath` 时，初始化器不会修改用户全局配置；它会
把现有 `pre-commit` / `pre-push` 与 DevGuard 项目 Hook 串联，并把项目本地
`.git/hooks` 设为有效 Hook 路径。复验会拒绝“文件已生成但 Git 实际忽略”的假安装。
生成项目可随时运行 `.\.venv\Scripts\python.exe scripts\install_hooks.py --root .`
重装或修复组合 Hook，无需修改用户级 Git 配置。

已有目录默认拒绝写入。只有 Owner 明确确认覆盖风险后才使用 `--force`；该参数只
覆盖 manifest 同名目标，不删除目录内其他文件。

## Profile

| Profile | 内容 | 适用场景 |
|---------|------|----------|
| `core` | 根文档、计划、Git 属性、依赖、双阶段 hooks、最小治理 CI、自检与测试 | 个人或小型项目 |
| `optional` | `core` 全部内容 + CODEOWNERS、决策与报告目录 | 团队项目 |

脚手架源文件位于 `scaffold/core/` 与 `scaffold/optional/`。复制范围由
`scripts/setup_scaffold.py` 的 `CORE_MANIFEST` / `OPTIONAL_MANIFEST` 唯一确定，
目录遍历不会自动把临时文件带入目标。

## 只验证，不写入

```powershell
py -3.11 scripts\setup_scaffold.py C:\path\to\project --verify --require-hooks
```

profile 默认从目标的 `.devguard.json` 读取，也可显式传 `--profile optional`。

## 其他模板资产

- `html-report-template/`：本仓仪表盘 HTML 渲染素材；由
  `scripts/render_dashboard.py` 跨平台入口调用。
- `final-report-template/`：高密度最终报告素材，不属于初始化 core 闭包。
- 目录根部旧配置/脚本：仅用于本仓历史同步与兼容，不是新项目部署入口。

物理载荷禁止出现 `.tmp`、`.bak`、`.pyc` 或 `__pycache__`。
