## 分级标签

> 本节为**渲染产物**（由 render_meta.py 从 _meta.yaml 自动生成）。
> 修改流程：改 `conventions/_meta.yaml` → 跑 `render_meta.py --render convention-grade`。
> **不要手改本节**（手改会被 `render_meta.py --check` 检测到，CI fail）。

| 级别 | 数量 |
|------|------|
| 红线 | 0 |
| 警告 | 0 |
| 推荐 | 0 |

**L1 检测**：CHANGELOG.md 存在（V1.1 章节级 L1）
**L3 路由**：任务类型=发布 → 必读本篇

---
# Changelog

All notable changes to devguard will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **markdownlint 门禁在 POSIX 空转**——`lint_markdown.py` 仅在 win32 使用 `shell=True`（.cmd shim 需要），POSIX 改为列表参数直跑；此前 `shell=True` + 列表参数在 POSIX 只执行裸 `npx`，markdownlint 从未运行却返回 0。npx 缺失时现在明确非零退出
- **render_meta.py 防截断**——`_strip_existing_grade_section` 改用 `^## 分级标签$` 行级正则（修 `### 分级标签说明` 子串误判）；小节缺 `---` 分隔符时抛 `GradeSectionError` 失败闭合，不再截断正文；render 改为全量预演后统一落盘
- **ruff 版本四方漂移**——统一收敛到 0.15.20，以 `conventions/_meta.yaml` 新增 `toolchain.ruff` 为单一真源；`check_consistency.py` 与 CI 契约测试改为从真源读期望值，不再硬编码版本字符串
- **脚本模板漂移盲区**——`check_template_drift.py` 新增 `scripts/` ↔ `docs/templates/devguard/scripts/` 逐字节镜像对比；同步了已漂移的 render_meta.py、lint_markdown.py、collect_l4_stats.py 模板副本（后者还带有 `L4_STATS=0/0` 假通过旧 bug）

## [V2.2.0] - 2026-07-11

### Added

- **ECC 十域对标闸门**——skills-first、规则真源、跨 Harness、profiles、hooks、安全、CI/TDD、事务部署、回执与量化治理均绑定可执行事实，门槛 80%
- **Codex/Claude 双入口**——core scaffold 生成 `AGENTS.md`、`CLAUDE.md`、canonical DevGuard skill、OpenAI 元数据与 credential-free 项目 Codex 配置
- **安装预演与事务回滚**——`--dry-run` 零写入列出完整载荷；逐文件唯一临时文件 + fsync + 原子替换，任一步失败恢复旧字节
- **生成项目 gitleaks**——密钥扫描进入 core pre-commit，不再依赖用户是否安装 ECC 全局 Hook

### Changed

- 合入所有本地/远程功能分支历史，冲突以 24 项一致性事实矩阵、10 项故障注入和跨平台 Python 实现为准
- 全量测试增至 163 项；仓外真实 E2E 生成 22 个 manifest 文件并通过 9 个 pre-commit 检查

## [V2.1.0] - 2026-07-11

### Added

- **可测治理**——`check_consistency.py` 以 24 个跨文件/可执行事实计算一致性，默认门槛 80%；`check_enforcement.py` 在隔离 Git 仓库执行 10 项故障注入，默认门槛 90%
- **8 个 commit-msg 治理闸门**——真实 worklog 引用、worklog↔STATUS、日志结构、文件放置、豁免登记、更新时间、三文档同步与收束节点
- **一键初始化**——`setup_scaffold.py <target> --install` 用 core/optional 显式 manifest 生成自包含治理项目，安装隔离依赖与双阶段 hooks，并在返回前 fail-closed 复验
- **跨平台 dashboard**——统一 Python 入口，L4 统计来自真实 pytest；详细功能表和机器进度标记保持同源

### Fixed

- 渲染器只向 Markdown 注入分级标签，恢复合法 MIT LICENSE 与 CODEOWNERS；所有渲染文本统一 LF + 单一 EOF 换行
- CI 不再先渲染后检查或吞掉 pytest 失败；L4 收集无法解析时失败，不再伪造 `0/0`
- STATUS/开发清单/CLAUDE 的 49/46/35 漂移统一为连续编号和同值机器标记
- 合规扫描从“文件存在即通过”提升为非空、可解析配置、可编译 Python 和真实 test 定义校验
- ECC/用户级全局 `core.hooksPath` 不再污染故障注入或阻断一键安装；临时测量使用空 Hook 隔离，新项目则保留并串联既有 `pre-commit` / `pre-push` 与 DevGuard Hook

## [V2.0.1] - 2026-06-08

### Fixed

