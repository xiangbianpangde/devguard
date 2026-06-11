# Worklog — Claude Code statusLine 切到 bash + jq

> 日期: 2026-06-10
> 任务: 把 ~/.claude/statusLine 从 PowerShell 切到 bash + jq，实现 /usage 风格持续显示
> 收束节点: 无（环境配置，非功能点）

## 做了什么

把 `~/.claude/settings.json` 的 `statusLine.command` 从 `powershell statusline.ps1` 切到 `bash /mnt/c/Users/yhn/.claude/statusline.sh`，并在 `/mnt/c/Users/yhn/.claude/statusline.sh` 落地 bash 版本脚本。

- [x] settings.json 切换 + bash 脚本落地
- [x] 10 个 stdin 场景全部预期输出

- **输入约定**（沿用 Claude Code + claude-hud 插件 schema）：stdin JSON 含 `model.display_name` + `rate_limits.{five_hour,seven_day}.{used_percentage,resets_at}`
- **输出格式**：`Opus 4.8 │ session 33% ↻now │ week 3% ↻1d22h (stale)`，完全匹配用户给的目标样例
- **颜色**：模型名 cyan、百分比按阈值上色（<50 绿 / 50–79 黄 / ≥80 红）、分隔符灰色、stale 红色
- **时间格式**：`now` (<60s) / `Xm` / `XhYm` / `XdYh`；兼容 10 位秒级和 13 位毫秒级 resets_at
- **陈旧检测**：状态文件 `/mnt/c/Users/yhn/.claude/statusline-state.json` 记录 last_seen；stdin 无 rate_limits 且距 last_seen > 10 分钟，标 `(stale)`；阈值可用 `STATUSLINE_STALE_SEC` 环境变量覆盖

## 验证结果

10 个 stdin 场景全部预期输出：

1. 完整数据 → `Opus 4.8 │ session 33% ↻now │ week 3% ↻1d22h`（完全匹配用户样例）
2. 缺 rate_limits → `Opus 4.8 │ week —`（不崩，week 段降级）
3. 空 stdin → 0 bytes（silent exit 0）
4. 非法 JSON → 0 bytes
5. 85% → 红色
6. state=700s 前 + 当前无 usage → `(stale)` 出现
7. state=700s 前 + 当前有 usage → 不标 stale（被新数据刷新）
8. 2h30m 倒计时 → `↻2h29m`（差 1 分是 NOW 重算）
9. 45m 倒计时 → `↻44m`
10. 13 位毫秒级 resets_at → 正确换算为分钟

settings.json 改后用 `jq -e .` 校验合法，旧 ps1 保留供回滚（不主动删）。

## 关键决策

- **陈旧文件路径统一**：`${HOME}/.claude/...`（WSL 下是 `/home/xbpd/...`）≠ `/mnt/c/Users/yhn/.claude/...`（Windows 真实目录）。硬编码到 `/mnt/c/Users/yhn/.claude/statusline-state.json` 避免 WSL HOME 漂移导致 stale 永远不触发
- **陈旧语义简化**：用单 `last_seen`（不是 per-window），因为 rate_limits 数据通常同时返回
- **stale 标在 week 段**：用户的样例就是这样，保持视觉一致
- **不动 `STATUS.md` 49/49 进度**：本次是环境配置，不是 devguard 功能点
- 旧 `statusline.ps1` 保留 1 周观察期再决定是否删
- 若要切到 claude-hud 插件（更完整的 HUD），可参考 `~/.claude/plugins/marketplaces/claude-hud/`，但本次只需 /usage 风格，未启用插件

## 交接

- 脚本：`/mnt/c/Users/yhn/.claude/statusline.sh`（4.5 KB，bash + jq，0 外部依赖）
- 状态：`/mnt/c/Users/yhn/.claude/statusline-state.json`（运行时自动创建）
- 配置：`~/.claude/settings.json` 的 `statusLine.command`
- 重启 Claude Code 后生效；用户需肉眼确认底部 status line 与上方目标样例一致
