# 2026-06-11 · ai-workflow 9 篇对齐 + 文件放置叶子级 + 4 问题补漏

## 完成了什么

- [x] 问题 2：ai-workflow L4 测试 7 失败修复 — `check_ai_workflow.py` + `test_07_ai_workflow.py` 重写对齐 v2.0 新 9 篇（01-流程全景/02-模块分类/03-设计规范/04-长程开发/05-思考设计/06-端到端流程/07-验收交付/08-汇报收束/09-部署规范），五核心原则（不越界/不黑盒/不断档/不拖欠/不积压）归口 README.md 单独校验
- [x] 问题 3：`_meta.yaml` 09/10 死链修复 — `09-dashboard-gen` 和 `10-templates-reporting` 的 `file` 字段从已不存在的 `07-汇报.md` 改为 `08-汇报收束.md`
- [x] 问题 4：STATUS(57) vs 开发清单(46) 口径统一 — 给两边 46 个编号功能点逐行打 fp HTML 注释标签；STATUS 详细列表里 11 行 V0.6–V1.5 衍展规范不打标；`check_plan.py` 改用 `FP_TAG.findall` 跨文件计数（替代旧的「整数首列行 vs 全部数据行」错配口径）
- [x] 问题 1：文件结构强制硬化 —
  - `scripts/check_file_placement.py` 升级为叶子级硬拦：模型改为 `ROOT_WHITELIST`（含 `.markdownlintignore`）+ `FREE_TOP_AREAS`（conventions/src/worklogs/scripts/meta/tests/.github/.claude）+ `DOCS_SUBSECTIONS`（plan/reports/research/specs/templates/历史文件）；允许 `docs/plan/design/<设计名>/` 容器（M1-M8 拆分设计文件夹）
  - 新增 `scripts/audit_file_placement.py` 全树审计脚本（exit 1 → CI），共用同一目录模型
  - 新增 `tests/conventions/test_file_placement.py`（8 个用例）+ `test_05_testing.py` 登记
  - 揪出真散文件 `docs/重构笔记-使用开发规范重构项目指南.md` 已 `git mv` 到 `docs/历史文件/`
- [x] 附带漂移清理：CLAUDE.md 4 处（07-汇报 → 08-汇报收束；05-完整流程 → README；06-第三步_收束节点 → 08-汇报收束）+ meta/FILE_GRAPH.md ai-workflow 子目录树改为新 9 篇 + 二级图谱引用 + 设计文件夹 7 件套说明 + scripts/check_status_updated.py + scripts/check_convergence_artifacts.py 注释文案
- [x] 删除 V1.0 残留：`conventions/ai-workflow_AI协作开发流程/05-完整流程与核心原则.md`（五原则已迁 README.md）
- [x] `.gitignore` 加 `docs/plan/design/_mermaid.min.js`（3.3MB 本地渲染脚手架不入库）

## 关键决策

- 问题 4 口径统一选「特殊标签」而非「两边同步成 1:1 行」：用户决策。STATUS 详细列表本质上是有意收敛的摘要表（含 11 行 V0.6–V1.5 衍展规范归档），强制它变 46 行会破坏摘要性。标签法两边各打各的标，跨文件只比标签数即可。
- 问题 1 文件放置硬化范围：用户决策「叶子级硬拦 + 全树审计」。叶子级模型设计上**不**强制 FILE_GRAPH §一 已枚举的精确子目录（如 `src/architecture/domain/`），允许已知顶层区内部自由嵌套（示例代码分层、模板分组、调研子树），只拦：根散文件 / docs 根散文件 / 未知 docs 子区 / 未知顶层区。
- 首批 commit 拆分：4 问题修复（规范/测试/钩子）一批；新增 M1-M8 设计文档群 + INDEX + 流程强制化总纲 + worklog 二批。

## 遇到的问题

- 初次叶子级过严：第一版模型用精确子目录枚举（VALID_DIRS），导致 audit 把 `src/architecture/domain/order.py`、`docs/reports/<日期>/`、`docs/research/<主题>/tree/` 等全部误报为违规。修正为「已知顶层区内部自由嵌套」语义。
- fp HTML 注释字面量被正则误数：STATUS.md 口径注释里写的字面 fp HTML 注释也被 `FP_TAG.findall` 计为 1，46 vs 47。修正注释里改用文字描述而非字面标签。
- commit 钩子拦截：第一次 `git commit` 被 markdownlint pre-commit 拦截（worklog 里 `#1 #2 #3 #4` 被识别成 ATX 标题缺空格）—— 改成「问题 1/2/3/4」措辞解决。

## 下一步

- 遗留（请你裁决）：conventions/01-08 + docs/templates/ 多模板里 12+ 处 `[ai-workflow 03-第一步_编写计划/04-第二步_迭代开发/06-第三步_收束节点/07-汇报].md` Markdown 链接仍死链（语义级映射，V2.0 按任务类型重组，旧"第二步 §2.6"在新结构里无对应章节）—— 建议单独立 #47 功能点做语义重映射；模板 `docs/templates/devguard/scripts/check_ai_workflow.py` 仍旧 7 篇硬编码，按 _meta.yaml 同步纪律该一并更新
- 推上 v2.2 收束节点

## 验证结果

- L4 全套：86/86 passed（新增 test_file_placement 8 个）
- check_ai_workflow.py：OK 9 篇 + §一 + 五原则
- check_plan.py：OK 46 ↔ 46 fp 标签
- check_status.py：OK 当前进度 4/15，收束节点 9
- audit_file_placement.py：340/340 合规（揪出+归档 1 个真散文件）