- **lint_markdown.py 长命令行 bug**（V2.0.1.2）—— Windows `shell=True` 下 137 文件拼接成超长命令行报“参数太多”；改为分批调用 markdownlint（50/批）+ N806 命名风格修正，脚本单独跑通 exit 0

### Changed

- **devguard dogfood**（V2.0.1）—— V1.x 强制约束范式首次施加于 devguard 自身代码：10 钩子 + commitlint 在自身仓库触发 8 次拦截（ruff F401/T201、ruff-format 行长、markdownlint MD024、commit-msg-worklog-ref 文件名正则），全部修复后复测 100% PASS

## [V1.5] - 2026-06-08

### Added

- **final-report-template 模板沉淀**（V1.5.1）—— `docs/templates/devguard/final-report-template/`：template.html（41 占位符 + 11 Mermaid + 3 Tab + 5 进度条 + 1 模拟器）+ render.py（std-lib 渲染）+ example-data.json + demo.html + README
- **2 份 V1.x 最终汇报 HTML**（V1.5.3）—— 原始带数据版 + render.py 渲染版（0 残留占位符）

### Changed

- **README-模板索引 + FILE_GRAPH 同步**（V1.5.2）—— 登记 final-report-template 节点
- **STATUS 滞后修复 + worklog 断档补登**（V1.5.2 / V1.5.4）

## [V1.4] - 2026-06-07

### Added

- **17-contributing 规范入 _meta.yaml**（V1.4.1）—— CONTRIBUTING.md 章节级 L1
- **CONTRIBUTING.md 新建**（V1.4.1）—— 含行为准则、贡献类型、PR 流程、Issue 报告、开发流程、编码规范、commit 格式
- **GitHub 标准 6 件套齐**（V1.4）—— README + CHANGELOG + SECURITY + SUPPORT + LICENSE + CONTRIBUTING

## [V1.3] - 2026-06-07

### Added

- **16-license 规范入 _meta.yaml**（V1.3.1）—— LICENSE 章节级 L1
- **LICENSE 新建**（V1.3.1）—— MIT License + Copyright 2026 袁 (xiangbianpangde)
- **devguard user-facing README 重写**（V1.3.2）—— 占位 → 当前状态/快速开始/16 规范清单/反馈
- **GitHub 标准 5 件套齐**（V1.3）—— README + CHANGELOG + SECURITY + SUPPORT + LICENSE

## [V1.2] - 2026-06-07

### Added

- **15-support 规范入 _meta.yaml**（V1.2）—— SUPPORT.md 章节级 L1
- **SUPPORT.md 新建**（V1.2）—— 含项目性质、获取帮助、报告 Bug、FAQ、Out of Scope

## [V1.1] - 2026-06-07

### Added

- **13-changelog 规范入 _meta.yaml**（V1.1.1）—— CHANGELOG.md 章节级 L1
- **CHANGELOG.md 升级**（V1.1.1）—— 原 1 段 → V0.x 11 段 + V1.0 段 + V1.1 段
- **14-security 规范入 _meta.yaml**（V1.1.2）—— SECURITY.md 章节级 L1
- **SECURITY.md 新建**（V1.1.2）—— 含披露流程、修复承诺、致谢、适用版本 4 大段


### Added

- **14-security 规范入 _meta.yaml**（V1.1.2）—— SECURITY.md 章节级 L1
- **13-changelog 规范入 _meta.yaml**（V1.1.1）—— CHANGELOG.md 章节级 L1
- **SECURITY.md 新建**（V1.1.2）—— 含支持版本、漏洞报告 SLA、安全实践、Out of Scope

### Fixed

- **CHANGELOG 缺 Deprecated 段**（V1.1.1）—— 加 Deprecated 段，6 段齐全

### Deprecated

- **gitleaks-action@v2**（V3.3 替换）—— 改手动跑 gitleaks 8.24.3 binary
- **`scripts/fix_render_date.py`**（V0.3 临时）—— 改无害占位 + 删

## [V1.0] - 2026-06-07

### Added

