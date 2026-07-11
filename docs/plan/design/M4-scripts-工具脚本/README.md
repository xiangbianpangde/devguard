# M4 工具脚本（scripts/）

> devguard 模块设计文档 · v1.0 · 2026-06-10
> 配套文档：[简报.md](简报.md) · [设计.md](设计.md) · [实现计划.md](实现计划.md) · [阅读笔记.md](阅读笔记.md) · [deliverable.md](deliverable.md)
> 更新: 2026-07-11

---

## 三句话读懂

`scripts/` 是 devguard 的**自动化工具集**——把"规范真源"和"红线条目"翻译成可执行命令：

1. **10 个脚本** —— 1 个核心渲染枢纽（render_meta.py）+ 4 个 L1 红线检测（check_*.py）+ 2 个仪表盘入口（start_server.py + 打开仪表盘.bat）+ 3 个工具脚本（lint_markdown / collect_l4_stats / fix_render_date）
2. **真源到下游的桥梁** —— `render_meta.py` 从 `_meta.yaml` 投射到 4 个产物：pre-commit 钩子、CI 范围、规范分级标签、dashboard 数据段
3. **红线条目即脚本** —— `_meta.yaml` 的 `l1_check` 字段直接对应 `scripts/check_*.py` 文件名——改一处即可全链路同步

---

## 文档索引

| 文档 | 读什么 | 适合谁 |
|------|--------|--------|
| **简报.md** | ≤80 行速读 + 10 脚本速览表 + 触发场景 + 调用关系 mermaid | 所有人先看 |
| **设计.md** | 模块定位·10 脚本逐个·渲染核心·L1 检测设计·边界·验收 | 所有人细读 |
| **实现计划.md** | V0.x 起步 → V2.0.1 dogfood 五阶段历史演进 | 想理解"为什么是 10 个"时读 |
| **阅读笔记.md** | 章节导航 + 概念索引 + BDD 清单 + 思考题 + 易踩坑速查 | 深度阅读时打开 |
| **deliverable.md** | 7 件交付物清单 + 维护清单 + Owner 决策点 | 评审/交付时检查 |
| **设计.html** | 设计.md 的 HTML 渲染版 | 浏览器预览 |
| **实现计划.html** | 实现计划.md 的 HTML 渲染版 | 浏览器预览 |

---

## 快速预览

```
开发者视角                          系统做了什么
────────                          ──────────
"改了 _meta.yaml"                  render_meta.py --render 同步到 .pre-commit-config.yaml
"commit message 没带 worklog 引用" check_worklog_ref.py 拦下
"想看仪表盘"                       双击 打开仪表盘.bat → 8080 端口起 start_server.py
"CI compliance 阶段红"             check_compliance.py 报告哪条 L1 配置缺失
"L4 测试通过数"                    collect_l4_stats.py → 注入 dashboard.html 模板
```

---

## 与其他模块的关系

- **真源依赖**：`conventions/_meta.yaml`（M1）→ 渲染目标
- **被钩子调用**：`.pre-commit-config.yaml`（M7/M8）调用 `lint_markdown.py` + `check_worklog_ref.py`
- **被 CI 调用**：`.github/workflows/ci.yml`（M8）调用 `render_meta.py` / `check_compliance.py` / `check_ai_workflow.py` / `check_code_understanding.py` / `collect_l4_stats.py`
- **被仪表盘调用**：`start_server.py` + `打开仪表盘.bat` 是 `dashboard.html`（M7）的本地入口
- **被模板派生**：`docs/templates/devguard/scripts/` 提供同套脚本模板，devguard 实例化
