# M8 基础设施（infrastructure）

> devguard 模块设计文档 · v1.0 · 2026-06-10
> 配套文档：[简报.md](简报.md) · [设计.md](设计.md) · [实现计划.md](实现计划.md) · [阅读笔记.md](阅读笔记.md) · [deliverable.md](deliverable.md)
> 更新: 2026-07-11

---

## 三句话读懂

`M8 infrastructure` 是 devguard 的**强制约束防线**——把 17 规范的全部红线以可执行形态落到仓库根：

1. **5 阶段 CI** —— lint / test / l4-conventions / compliance / build，每阶段各管一摊
2. **10 个 pre-commit 钩子** —— 双层（pre-commit 9 个 + commit-msg 1 个），提交时强制卡口
3. **65 个 L4 测试** —— `tests/conventions/` 用 Python 代码验证规范本身的正确性

---

## 文档索引

| 文档 | 读什么 | 适合谁 |
|------|--------|--------|
| **简报.md** | ≤80 行速读 + 防线拓扑 mermaid + 关键数字 | 所有人先看 |
| **设计.md** | 5 阶段 / 10 钩子 / L4 详解 + 双层钩子 + 治理文件矩阵 + 边界 + 验收 | 所有人细读 |
| **实现计划.md** | V0.1 → V2.0.1 八阶段历史 + 每次增量的钩子/CI 变化 | 想理解"为什么是 10+5"时读 |
| **阅读笔记.md** | 章节导航 + 概念索引 + BDD 清单 + 思考题 + 易踩坑速查 | 深度阅读时打开 |
| **deliverable.md** | 7 件交付物清单 + 维护清单 + 治理文件维护 | 评审/交付时检查 |
| **设计.html** | 设计.md 的 HTML 渲染版 | 浏览器预览 |
| **实现计划.html** | 实现计划.md 的 HTML 渲染版 | 浏览器预览 |

---

## 快速预览

```
开发者视角                        系统做了什么
────────                        ──────────
"git commit"                    10 钩子自动跑（pre-commit 9 + commit-msg 1）
"git push"                      CI 5 阶段流水线触发（lint → test → l4 → compliance → build）
"PR merge"                      CODEOWNERS 自动 assign owner
"改 17 规范"                    推送到 PR → CI 跑 L4 测试 → 验证规范自洽
"密钥泄漏到代码"                gitleaks pre-commit 钩子立即拦截
"worklog 文件名不规范"          commit-msg-worklog-ref 钩子拒绝 commit
"commit 格式错"                 commitlint 钩子拒绝 commit
"openapi.yaml 有动词路径"       spectral 步骤（CI lint 阶段）失败
"模块有循环依赖"                importlinter 步骤（CI lint 阶段）失败
"doc 标题重复"                  markdownlint 钩子立即拦截
```

---

## 与其他模块的关系

- **被规范驱动**：`conventions/_meta.yaml`（M1）的 `ci` 节是真源，渲染出本模块的 `.github/workflows/ci.yml` + `.pre-commit-config.yaml`
- **被脚本驱动**：`scripts/render_meta.py`（M4）从 `_meta.yaml` 渲染本模块的钩子配置
- **被 L4 验证**：`tests/conventions/`（本模块）用代码验证 M1 规范的正确性
- **被仪表盘引用**：`dashboard.html`（M7）显示"5 阶段 / 10 钩子 / 65 tests passed" 数据
- **被示例引用**：`src/<维度>/`（M3）的 ruff.toml / importlinter.ini 是规范落地的可运行版

---

## 关键数字（从 STATUS.md 摘录，2026-06-08 V2.0.1 时点）

| 指标 | 数值 |
|------|:---:|
| CI 阶段数 | 5（lint / test / l4-conventions / compliance / build） |
| pre-commit 钩子数 | 10（pre-commit 9 + commit-msg 1） |
| L4 测试用例数 | 65（tests/conventions/） |
| devguard 自身 dogfood 拦截次数 | 8 次（V1.5-V2.0.1 实证） |
| 治理文件数 | 6（CODEOWNERS / commitlint / markdownlint / gitleaks / spectral / importlinter） |
