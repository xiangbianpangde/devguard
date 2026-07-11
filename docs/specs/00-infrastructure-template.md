# BDD 规格: 项目基础设施模板

> 更新: 2026-07-11
> 对应规划中各个基础设施文件的创建与验证标准。
> 本文档泛化适用于 STATUS.md / CLAUDE.md / dashboard.html / plan / worklog 等文件的创建检查。
> 更新: 2026-05-30

---

## 功能：项目基础设施文件创建

### 场景 1：创建 CLAUDE.md 项目上下文文件
- 前置条件：仓库已初始化，目录结构已创建
- 操作步骤：
  1. 在项目根目录创建 `CLAUDE.md`
  2. 写入项目概述、目录结构、模块依赖图谱、当前开发状态、关键决策
- 预期结果：Claude 新会话启动时自动读取该文件，了解项目全貌

### 场景 2：创建 STATUS.md 进度仪表盘
- 前置条件：`docs/plan/开发清单.md` 已存在，包含功能点列表
- 操作步骤：
  1. 在项目根目录创建 `STATUS.md`
  2. 按模板格式写入当前进度表（功能点、BDD引用、状态、完成日期）
  3. 写入阻塞项和技术债区域
- 预期结果：打开文件即可看到项目整体进度，所有功能点状态一目了然

### 场景 3：创建 dashboard.html 可视化仪表盘
- 前置条件：`STATUS.md` 已创建且格式正确
- 操作步骤：
  1. 创建 `dashboard.html` 文件
  2. 通过 fetch 读取 `STATUS.md`
  3. 解析 Markdown 表格，渲染进度条和功能卡片
- 预期结果：在浏览器中打开后自动显示项目进度，60秒自动刷新

### 场景 4：空文件处理
- 前置条件：`STATUS.md` 不存在或无法访问
- 操作步骤：
  1. 在浏览器中打开 `dashboard.html`
- 预期结果：显示友好错误提示"无法加载 STATUS.md"，不出现白屏

### 场景 5：一条命令初始化自包含治理基线
- 前置条件：目标目录为空，Python 3.10+ 与 Git 可用
- 操作步骤：
  1. 运行 `python scripts/setup_scaffold.py <目标目录> --profile core --install`
- 预期结果：
  - manifest 中的核心文件全部生成，无未解析模板变量
  - 自动创建隔离虚拟环境、安装依赖并初始化 Git
  - `pre-commit` 与 `commit-msg` 两类 hook 都已安装
  - 若用户已配置 ECC/其他全局 `core.hooksPath`，安装器不得修改全局配置；必须把既有 `pre-commit` / `pre-push` 与项目 Hook 串联，并用本地 `.git/hooks` 保证两套约束都生效
  - 初始化结束前自动执行 fail-closed verify；任何依赖或验证失败都返回非零退出码

### 场景 6：拒绝不安全覆盖与不完整载荷
- 前置条件：目标目录非空，或模板 manifest 引用缺失文件
- 操作步骤：
  1. 不带 `--force` 运行初始化
- 预期结果：
  - 非空目录被拒绝，已有文件不被静默覆盖
  - manifest 源文件缺失时在首次写入前失败
  - `.tmp`、`.bak`、`.pyc` 和 `__pycache__` 不得进入模板载荷

### 场景 7：初始化结果可独立复验
- 前置条件：初始化已经成功
- 操作步骤：
  1. 在源仓库之外运行 `python scripts/setup_scaffold.py <目标目录> --verify --require-hooks`
  2. 在目标目录运行其自带的验证脚本和测试
- 预期结果：目标不依赖源仓库中的脚本或相对路径，验证和测试均通过
  - `--require-hooks` 必须验证本地 `core.hooksPath` 确实指向项目 `.git/hooks`，不能把“Hook 文件存在但 Git 实际忽略”计为通过
