# AI 协作开发流程

> 适用场景：使用 AI（Claude/DeepSeek/GPT 等）作为主力开发者的项目。
> 核心理念：先计划后开发、BDD 驱动迭代、可视化验证、持续回顾。

---

## 角色分工

| 角色 | 模型 | 职责 |
|------|------|------|
| **执行者** | Claude | 写代码、修 bug、跑测试、生成文档 |
| **审查者** | DeepSeek | 读 diff、对照计划检查、发现遗漏和风险 |
| **架构师 + 开发** | Opus | 架构设计、开发计划审查、代码审查 |
| **决策者** | 我 | 验收功能、决定方向调整、拍板关键选择 |

> 你只在审查者标记的差异点和高风险项上做决策，不做逐行审查。

---

## 文件体系

```
project/
├── docs/
│   ├── research/          # 调研文档
│   ├── specs/             # BDD 功能规格
│   └── decisions/         # 架构决策记录 (ADR)
├── plan/                  # 计划提纲 + 实时进度
│   ├── 背景.md            # 流程笔记与背景分析
│   └── 开发清单.md         # 功能点开发计划清单
├── STATUS.md              # 当前状态仪表盘
├── dashboard.html         # 可视化仪表盘
├── CLAUDE.md              # Claude 项目上下文（代码库图谱、当前进度）[新会话自动加载]
├── worklogs/              # 工作日志
│   └── YYYY-MM-DD_描述.md
└── src/                   # 代码
```

---

## 第零步：调研

在写任何计划之前，先做调研并落库。确保 `docs/research/` 目录已存在。

**产出：**
- `docs/research/` 目录下的调研文档
- 每份文档包含：信息来源、关键结论、对项目的启示

**原则：**
- 调研产物必须落盘，不留在对话里
- 调研结论与计划条目一一对应（每个计划项都能追溯到调研来源）

---

## 第一步：编写计划

### 1.1 流程笔记
我先写流程式笔记，理解整体流程。输出到 `plan/背景.md`。

### 1.2 功能拆分
以功能为粒度拆分检查点，每个功能点满足：
- 独立可测试
- 独立可演示
- 不超过一个对话轮次的开发量

### 1.3 BDD 规格
用统一模板为每个功能点编写 BDD。存放在 `docs/specs/`。

**BDD 模板：**
```markdown
## 功能：{功能名称}

### 场景 1：{场景描述}
- 前置条件：
- 操作步骤：
  1.
  2.
- 预期结果：

### 场景 2：{异常场景}
- 前置条件：
- 操作步骤：
- 预期结果：
```

### 1.4 技术选型
我使用 DeepSeek 为每个 BDD 场景标注实现路径（一句话即可）：
```
场景 1 实现路径：使用 SQLAlchemy ORM 查询 + FastAPI endpoint
场景 2 实现路径：Pydantic validator + 统一异常处理器
```

### 1.5 我与 DeepSeek 讨论完善

- 将粗浅想法与 DeepSeek 讨论，完善设计
- **硬终止条件：最多两轮讨论**，两轮后必须落地为可执行的计划条目
- 遇到能力边界外的概念（如用户画像→认知模型），先让 DeepSeek 解释实现路径，再决定是否纳入本期

### 1.6 生成计划提纲

我让 DeepSeek 根据以上产出编写 `plan/开发清单.md`，包含：
- 功能点列表（按优先级排序）
- 每个功能点的 BDD 引用
- 预估轮次
- 依赖关系

### 1.7 系统模拟运行

* 对计划进行模拟运行，检查是否存在设计问题

### 1.8 交叉审查（Opus）

我将计划交给 Opus 审查，**同时附上当前仓库状态**（目录树 + 关键文件头）。
检查点：

- 执行层面：计划是否可落地
- 架构层面：是否有设计缺陷
- 根据审查结果生成开发计划文件（`plan/开发清单.md` + `STATUS.md`）
- 对优化后的计划进行第二次系统模拟运行，检查是否存在设计问题

### 1.9 创建基础设施

```bash
git init
# 单人项目直接 main 分支，每个功能点完成后打 tag
# 多人协作使用 feature 分支

# 创建文件骨架
mkdir -p docs/research docs/specs docs/decisions worklogs plan
touch plan/背景.md plan/开发清单.md STATUS.md

# 初始化 CLAUDE.md — 代码库图谱，每个新会话自动加载
cat > CLAUDE.md << 'EOF'
# {项目名} — Claude 项目上下文

> 本文件在新会话中自动加载。每次功能点完成后更新。

## 目录结构
<!-- 由脚本自动生成或手动维护 -->

## 模块依赖图谱
<!-- 描述核心模块及其关系，避免重复造轮子 -->

## 当前开发状态
<!-- 引用 STATUS.md 中的当前功能点 -->

## 关键决策
<!-- 引用 docs/decisions/ 中的 ADR -->
EOF
```

`STATUS.md` 模板：
```markdown
# 项目状态

> 更新: YYYY-MM-DD

## 当前进度
| 功能点 | BDD | 状态 | 完成日期 |
|--------|-----|------|---------|
| 用户登录 | specs/login.md | 进行中 | - |
| 订单创建 | specs/order.md | 待开始 | - |

## 阻塞项
（无）

## 技术债
（无）
```

