# 基准约束脚手架 — 一键复制最小约束基线（V2.3 #49）

> 复制器：`scripts/setup_scaffold.py`（在本仓运行，把基线写入新项目目录）。
> 区分**必带层**（流程强制核心，任何项目都该有）与**可选层**（依赖 Claude Code / 流程成熟度）。
> 更新: 2026-06-11

## 快速上手（3 步）

```bash
# 1. 在本仓运行复制器（--with-optional 附带可选层）
python scripts/setup_scaffold.py <新项目目录> [--with-optional]

# 2. 在新项目里：改真源 → 渲染钩子配置
#    编辑 conventions/_meta.yaml（项目名 / 规范列表）
python scripts/render_meta.py --render pre-commit-config

# 3. 装钩子（commitlint 另需 npm i -D @commitlint/cli @commitlint/config-conventional）
git init && pip install pre-commit
pre-commit install && pre-commit install --hook-type commit-msg
```

之后按 `docs/templates/` 模板实例化 `CLAUDE.md` / `STATUS.md` / `README.md` / `docs/plan/开发清单.md`，即可获得与本仓同款的"汇报不断档 + 豁免留痕 + 文档同步"流程强制。

## 必带层（core）

| 类别 | 内容 |
|------|------|
| 真源 + 渲染器 | `conventions/_meta.yaml`（模板骨架 + 本仓 live 钩子节按层拼接）+ `scripts/render_meta.py` |
| 7 个通用流程钩子 | worklog 引用/同步/结构（#36-#38）+ 文件放置（#45）+ 豁免登记（#51）+ 更新标签（#53/#54）+ 四件套同步（阶段C） |
| L1 工具配置 | `commitlint.config.js` / `.markdownlint.json` + `lint_markdown.py` / `src/coding/ruff.toml` |
| CI | `.github/workflows/ci.yml`（5 阶段：lint / test / l4-conventions / compliance / build） |
| 文档模板 | CLAUDE / README / STATUS / worklog / plan开发清单 / plan背景 / BDD规格 七件 |
| 豁免账种子 | `meta/豁免清单.md`（§二 已含核心标记目录 + §三 空账） |

## 可选层（--with-optional）

| 类别 | 内容 | 依赖 |
|------|------|------|
| 收束硬闸门 | `check_convergence_gate.py`（节点驱动，需 STATUS 机器标记） | 项目用收束节点流程 |
| HTML 模板族 + 校验 | 汇报/计划/实施设计/绘图素材库 4 模板 + `check_html_artifact.py` | 项目出 HTML 产出物 |
| 决策对齐 | `check_decision_alignment.py` + `.claude/agents/liaison.md` 交流 agent | 项目用设计提案流程 |
| 编辑当下护栏 | `hook_updated_tag_posttooluse.py` + `.claude/settings.json` | Claude Code |

## 注意

- 复制器拒绝写入非空目录（`--force` 覆盖同名文件）；清单源缺失会直接报错——保证脚手架与本仓不脱钩（有 L4 测试 `test_scaffold.py` 守护）。
- 目标项目的 `_meta.yaml` pre_commit 节来自本仓 live 版（按层过滤），其余节是模板骨架（占位符待填）。
- 收束闸门在新项目启用前，需在 STATUS.md 写入 `<!-- convergence-gate: nodes=… last_converged_fp=… -->` 机器标记。
