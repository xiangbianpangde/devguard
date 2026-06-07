# html-report-template — HTML 报告模板

## 用途

新项目 fork `devguard` 后，用本模板**自动生成 dashboard.html**：
- 数据源：`conventions/_meta.yaml` + `STATUS.md`
- 渲染脚本：`render.py`（纯 Python stdlib，无依赖）
- 风格：极简学术风（teal 主色 + 卡片网格 + 状态色编码）

## 复制为

```
{新项目仓库}/
└── docs/
    └── templates/   (本目录)
        ├── index.html
        └── render.py
```

新项目**不需要**整个 devguard 模板——只复制本目录 2 个文件即可。

## 使用流程

```bash
# 1. 准备数据源（新项目本身应该有）
ls /path/to/new-project/
  conventions/_meta.yaml
  STATUS.md

# 2. 渲染
python docs/templates/render.py \
    --meta /path/to/new-project/conventions/_meta.yaml \
    --status /path/to/new-project/STATUS.md \
    --out /path/to/new-project/dashboard.html \
    --l4-passed 51 \
    --l4-total 53

# 3. 启动（用项目自己的 start_server.py 或 python -m http.server）
python -m http.server 8080
# 访问 http://localhost:8080/dashboard.html
```

## 占位符清单

`index.html` 中的 `{占位}` 会被 `render.py` 替换：

| 占位 | 来源 | 含义 |
|------|------|------|
| `{project_name}` | `_meta.yaml.project` | 项目名 |
| `{render_date}` | 系统时间 | 渲染时间 |
| `{progress_pct}` / `{progress_done}` / `{progress_total}` | `STATUS.md` 表格 | 进度 |
| `{convention_count}` | `_meta.yaml.conventions` 长度 | 规范篇数 |
| `{red_line_total}` | `_meta.yaml.conventions[*].grade.red_line` 之和 | 红线总数 |
| `{l4_passed}` / `{l4_total}` | 命令行参数 | L4 测试统计 |
| `{convention_rows}` | `_meta.yaml.conventions` | 规范表行 |
| `{status_rows}` | `STATUS.md` 表格 | 功能点表行 |

## 集成到 CI

`.github/workflows/ci.yml` 的 `build` 阶段可加：
```yaml
- name: Render dashboard
  run: |
    python docs/templates/render.py \
      --meta conventions/_meta.yaml \
      --status STATUS.md \
      --out dashboard.html \
      --l4-passed 51 --l4-total 53
```

## 风格说明

- **极简学术风**：无外部依赖（无 Tailwind / 无 chart 库），纯 HTML + CSS
- **高信息密度**：4 卡片（总览）+ 2 表格（规范元数据 + 功能点进度）
- **状态色编码**：
  - `ok` (绿) = 完成
  - `warn` (amber) = WIP/失败
  - `err` (红) = 失败
- **teal 主色** (`--accent: #0e7c66`)：参考学术配图偏好

## 不在范围内

- 不实现**实时刷新**（如需：每 N 分钟跑一次 render 即可）
- 不实现**图表**（如需：用 Mermaid 内嵌，render.py 加支持）
- 不实现**多语言**（如需：模板加 `{lang}` 占位 + render.py 接受 `--lang` 参数）
