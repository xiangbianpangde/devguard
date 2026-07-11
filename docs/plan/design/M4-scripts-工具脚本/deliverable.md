# M4 工具脚本 · 交付物清单

> 版本: v1.0 · 2026-06-10
> 状态: 设计文档已交付（模块本身已 49/49 完成）
> 更新: 2026-07-11

---

## 7 件交付物

| # | 文件 | 状态 | 说明 |
|---|------|:---:|------|
| 1 | 简报.md | ✅ | ≤ 80 行 + 10 脚本速览表 + 调用关系 mermaid |
| 2 | 设计.md | ✅ | 模块定位·10 脚本逐个·渲染核心·L1 检测设计·边界·验收 |
| 3 | 实现计划.md | ✅ | V0.x 起步 → V2.0.1 dogfood 五阶段历史演进路径 |
| 4 | 阅读笔记.md | ✅ | 章节导航·概念索引·BDD 清单·思考题·易踩坑速查 |
| 5 | README.md | ✅ | 文件夹索引 |
| 6 | 设计.html | ⬜ 待生成 | 设计.md 的 HTML 渲染版 |
| 7 | 实现计划.html | ⬜ 待生成 | 实现计划.md 的 HTML 渲染版 |

---

## 模块本体的交付状态

| 子模块 | 状态 | 数量 |
|--------|:---:|:---:|
| 渲染枢纽 render_meta.py | ✅ | 1 个 · 370 行 |
| L1 红线检测 check_*.py | ✅ | 4 个 · 460 行（98+66+238+58） |
| L1 红线检测 lint_markdown.py | ✅ | 1 个 · 54 行 |
| L4 测试 collect_l4_stats.py | ✅ | 1 个 · 48 行 |
| 入口工具 start_server.py | ✅ | 1 个 · 77 行 |
| 入口工具 打开仪表盘.bat | ✅ | 1 个 · 28 行 |
| 临时脚本 fix_render_date.py | ✅ | 1 个 · 2 行（intentional empty） |
| **总计** | **✅** | **10 个 · 1039 行** |

---

## 维护清单（持续）

- [ ] 改 `_meta.yaml` → 跑 `python scripts/render_meta.py --render`
- [ ] 改 `_meta.yaml` → 同步 `docs/templates/devguard/conventions/_meta.yaml`
- [ ] 改 `_meta.yaml` → commit message 加 `[meta]` 标记
- [ ] 新增 L1 检测脚本 → 同步 `_meta.yaml.l1_check` 字段 + 同步 `check_compliance.py` 的 L1_CHECKS 字典
- [ ] 新增 ai-workflow 流程文档 → 更新 `check_ai_workflow.py` 的 EXPECTED_FILES_AND_KEYWORDS
- [ ] 改 08 示例代码 → 同步 `check_code_understanding.py` 的 EXPECTED_FILES_AND_FUNCS
- [ ] CI 阶段脚本调用关系改动 → 同步 `.github/workflows/ci.yml`
- [ ] pre-commit 钩子改动 → 同步 `.pre-commit-config.yaml`（注意：是渲染产物，不能手改）

---

## Owner 决策点（针对未来扩展）

- [ ] 是否将 L1 检测脚本插件化（注册机制）？
- [ ] 是否新增 L2 警告类脚本？
- [ ] 是否引入跨平台 .sh 启动器（Mac/Linux）？
- [ ] dashboard 实时数据（定时刷新）？
- [ ] `render_meta.py` 增量渲染（只渲染变化部分）？
- [ ] commit-msg 多语言（unicode 文件名）？

---

## 关键文件/引用清单

### 模块本体
- `scripts/render_meta.py`（370 行，核心枢纽）
- `scripts/check_ai_workflow.py`（98 行，L1 红线）
- `scripts/check_code_understanding.py`（66 行，L1 红线）
- `scripts/check_compliance.py`（238 行，L1 红线）
- `scripts/check_worklog_ref.py`（58 行，L1 红线）
- `scripts/collect_l4_stats.py`（48 行，L4 测试）
- `scripts/lint_markdown.py`（54 行，L1 红线）
- `scripts/fix_render_date.py`（2 行，临时脚本存档）
- `scripts/start_server.py`（77 行，仪表盘入口）
- `scripts/打开仪表盘.bat`（28 行，Windows 启动器）

### 上下游关联
- `conventions/_meta.yaml`（真源）
- `.pre-commit-config.yaml`（渲染产物）
- `.github/workflows/ci.yml`（CI 5 阶段）
- `docs/templates/devguard/conventions/_meta.yaml`（模板版本）
- `docs/templates/devguard/html-report-template/render.py`（dashboard 渲染）

### worklog 引用
- `worklogs/2026-05-26_基础设施搭建.md`
- `worklogs/2026-05-27_规范正文v2重构.md`
- `worklogs/2026-05-28_08规范v3.0双图谱重构.md`
- `worklogs/2026-06-07_添加markdownlint.md`
- `worklogs/2026-06-08_v15-section3-hook-text-table-collapsed.md`
- `worklogs/2026-06-08_v20-devguard-dogfood.md`
- `worklogs/2026-06-09_ai-workflow-v2-rewrite.md`
