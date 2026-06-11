# M3 示例代码 · 交付物清单

> 版本: v1.0 · 2026-06-10
> 状态: 设计文档已交付（模块本身已 49/49 完成）

---

## 7 件交付物

| # | 文件 | 状态 | 说明 |
|---|------|:---:|------|
| 1 | 简报.md | ✅ | ≤80 行 + 7 子目录速览表 + 拓扑 mermaid |
| 2 | 设计.md | ✅ | 模块定位·7 子目录详介·落地策略·互检·边界·验收 |
| 3 | 实现计划.md | ✅ | V0.x 起步 6 子目录 → V0.x 扩展 +code-understanding → V0.x 重构 §二 1:1 对齐 |
| 4 | 阅读笔记.md | ✅ | 章节导航·概念索引·BDD 清单·思考题·易踩坑速查 |
| 5 | README.md | ✅ | 文件夹索引 |
| 6 | 设计.html | ⬜ 待生成 | 设计.md 的 HTML 渲染版 |
| 7 | 实现计划.html | ⬜ 待生成 | 实现计划.md 的 HTML 渲染版 |

---

## 模块本体的交付状态

| 子目录 | 对应规范 | 状态 | 关键文件数 |
|--------|---------|:---:|:---:|
| `architecture/` | 01-架构设计 | ✅ | 8（含 4 层 + importlinter.ini + main.py） |
| `coding/` | 02-代码编写 | ✅ | 5（ruff.toml + 4 个 .py） |
| `git/` | 03-Git 协作 | ✅ | 3（.gitignore + .pre-commit-config.yaml + commitlint.config.js） |
| `api/` | 04-API 设计 | ✅ | 2（main.py + .spectral.yaml） |
| `testing/` | 05-测试规范 | ✅ | 3（discount.py + test_discount.py + pytest.ini） |
| `documentation/` | 06-文档规范 | ✅ | 2（CHANGELOG.md + docstring_example.py） |
| `code-understanding/` | 08-代码理解与图谱 v3.0 | ✅ | 1（call_graph_example.py） |
| `README-示例代码总览.md` | — | ✅ | 1（组织方式说明） |

**合计**：7 个子目录 + 24 个有效源文件 + 1 个总览 README

### 引用关系

| 上游 | 引用本模块的位置 | 数量 |
|------|-----------------|:---:|
| `conventions/_meta.yaml` | `l1_check_path` 字段指向 `src/coding/ruff.toml` / `src/architecture/importlinter.ini` / `src/api/.spectral.yaml` | 3 |
| `docs/specs/08-examples.md` | 互检 src/ 整体 | 1 |
| `docs/templates/devguard/` | V0.x 重构时同步过 code-understanding 模板 | 1 |
| `worklogs/2026-05-27~28_*.md` | 多处提及本模块演进 | 5+ |

---

## 维护清单（持续）

- [ ] 改规范 §二 → 同步对应 `src/<维度>/` 配置文件 + worklog
- [ ] 改 `src/<维度>/` 配置 → 同步对应规范 §二 + worklog
- [ ] 新增教学示例 → 加到对应子目录 + 更新 `README-<维度>示例.md`
- [ ] `naming_bad.py` 故意违规必须保留（L4 测试复用）
- [ ] 改 `call_graph_example.py` 顶部 `# ruff: noqa` 列表前先看 L4 测试期望
- [ ] 改 `_meta.yaml.l1_check_path` 时确认 `src/` 内配置存在
- [ ] 跨子目录不加共享代码（每个子目录独立自治）
- [ ] `__pycache__` / `.ruff_cache` / `.pytest_cache` 持续忽略（已在 .gitignore）

---

## Owner 决策点（针对未来扩展）

- [ ] 是否新增 `src/security/`（02 安全子篇）作为独立子目录？
- [ ] 是否给 `src/code-understanding/` 增加 JS/Go/Rust 教学版本（多语言）？
- [ ] `src/api/` 是否要演示 FastAPI 之外的框架（Flask/Django）？
- [ ] 是否把 `src/` 拆成"教学版"和"产品模板版"两套？
- [ ] code-understanding 是否直接集成 CodeGraph 二进制（替换 AST 教学）？
