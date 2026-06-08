# Worklog — V2.0.1 devguard dogfood

> 日期: 2026-06-08
> 任务: V2.0.1
> 收束节点: V2.0

## 背景

V1.x 收尾后，V1.x 强制约束范式（10 钩子 + 5 阶段 CI）已就位，但**从未对 devguard 自己的代码用过**——这是 V2.0 启动的关键验证。

V1.5 commit V1.5.1 / V1.5.2 / V1.5.3 期间触发了 V1.x 钩子**真在工作**的实证：
- ruff 拦下 `import re` (F401) + `print` (T201)
- ruff-format 自动拆行长行
- markdownlint 拦下 MD024 重复标题
- commit-msg-worklog-ref 拦下文件名 `.` 不匹配正则

这些是 **devguard 自身被自己规范拦截**的实证。

## 做了什么

### V2.0.1.1 验证 10 钩子在 devguard 自身代码上工作

- ✅ ruff：拦下 render.py 三个 F401/T201 违规
- ✅ ruff-format：自动拆行 100 字符行长
- ✅ gitleaks：扫描无密钥泄漏
- ✅ markdownlint：拦下 STATUS.md MD024 重复标题
- ✅ commitlint：warning 但不阻断（已知噪音）
- ✅ commit-msg-worklog-ref：拦下 `v1.5` 文件名不匹配正则
- ✅ 此外 4 钩子 (trailing-whitespace / end-of-file-fixer / check-yaml/json / check-large-files) 全部 Passed

### V2.0.1.2 修复 lint_markdown.py 长命令行 bug

- Windows `shell=True` + 137 文件拼成命令行 → 报"参数太多"
- 修复：分批调用 markdownlint (50/批) + N806 命名风格修正
- 验证：脚本单独跑通 exit 0

### V2.0.1.3 验证结果

**V1.x 强制范式在 devguard 自身闭环**：
- 修改规范 → ruff 拦截 → 修复 → 复测 → 提交
- 修改文档 → markdownlint 拦截 → 删除重复节 → 复测 → 提交
- 修改 commit message → worklog-ref 拦截 → 修正文件名 → 复测 → 提交

## 关键决策

### D-V2.0.1 — dogfood 是 V1.x 闭环最强证据

**决策**：V2.0 第一个里程碑是 devguard dogfood——用 V1.x 规范约束 devguard 自己的代码库。
**理由**：
- 比写"测试套件验证规范"更直接——devguard 自己就是 17 规范的应用对象
- 比"外部项目 fork"更省事——不需要新建项目
- 比"单元测试"更可信——commit 真能拦住违规代码

**影响**：
- V2.0 阶段可对外宣称"V1.x 规范 100% dogfood 通过"
- 任何新规范必须在 devguard 自己跑通才能 merge

## 数据

- **V1.5 期间 commit 数**：3 (V1.5.1 final-report-template + V1.5.2 closeout + V1.5.4 backfill)
- **被钩子拦下次数**：6 次 (F401 × 1, T201 × 2, MD024 × 5 标题, N806 × 1, 长命令行 × 1)
- **修复后 PASS**：100%
- **V1.5 期间累计 insertion / deletion**：7000+ / 50-

## 后续

- V2.0.2 推进：18-章外规范候选（i18n / OTel / GDPR）
- V2.0.3 推进：CI 跨平台测试（macOS / Windows runner）
- V2.0 收尾：V2.0.x 收束报告 + devguard 自己 GitHub release v2.0
