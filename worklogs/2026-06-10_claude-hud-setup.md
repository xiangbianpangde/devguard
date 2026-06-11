# Worklog — Claude HUD 启用 (/claude-hud:setup)

> 日期: 2026-06-10
> 任务: 跑 /claude-hud:setup，启用 claude-hud 替代自写 statusline.sh
> 收束节点: 无（环境配置，非功能点）

## 做了什么

按 `~/.claude/plugins/marketplaces/claude-hud/commands/setup.md` 走完 5 步流程，把 Claude Code statusLine 从自写 bash 切到 claude-hud 插件：

- [x] 走完 setup 5 步（Ghost 检测 / 运行时 / 测试命令 / 写 settings.json / 可选特性）
- [x] 验证重启后 HUD 正常出现

1. **Step 0 Ghost 检测**：cache/registry/marketplace 全 YES，无 temp 残留，EXDEV 风险 NO
2. **Step 1 检测运行时**：plugin=`/mnt/c/Users/yhn/.claude/plugins/cache/claude-hud/claude-hud/0.1.0/`，runtime=`/usr/bin/node`，source=`dist/index.js`
3. **Step 2 测试命令**：mock stdin 跑通，输出含 5h/Weekly 用量条
4. **Step 3 写 settings.json**：用 `jq` 合并 `statusLine` 段（434 字节 bash -c 字符串，含 `\\$(NF-1)` 双反斜杠转义），保留其他 8 个键，JSON 合法 + 无 BOM
5. **Step 4 可选特性**：启用 `showTools`/`showAgents`/`showTodos`（用户选；走本地 transcript JSONL 解析，**不消耗 API token**）
6. **Step 5 验证**：用户重启 Claude Code 后确认 HUD 出现

## 验证结果

- Step 2 mock 测试输出含完整 5h/7d 用量条（用户原诉求）
- settings.json：`jq -e .` 合法，首字节 `{` 非 BOM
- 配置备份：`settings.json.bak-20260610-174659`
- 旧 `statusline.sh` 保留（可手动回滚）
- 用户确认重启后 HUD 出现

## 关键决策

- **config.json 写到 `/mnt/c/Users/yhn/.claude/plugins/claude-hud/`**（不是 cache 目录）— 这是 setup.md 指定的位置，与 cache 内的 `0.1.0/` 版本目录解耦
- **不写 Session info / Session name / Custom line** — 用户只选了 tools/agents/todos
- **stale 阈值机制失效** — claude-hud 的 5h/7d 用量由 stdin JSON 实时提供，不依赖本地状态文件；陈旧数据由 Claude Code 自身的 API 决定
- **可回滚**：恢复 `settings.json.bak-20260610-174659` + 删 `plugins/claude-hud/config.json` + 删 `cache/claude-hud/`

## 交付物

- `~/.claude/settings.json` — statusLine 指向 claude-hud
- `~/.claude/plugins/claude-hud/config.json` — 启用 tools/agents/todos
- 旧 `~/.claude/statusline.sh` 保留（参考用，4.5 KB bash + jq）
- `~/.claude/statusline.ps1` 保留（之前已有）
- `~/.claude/settings.json.bak-20260610-174659` — 改前快照

## 交接

- 后续如要调 HUD 样式：编辑 `~/.claude/plugins/claude-hud/config.json`（无需重启 plugin，会被热加载）
- 如要卸载：`/plugin uninstall claude-hud`，再把 settings.json statusLine 段还原或清空
- 详细配置项参考 `cache/claude-hud/claude-hud/0.1.0/CLAUDE.md` + `commands/configure.md`