- **12-codeowners 规范入 _meta.yaml**（V1.1）—— GitHub 自动审查分配
- **10 篇 l1_check_doc 字段**（V8.1）—— 每篇规范指向 L1 tool 官方文档 URL
- **11-readme 规范入 _meta.yaml**（V9.2）—— README 章节级 L1
- **10-templates-reporting 规范入 _meta.yaml**（V7.1）—— 模板 + reports/ 目录
- **09-dashboard-gen 规范入 _meta.yaml**（V6.2）—— 仪表盘模板 + 渲染脚本
- **grade.l1_check_path 字段**（V5.1）—— 6 篇规范 + L4 自动验证
- **章节级 L1 钩子**（V5.2 + V5.3）—— check_ai_workflow.py + check_code_understanding.py
- **dashboard.html CSP**（V5.4）—— `<meta http-equiv="Content-Security-Policy">` 防 XSS
- **render-mtime 自我刷新标识**（V5.5）—— `<meta name="render-mtime">` 字段
- **L4 元一致性测试**（V4.4）—— test_meta_l1_check.py 10 tests
- **L4 性能基线**（V2.5）—— test_perf_baseline.py 2.69s × 1.5 容忍
- **dashboard 字段同步**（V4.2）—— 53/53 实际值
- **markdownlint 钩子**（V3.1）—— 10 钩子 pre-commit
- **dashboard.html 整体切换**（V3.2）—— 100% (35/35) + 32 红线
- **gitleaks 手动跑**（V3.3）—— 绕开 v2 cache drift
- **commitlint 启用**（V2.3 / V0.2）—— npm @commitlint/cli
- **end-of-file-fixer**（V2.1）—— 统一 LF newline
- **render_meta.py 双轨同步**（V2.1）—— 模板版与主仓同步
- **core.autocrlf=false**（V2.1）—— 跨平台 newline 一致
- **src/coding/ruff.toml per-file-ignores**（V2.1）—— 测试 + 工具脚本豁免
- **scripts/check_worklog_ref.py**（V0.1）—— commit-msg worklog 引用强制

### Fixed

- **render.py 数据 bug**（V3.2）—— BDD 字符串 check 误跳数据行 + 跨节表格错收
- **render_date 跨平台**（V3.3）—— 改 static `latest` 彻底幂等
- **render.py 写文件强制 LF**（V3.3）—— CRLF→LF 跨平台一致
- **L4 自动收集 L4 数字**（V6.3 + V7.2 retry）—— V6.3 失败 + V7.2 找到 bash `VAR=空变无参` 根因
- **07-ai-workflow §一 红线扩展**（V9.1）—— 7 篇每篇 §一 红线验证
- **02-第零步_调研.md §一 红线缺口**（V9.1）—— 补"调研 4 问"段
- **docs/templates/devguard/README-模板索引.md 重建**（V8.2）—— V0.2 清理后丢失
- **dashboard.html 53/53 硬编码 → 真实值**（V4.2）
- **commitlint subject-case**（V0.2）—— L1 → l1
- **commit-msg-worklog-ref**（V0.2+）—— 强制 worklog 引用
- **render.py ruff S603/S607**（V0.2 修订）—— 豁免
- **render.py 缺 import subprocess**（V0.3 修订）—— 加 import
- **render.py 缺 subprocess 真实 import**（V0.3）—— 验证 sys.path

### Changed

- **dashboard.html 渲染模板**（V0.1 → V1.0）—— 从手写硬编码到模板化渲染
- **CI 5 阶段流水线**（V0.1）—— lint / test / l4-conventions / compliance / build
- **9 钩子 → 10 钩子**（V0.1 → V0.3）—— 加 markdownlint
- **8 规范 → 12 规范**（V0.1 → V1.0）—— 累计加 09/10/11/12
- **L4 套件 53 → 65 tests**（V0.1 → V0.9）

### Deprecated

- **gitleaks-action@v2**（V3.3 替换）—— 改手动跑 gitleaks 8.24.3 binary
- **`scripts/fix_render_date.py`**（V0.3 临时）—— 改无害占位 + 删

### Removed

- 无（V0.1 → V1.0 纯增量演进）

### Security

- **dashboard.html CSP**（V5.4）—— `<meta http-equiv="Content-Security-Policy">` 防 XSS
- **gitleaks 手动跑**（V3.3）—— 绕开 v2 cache drift 误报
- **CODEOWNERS**（V1.1）—— GitHub 自动审查分配

## [V0.1] - 2026-05-27

### Added

- 8 规范（01-08）+ ai-workflow 7 篇流程文档
- 9 钩子 pre-commit（trim whitespace / end-of-file-fixer / yaml / json / large files / ruff / ruff-format / gitleaks / commit-msg-worklog-ref）
- 5 阶段 CI（lint / test / l4-conventions / compliance / build）
- 35 个功能点 + 32 红线
- 33 L4 套件（初版）
- importlinter.ini（01-architecture 架构分层契约）
- scripts/check_compliance.py（合规扫描）
- scripts/render_meta.py（真源 → 产物渲染）
- 33 功能点
- docs/templates/devguard/ 双轨模板（html-report-template + importlinter + scripts）

### Security

- gitleaks 钩子（v0.1 用 gitleaks-action@v2）
- 教学反例 allowlist（src/coding/security_demo.py 等）
- commit-msg-worklog-ref 强制 worklog 引用

[V1.0]: ./收束报告-v1.0.md（待写）
[V0.1]: ./收束报告-v0.1.md
