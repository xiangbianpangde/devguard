# M8 基础设施 · 交付物清单

> 版本: v1.0 · 2026-06-10
> 状态: 设计文档已交付（模块本身已 49/49 完成）

---

## 7 件交付物

| # | 文件 | 状态 | 说明 |
|---|------|:---:|------|
| 1 | 简报.md | ✅ | ≤80 行 + 防线拓扑 mermaid + 关键数字 |
| 2 | 设计.md | ✅ | 模块定位·5 阶段 CI·10 钩子·L4 65 tests·治理文件矩阵·边界·dogfood |
| 3 | 实现计划.md | ✅ | V0.1 → V2.0.1 八阶段历史 + dogfood 拦截 8 次 |
| 4 | 阅读笔记.md | ✅ | 章节导航·概念索引·BDD 清单·思考题·易踩坑速查 |
| 5 | README.md | ✅ | 文件夹索引 |
| 6 | 设计.html | ⬜ 待生成 | 设计.md 的 HTML 渲染版 |
| 7 | 实现计划.html | ⬜ 待生成 | 实现计划.md 的 HTML 渲染版 |

---

## 模块本体的交付状态

| 子模块 | 状态 | 数量 | 路径 |
|--------|:---:|:---:|------|
| CI 5 阶段 | ✅ | 1 文件 | `.github/workflows/ci.yml`（173 行）|
| pre-commit 10 钩子 | ✅ | 1 文件 | `.pre-commit-config.yaml`（54 行）|
| L4 测试 | ✅ | 10 文件 / 65 tests | `tests/conventions/` |
| 治理文件 | ✅ | 6 文件 | CODEOWNERS / commitlint / markdownlint / gitleaks / spectral / importlinter |
| 模板同步源 | ✅ | 7 文件 | `docs/templates/devguard/` |
| dogfood 实证 | ✅ | 8 次拦截 | `worklogs/2026-06-08_v20-devguard-dogfood.md` |

---

## 维护清单（持续）

- [ ] 改 `.github/workflows/ci.yml` → 同步 `docs/templates/devguard/.github/workflows/ci.yml`
- [ ] 改 `.pre-commit-config.yaml` → 改 `conventions/_meta.yaml` + 跑 `render_meta.py`（不要手改！）
- [ ] 改治理文件（CODEOWNERS / commitlint / markdownlint / gitleaks / spectral / importlinter）→ 同步 `docs/templates/devguard/` 对应文件
- [ ] 改 `tests/conventions/` → 同步 `docs/templates/devguard/tests/conventions/`
- [ ] commit message 加 `[infra]` 标记以便追溯
- [ ] 每次新增/修改钩子 → 跑 L4 测试 + dogfood 自证
- [ ] 收束节点到达 → 跑 L4 65 tests + CI 全绿

---

## 治理文件维护要点

| 文件 | 改动触发条件 | 验证方式 |
|------|------------|---------|
| `.github/CODEOWNERS` | 新增规范维度 / 改 owner | GitHub Web UI PR 验证 |
| `commitlint.config.js` | 03-git §一 红线变化 | `git commit` 验证 |
| `.markdownlint.json` | 06-documentation §一 红线变化 | markdownlint 钩子验证 |
| `.gitleaks.toml` | 新增教学反例文件 / 改白名单 | 故意提交含密钥代码验证 |
| `.spectral.yaml` | 04-api §一 红线变化 | CI lint 阶段验证 |
| `importlinter.ini` | 01-architecture §一 红线变化 | `lint-imports` 本地验证 |

---

## Owner 决策点（针对未来扩展）

- [ ] 钩子是否扩到 11+（如 secretlint / shellcheck / hadolint）？
- [ ] CI 是否支持跨平台 runner（macOS / Windows）？
- [ ] L4 测试是否并行跑（规模到 500+ 时需要）？
- [ ] dashboard.html 是否支持增量渲染（性能优化）？
- [ ] gitleaks 是否升级为 secretlint（更多规则）？
- [ ] commitlint config warning 噪音是否长期保留（技术债 #2）？

---

## 与其他模块的接口

| 上游 | 接口 | 下游 |
|------|------|------|
| M1 `conventions/_meta.yaml` | `ci` 节 + `l1_check` 字段 | M8 `.pre-commit-config.yaml` + `ci.yml` |
| M4 `scripts/render_meta.py` | 渲染钩子配置 | M8 `.pre-commit-config.yaml` |
| M8 `tests/conventions/` | L4 65 tests | M7 `dashboard.html` 数字段 |
| M8 `ci.yml build 阶段` | 渲染 dashboard | M7 `dashboard.html` |
| M3 `src/<维度>/` | 规范落地配置 | M8 `ci.yml lint 阶段` 验证 |
