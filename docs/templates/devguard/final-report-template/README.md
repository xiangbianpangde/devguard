# final-report-template — 最终汇报 HTML 模板

## 用途

V1.x 收尾后定型的"高密度学术风 + 大量可视化 + 多交互"汇报模板。后续每次阶段性汇报、收束报告、季度总结都按这个标准出。

**与 `html-report-template/` 的区别**：
- `html-report-template/` 是**自动 dashboard** —— 由 `render.py` 从 `_meta.yaml` + `STATUS.md` 渲染生成，每个 devguard 派生项目 fork
- `final-report-template/` 是**人工撰写的高密度报告** —— 由 AI/开发者按节填充，**带 Mermaid 图 + Tab 切换 + 数字滚动 + 步骤模拟器**，不依赖 Python 渲染

## 风格特征

| 维度 | 选择 | 原因 |
|------|------|------|
| 整体配色 | 期刊式学术风（深红 + 茶色 + teal 辅） | 跨项目稳定偏好：academic figure 风格 |
| 字体 | Serif 标题 + Sans 正文 + Mono 代码 | 学术论文排版范式 |
| 信息密度 | 单页 1200+ 元素（KPI/卡/矩阵/Mermaid/Tab） | "消息密度高、方便理解" 是硬要求 |
| 可视化 | Mermaid 11 图 + ASCII 架构图 5+ + 数字矩阵 6 维度 | 数据/流程/对比三栖呈现 |
| 交互 | Tab 切换 + 数字滚动 + 进度条动画 + 步骤模拟器 | 可点击 = 可理解 = 可记忆 |
| 外部依赖 | 仅 Mermaid CDN (10.9.1) | 离线可改，本地 python http.server 即用 |

## 章节骨架（12 节固定）

1. **§ 00 Executive Summary** — 8 KPI 卡 + 5 维健康度仪表
2. **§ 01 V1 第一版痛点** — 5 个具体崩塌点（红框卡）
3. **§ 02 强制约束范式** — Mermaid 架构图 + 时序图 + commit 模拟器
4. **§ 03 17 规范矩阵** — 表格 + 8 红线 + 落地配置
5. **§ 04 10 钩子流水线** — Mermaid 状态机 + 10 钩子逐个展开
6. **§ 05 CI 5 阶段** — ASCII 流水线 + 工具表
7. **§ 06 收束闸门** — ASCII 四阶段 + V1 vs V1.x 代码对比
8. **§ 07 L4 测试矩阵** — Mermaid 饼/柱/甘特/关系图 + 3 Tab 切换
9. **§ 08 13 收束时间线** — Mermaid 甘特 + 文字时间线
10. **§ 09 双向交叉引用** — ASCII 四方互检图
11. **§ 10 V1 vs V1.x 对比** — Mermaid 雷达/柱状 + 4 架构 × 6 维度矩阵
12. **§ 11 仓库文件图谱** — ASCII 目录树
13. **§ 12 后续路线** — 3 候选卡 + verdict 结尾

## 占位符清单（41 唯一）

详见 `render.py` 顶部的 `PLACEHOLDERS` 列表。8 类：

- **基础**：`{{PROJECT_NAME}}` / `{{REPORT_TITLE}}` / `{{REPORT_SUBTITLE}}` / `{{REPORT_DATE}}`
- **周期**：`{{PERIOD_START}}` / `{{PERIOD_END}}` / `{{GIT_BRANCH}}` / `{{WORKSPACE_STATUS}}`
- **8 KPI**：`{{KPI_{1-8}_NUM}}` / `{{KPI_{1-8}_LBL}}` / `{{KPI_{1-8}_SUB}}`
- **5 健康度**：`{{HEALTH_DIM_{1-5}}}` / `{{HEALTH_DIM_{1-5}_PCT}}`

## 使用流程

### 模式 A：直接复制（推荐，小改即可）

```bash
# 1. 复制模板
cp docs/templates/devguard/final-report-template/template.html docs/reports/<你的报告>.html

# 2. 在编辑器中替换 41 个占位符为实际数据
#    （用 VSCode / Cursor 的全局搜索 {{  → 逐一填值）

# 3. 本地预览
python -m http.server 8080
# 访问 http://localhost:8080/docs/reports/<你的报告>.html
```

### 模式 B：用 render.py + JSON（适合大批量）

```bash
# 1. 准备数据
cat > data.json <<EOF
{
  "PROJECT_NAME": "AgentHub",
  "REPORT_TITLE": "AgentHub V2.x 最终汇报",
  "REPORT_SUBTITLE": "从 V1.0 起步到 V2.x 收尾...",
  "REPORT_DATE": "2026-06-15",
  "KPI_1_NUM": "23",
  "KPI_1_LBL": "规范文档",
  "KPI_1_SUB": "01-08 原始 + 09-23 衍展",
  ...
}
EOF

# 2. 渲染
python docs/templates/devguard/final-report-template/render.py \
    --data data.json \
    --out docs/reports/agenthub_v2x_report.html
```

## 改造规则（修改前必读）

- **改样式** → 改 `<style>` 块内变量（`:root` 顶部），不动具体 class
- **改章节** → 不要新增 <section>，而是把现有 13 节复用 + 改标题
- **改 Mermaid** → 不动 CDN 版本号（10.9.1），可换 `theme` 或 `themeVariables`
- **改 JS** → 三个函数（tab/anim-bar/counter）已写好，**不要重写**；要扩展用 `data-target` / `data-tab` 属性驱动
- **加 mermaid 图** → 复制一个 `.mermaid-wrap` 容器，改 `<div class="cap">` 和 mermaid 源码

## 与 §-06 文档规范的关系

- 本模板**本身**就是 §06 的"高密度报告"实例
- 复制模板到 `docs/reports/` 时，**文件名必须**以 `YYYY-MM-DD_` 开头
- 落盘后必须在 `docs/reports/INDEX.md` 加索引行

## 已知限制

- **Mermaid CDN 需要外网** —— 离线场景下需要本地化 mermaid.min.js
- **IE 不支持** —— Mermaid 10.x 需 Chrome 90+/Edge 90+/Safari 14+
- **打印友好度** —— 当前未做 print CSS 优化，需要 A4 打印时再补
- **大屏 vs 移动** —— >1080px 最佳，<1080px 自动降级为 2 列

## 版本

- **v1.0**（2026-06-08）：V1.x 收尾汇报定型（11 mermaid / 3 tab / 1 sim / 5 anim-bar / 2 counter）
