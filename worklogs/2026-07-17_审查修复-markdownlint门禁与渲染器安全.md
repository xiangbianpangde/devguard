# 工作日志：审查修复—markdownlint 门禁与渲染器安全

> 日期: 2026-07-17
> 功能点: -（外部代码审查后续加固，未新增功能点行）
> 关联 BDD: -

## 做了什么

基于一轮只读代码审查的 🔴1-3 + 🟡4 结论，在 `fix/review-hardening-20260717` 分支实施 4 项修复：

1. **markdownlint POSIX 门禁空转**：`lint_markdown.py` 此前 `subprocess.run(cmd_list, shell=True)` 在 POSIX 只执行 `args[0]`（裸 npx），markdownlint 从未运行却 exit 0。改为仅 win32 用 `shell=True`，POSIX 列表直跑；`shutil.which("npx")` 预检 + `FileNotFoundError` 捕获，npx 缺失时非零退出。
2. **ruff 版本四方漂移**：pyproject(0.6.0) / requirements-dev(0.15.20) / CI(0.6.0) / scaffold 模板(0.11.7) 统一收敛到 **0.15.20**；`conventions/_meta.yaml` 新增 `toolchain.ruff` 作为单一真源，`check_consistency.py` 与 `test_ci_contract.py` 改为从真源读期望值。
3. **脚本模板漂移盲区**：`check_template_drift.py` 新增 `check_script_mirrors()` 逐字节对比 `scripts/` ↔ `docs/templates/devguard/scripts/`；同步了 3 个已漂移副本（render_meta.py、lint_markdown.py、collect_l4_stats.py——后者模板副本还带 `L4_STATS=0/0` 假通过旧 bug）。
4. **render_meta 截断 bug**：`_strip_existing_grade_section` 改用 `^## 分级标签[ \t]*$` 行级正则（修 `### 分级标签说明` 子串误判）；缺 `---` 分隔符时抛 `GradeSectionError`；`render_convention_grade` 改为全量预演后统一落盘（任一篇畸形则零写入）。

完成项：

- [x] 4 项修复全部落地，新增 16 个 L4 测试（含边界与异常路径）
- [x] 模板脚本副本三份同步，漂移检测实测可检出人为漂移
- [x] CHANGELOG Unreleased + STATUS 更新标签/测试数（最小合规修改，未动机器标记）
- [ ] ruff.toml per-file-ignores 相对路径、CI job 合并、gitleaks 哈希钉版（审查 🟡5-7/🔵 项，本轮明确不做）

## 验证结果

- `pytest tests/conventions -q`（.venv，PATH 含 .venv/bin）：**179 passed**（基线 163 + 净增 16）
- TDD 红→绿：实现前新增测试 17 个失败 / 15 个通过，实现后全绿
- POSIX 实测：仓内放置坏 md（MD018+MD009）→ `lint_markdown.py` exit=1 并打印违规；干净仓库 exit=0（261 个 md）
- render_meta 实测：缺 `---` → `GradeSectionError`；`### 分级标签说明` → found=False 原文保留；正常小节剥离后正文完整；`--check` 双 target 均 OK
- 漂移检测实测：/tmp 副本人为改模板副本 → 检出并点名 render_meta.py；仓库现状 `check_template_drift.py` OK
- `ruff check scripts/`（0.15.20）：All checks passed；`check_consistency.py`：24/24 = 100.0%
- `.pre-commit-config.yaml` 由 `render_meta.py --render pre-commit-config` 重新渲染（diff 仅 rev 一行）

## 关键决策

| 决策 | 原因 | 影响 |
|------|------|------|
| 版本真源放 `_meta.yaml` 新 `toolchain` 节而非解析 requirements-dev.txt | 项目哲学：_meta.yaml 是一切渲染/校验的 single source of truth | 改版本需同步四处钉版，但有测试+一致性评分双闸门兜底 |
| 漂移检查做逐字节对比而非章节级 | 脚本无"章节"概念；check_ai_workflow 等既有两副本本就逐字节相同 | 模板脚本任何手改都会被 CI compliance 阶段拦截 |
| render 预演后统一落盘 | 单文件原地写会在第 N 篇畸形时留下前 N-1 篇半成品 | 渲染失败=零副作用 |
| 新增 `tests/conventions/test_template_drift.py` | 33 个现有测试均按脚本/主题一文件聚焦，漂移检测无既有归属文件（FILE_GRAPH §tests/conventions 为 L4 测试目录） | 新增 1 文件，其余改动均为原地编辑 |

## 遇到的问题

- 仓外路径（/tmp）喂给 markdownlint-cli 会触发 ignore 库 RangeError（exit≠0，失败闭合但报错难看）：不影响仓内真实用法，仓内文件实测正常
- 模板 collect_l4_stats.py 是 V6.3 旧版（带假通过 bug）：以根版为权威同步，漂移检查防复发
- 首次提交时 `core.hooksPath` 指向全局 Codex hooks（`~/.codex/git-hooks`），`.git/hooks` 的 pre-commit 未触发；改跑 `pre-commit run --all-files` 兜底，抓到 1 个 E501 与 **ruff 0.15.20 格式化差异（19 个文件隐式字符串拼接风格变化）**——这是版本收敛的预期副作用，已随本提交一并落盘并通过 `ruff format --check` 全仓稳定（99 files formatted）
- 提交信息引用本 worklog 即可满足 check_worklog_ref；修订（amend）时 worklog 需有暂存变更，故本节同步补记

## 给下一位的交接

> 下一轮可做审查报告 🟡5-7：`src/coding/ruff.toml` per-file-ignores 改配置相对路径（IDE 裸跑 ruff 不再报 15 个教学反例）、CI test/l4 job 去重、gitleaks 版本对齐+哈希钉版。push 与 PR 由 owner 确认后执行。

## 验收报告落盘（2026-07-17 续）

- [x] Owner 要求留档 → 按 final-report-template 高密度学术风（对齐 `docs/reports/2026-06-08_devguard_V1.5_V2.0_merged_report.html` 格式：KPI 卡 + 健康度仪表 + Mermaid + Tab + 多节骨架）撰写 `docs/reports/2026-07-17_devguard_审查修复_验收报告.html`（首版 8 要素契约 report 已按 Owner 反馈推翻重写）
- [x] `check_html_artifact.py --all` 通过（本报告无 doc-template 声明 → untyped，仅 WARN，与 merged_report 同等地位）；全量 pytest 179 passed 零回退
- 门禁实录：`check_worklog_ref` 要求被引用 worklog 必须出现在本次暂存变更 → 本节补记后随报告同提交，链路成立