`dashboard.html` 模板：一个自刷新 HTML 文件，通过读取 `STATUS.md` 渲染进度条和功能卡片。脚本从 Git log + `plan/开发清单.md` 自动生成。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta http-equiv="refresh" content="60">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>项目仪表盘</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: #0d1117; color: #c9d1d9; padding: 2rem;
      max-width: 900px; margin: 0 auto;
    }
    h1 { color: #58a6ff; margin-bottom: 0.5rem; }
    .updated { color: #8b949e; font-size: 0.85rem; margin-bottom: 2rem; }
    .card {
      background: #161b22; border: 1px solid #30363d;
      border-radius: 8px; padding: 1.25rem; margin-bottom: 1rem;
    }
    .card-header {
      display: flex; justify-content: space-between; align-items: center;
      margin-bottom: 0.75rem;
    }
    .card-title { font-weight: 600; font-size: 1.1rem; }
    .badge {
      padding: 0.2rem 0.6rem; border-radius: 12px;
      font-size: 0.75rem; font-weight: 600;
    }
    .badge-done { background: #1b3a2d; color: #3fb950; }
    .badge-active { background: #1a2e3f; color: #58a6ff; }
    .badge-pending { background: #30363d; color: #8b949e; }
    .badge-blocked { background: #3a1b1b; color: #f85149; }
    .progress-bar {
      width: 100%; height: 8px; background: #21262d;
      border-radius: 4px; overflow: hidden; margin: 0.5rem 0;
    }
    .progress-fill {
      height: 100%; background: linear-gradient(90deg, #238636, #3fb950);
      border-radius: 4px; transition: width 0.3s;
    }
    .meta { color: #8b949e; font-size: 0.8rem; margin-top: 0.5rem; }
    .blocked-section { margin-top: 2rem; }
    .blocked-section h2 { color: #f85149; margin-bottom: 1rem; }
    .tech-debt { color: #d2991d; }
  </style>
</head>
<body>
  <h1>📊 项目仪表盘</h1>
  <p class="updated">最后更新: <span id="update-time">--</span></p>

  <div class="card" style="margin-bottom: 2rem;">
    <div class="card-header">
      <span class="card-title">总体进度</span>
      <span id="overall-percent">0%</span>
    </div>
    <div class="progress-bar">
      <div class="progress-fill" id="overall-bar" style="width: 0%"></div>
    </div>
  </div>

  <div id="feature-cards"></div>

  <div class="blocked-section" id="blocked-section" style="display: none;">
    <h2>🚫 阻塞项</h2>
    <div id="blocked-list"></div>
  </div>

  <div class="blocked-section" id="debt-section" style="display: none;">
    <h2 class="tech-debt">⚠️ 技术债</h2>
    <div id="debt-list"></div>
  </div>

  <script>
    async function loadStatus() {
      try {
        const res = await fetch('STATUS.md');
        const text = await res.text();
        render(text);
        document.getElementById('update-time').textContent =
          new Date().toLocaleString('zh-CN');
      } catch (e) {
        document.getElementById('feature-cards').innerHTML =
          '<div class="card"><p>无法加载 STATUS.md</p></div>';
      }
    }

    function render(md) {
      // 解析 STATUS.md 表格
      const lines = md.split('\n');
      const features = [];
      let blocked = [];
      let debt = [];
      let inTable = false, inBlocked = false, inDebt = false;

      for (const line of lines) {
        if (line.startsWith('| 功能点')) { inTable = true; continue; }
        if (inTable && line.startsWith('|') && !line.includes('---')) {
          const cols = line.split('|').map(s => s.trim()).filter(Boolean);
          if (cols.length >= 4) {
            features.push({
              name: cols[0], bdd: cols[1], status: cols[2], date: cols[3]
            });
          }
        }
        if (line.startsWith('## 阻塞项')) { inTable = false; inBlocked = true; continue; }
        if (line.startsWith('## 技术债')) { inBlocked = false; inDebt = true; continue; }
        if (inBlocked && line.startsWith('- ')) blocked.push(line.slice(2));
        if (inDebt && line.startsWith('- ')) debt.push(line.slice(2));
        if (line.startsWith('##') && inBlocked) inBlocked = false;
        if (line.startsWith('##') && inDebt) inDebt = false;
      }

      // 总体进度
      const done = features.filter(f => f.status === '已完成').length;
      const total = features.length;
      const pct = total > 0 ? Math.round(done / total * 100) : 0;
      document.getElementById('overall-percent').textContent = pct + '%';
      document.getElementById('overall-bar').style.width = pct + '%';

      // 功能卡片
      const container = document.getElementById('feature-cards');
      container.innerHTML = features.map(f => {
        const badgeClass = f.status === '已完成' ? 'badge-done'
          : f.status === '进行中' ? 'badge-active'
          : f.status === '阻塞' ? 'badge-blocked'
          : 'badge-pending';
        return `<div class="card">
          <div class="card-header">
            <span class="card-title">${f.name}</span>
            <span class="badge ${badgeClass}">${f.status}</span>
          </div>
          <p class="meta">BDD: ${f.bdd}${f.date !== '-' ? ' · 完成: ' + f.date : ''}</p>
        </div>`;
      }).join('');

      // 阻塞项
      if (blocked.some(b => b !== '（无）' && b !== '')) {
        document.getElementById('blocked-section').style.display = 'block';
        document.getElementById('blocked-list').innerHTML =
          blocked.filter(b => b.trim()).map(b => `<div class="card"><p>${b}</p></div>`).join('');
      }

      // 技术债
      if (debt.some(d => d !== '（无）' && d !== '')) {
        document.getElementById('debt-section').style.display = 'block';
        document.getElementById('debt-list').innerHTML =
          debt.filter(d => d.trim()).map(d => `<div class="card"><p>${d}</p></div>`).join('');
      }
    }

    loadStatus();
  </script>
</body>
</html>
```

---

## 第二步：迭代开发

### 开发循环（每个功能点）

```
1. Claude 实现
   ↓
2. 可视化验证（必须）
   ↓
3. DeepSeek 审查 diff
   ↓
4. 你确认差异点（只看审查标记的）
   ↓
5. 更新 plan/ + worklog + STATUS.md
   ↓
6. Git commit + tag
   ↓
7. 3 分钟回顾
   ↓
   → 回到 1，开始下一个功能点
```

### 2.1 Claude 实现

**前置步骤（每个功能点开始前）：**

1. **扫描仓库**：读取当前目录树和关键模块头，确认已有代码结构
2. **更新代码库图谱**：将模块依赖关系写入 `CLAUDE.md`（新会话自动加载，避免遗忘已有模块）
3. **标记可复用点**：在 `CLAUDE.md` 中标注当前功能可复用的已有模块

**开发规则：**

- 一次只做**一个功能点**，不做范围蔓延
- 代码产出包含测试
- 完成后立即跑验证命令
- 开发完成后更新 `CLAUDE.md` 的目录结构和模块图谱

### 2.2 可视化验证（硬性要求）

**每一个功能点必须有可视化产出**，哪怕是对数据库的，我和 Opus 都要做：

| 功能类型 | 可视化方式 |
|---------|-----------|
| 前端页面 | 浏览器截图 |
| API 接口 | Swagger 截图 / curl 输出 |
| 数据库变更 | 表结构图 / 查询结果截图 |
| 算法逻辑 | console 输出 / 日志截图 |
| CLI 工具 | 终端运行截图 |

### 2.3 DeepSeek 审查
将 `git diff` 发给 DeepSeek，附带 `plan` 中的当前功能点描述。
审查清单：

- [ ] 是否实现了 BDD 中所有场景
- [ ] 是否有越界变更（改了不该改的）
- [ ] 是否与已有模块功能重复（对照 `CLAUDE.md` 的代码库图谱）
- [ ] 是否有安全隐患
- [ ] 是否有遗留调试代码

### 2.4 你确认
只看 DeepSeek 标记的**差异点**和**高风险项**。正常情况下无需介入。

### 2.5 更新记录
- `plan/开发清单.md`：当前功能点标记完成，修正后续估算
- `worklogs/YYYY-MM-DD_描述.md`：记录做了什么、遇到的问题、给下一位的交接
- `STATUS.md`：更新进度表

### 2.6 Git 提交
```bash
git add .
git commit -m "feat(xxx): 完成{功能点名称}"
git tag v0.1.0  # 里程碑时打 tag
```

### 2.7 回顾（3 分钟）
- 计划估算 vs 实际耗时（修正后续）
- 是否有意外发现（更新 `docs/research/`）
- 是否留下技术债（记录到 `STATUS.md` 的技术债区）

---

## 完整流程总览

```
零、调研
  └─ 产出 → docs/research/

一、计划
  1. 流程笔记 (plan/背景.md)
  2. 功能拆分 (plan/开发清单.md)
  3. BDD 规格 (docs/specs/)
  4. 技术选型 (plan/开发清单.md 中标注)
  5. DeepSeek 讨论完善 (≤ 2 轮)
  6. DeepSeek 生成计划提纲 (plan/开发清单.md)
  7. Opus 交叉审查 (附仓库状态)
  8. 创建基础设施 (git/STATUS/日志/仪表盘)

二、开发（功能点循环）
  ┌─────────────────────────────────┐
  │ 1. Claude 实现                    │
  │ 2. 可视化验证（必须）               │
  │ 3. DeepSeek 审查 diff              │
  │ 4. 你确认差异点                     │
  │ 5. 更新 plan/ + worklog + STATUS  │
  │ 6. Git commit + tag               │
  │ 7. 3 分钟回顾                      │
  └─────────────────────────────────┘
            ↓
     下一个功能点
```

---

## 核心原则

2. **不黑盒** — 每个功能点必须可视化验证，不开盲盒
3. **不断档** — 每个功能点完成时更新所有记录文件，下一个人（或明天的你）能无缝接手
4. **不拖欠** — 回顾中发现的技术债记录到 STATUS，下个循环优先处理
