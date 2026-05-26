# Git 协作规范

> 定义分支策略、提交格式、Code Review 流程和合并规则，确保团队协作有序、历史可追溯。

---

## 适用范围

- **项目类型**：所有使用 Git 的软件项目
- **团队规模**：1-3 人（Trunk-Based）/ 4-10 人（GitHub Flow）/ 10+ 人（Git Flow）
- **托管平台**：GitHub / GitLab / Gitee 均适用

---

## 一、核心原则

### 原则 1：一个提交只做一件事

每个 commit 是独立、可回滚的最小变更单元。Review 者能逐个理解变更意图，出问题时 `git revert` 不影响其他改动。

**为什么**：把不相关的改动塞进一个 commit（如"修复登录 bug + 调整按钮颜色 + 改文档"），Review 者无法聚焦，回滚其中任何一个都会牵连其他。原子提交让 Git 历史成为可检索的变更日志。

### 原则 2：main 分支随时可发布

`main` 分支上的代码应始终处于可部署状态。所有开发在功能分支完成并通过验证后才合入。

**为什么**：如果 main 上积压了未完成的半成品，紧急 hotfix 就无法直接从 main 切分支。保持 main 干净让发布节奏自主可控。

### 原则 3：Review 是质量防线，不是找茬

Code Review 的目标是发现逻辑缺陷、安全隐患和可维护性问题，而非挑剔个人风格。Review 者和提交者是协作关系。

**为什么**：如果 Review 文化变成"挑刺大赛"，开发者会抵触 Review，甚至绕过流程。健康的 Review 文化让双方都学到东西，代码质量自然上升。

---

## 二、具体规则

### 2.1 分支策略

| 模型 | 适用团队 | 说明 |
|------|---------|------|
| Trunk-Based | 1-3 人 | 唯一长期分支为 `main`，功能分支生命周期 < 1 天，合入后立即删除，通过 tag 标记发布 |
| GitHub Flow | 4-10 人 | `main` 为可发布分支，所有开发在 `feature/*` 分支，通过 PR 合入 |
| Git Flow | 10+ 人 | `main` + `develop` 双长期分支，`feature/*` / `release/*` / `hotfix/*` 分离 |

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| `main` 禁止直接 push | 所有变更通过 PR/MR 合入 | 必须 |
| 功能分支从 `main` 创建 | 确保分支起点为最新稳定代码 | 必须 |
| 合并后删除功能分支 | 避免仓库堆积僵尸分支 | 必须 |
| 小团队用 Trunk-Based | 减少分支管理开销，频繁小步合入 | 建议 |

### 2.2 分支命名

```
feature/<描述>    新功能
fix/<描述>        Bug 修复
hotfix/<描述>     紧急修复（直接从 main 切出）
refactor/<描述>   重构
docs/<描述>       文档
chore/<描述>      工程配置（依赖更新、脚本等）
```

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| 使用 kebab-case | `feature/user-login` 而非 `feature/user_login` | 必须 |
| 描述简洁明确 | 名字本身就能说明分支目的 | 必须 |

### 2.3 提交格式（Conventional Commits）

```
<type>(<scope>): <description>

[body]

[footer]
```

| type | 说明 | type | 说明 |
|------|------|------|------|
| feat | 新功能 | fix | Bug 修复 |
| refactor | 重构（不改变行为） | docs | 文档 |
| style | 格式（空格/分号等） | test | 测试 |
| chore | 构建/依赖/工具 | perf | 性能优化 |

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| 格式必须符合 Conventional Commits | `type(scope): description` | 必须 |
| 提交粒度原子化 | 禁止 `WIP`、`fix bug`、`update` 等模糊提交 | 必须 |
| body 解释"为什么" | 描述变更动机和方案，而非重复 diff | 建议 |

### 2.4 提交前检查

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| `git diff` 自查变更 | 确认每个文件都是有意修改 | 必须 |
| `git add -p` 分批暂存 | 不相关改动分不同 commit | 建议 |
| 不提交生成/依赖文件 | `node_modules/`、`__pycache__/`、`.env`、`dist/` | 必须 |
| 不提交大文件 | 单文件 > 10MB 用 Git LFS | 建议 |

### 2.5 Code Review

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| PR 描述含三段信息 | 做了什么、为什么这样做、怎么验证 | 必须 |
| PR 变更量 < 500 行 | 超过拆分为多个 PR | 建议 |
| 提交前自审一遍 | 在自己分支上先做一轮自查 | 必须 |
| 24 小时内给出 Review 反馈 | 避免阻塞他人进度 | 建议 |
| 区分"必须改"和"建议改" | 用 `nit:` 前缀标注非阻塞建议 | 建议 |
| 关注逻辑 > 风格 | 逻辑正确性和安全性优先于命名偏好 | 必须 |
| 至少 1 人 Approve 后合入 | 禁止自己 Approve 自己的 PR | 必须 |

### 2.6 合并策略

| 策略 | 命令 | 适用场景 |
|------|------|---------|
| Squash Merge | `git merge --squash` | 功能分支有大量细碎 commit，压缩为一个有意义的提交 |
| Rebase + Merge | `git rebase main` + `git merge --ff-only` | 追求干净线性历史的小团队 |
| Merge Commit | `git merge --no-ff` | 开源项目或需要保留完整分支历史的场景 |

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| 禁止 `git push --force` 到共享分支 | `main`、`develop` 等共享分支严禁 force push | 必须 |
| 小团队推荐 Squash + Rebase | 保持历史线性可读 | 建议 |

---

## 三、反模式

### ❌ 反模式 1：巨型 PR

```
PR #42: 重构用户模块 + 新增订单功能 + 更新文档 + 修3个bug
变更: +3200 -1800 行，47 个文件
```

**问题**：Review 者无法在合理时间内完成审查，只能草草 Approve 或一直拖着。出问题后无法精确定位是哪个改动引入的。

### ✅ 正确做法：拆分独立 PR

```
PR #42: 提取用户模块公共接口（+200 -150 行，5 文件）
PR #43: 实现用户登录重构（+450 -300 行，8 文件）
PR #44: 新增订单创建功能（+600 -50 行，12 文件）
```

**理由**：每个 PR 聚焦一个主题，Review 者可以在 15 分钟内完成审查。引入 bug 时 `git bisect` 能精确到单个 PR。

---

### ❌ 反模式 2：模糊提交信息

```bash
git commit -m "fix"
git commit -m "update"
git commit -m "WIP"
git commit -m "改了一些东西"
```

**问题**：3 个月后翻阅 Git 历史时完全不知道这些 commit 做了什么。`git log --oneline` 变成天书，回滚/定位问题时只能逐 commit 看 diff。

### ✅ 正确做法：结构化提交

```bash
git commit -m "fix(auth): 修复 token 过期后未自动刷新的问题

原逻辑在 401 返回时只提示用户重新登录，未调用 refresh 接口。
改为：收到 401 后先用 refresh_token 尝试续期，续期失败才跳转登录页。

Closes #128"
```

**理由**：`git log --oneline` 自动成为可读的变更日志。`fix(auth)` 前缀让筛选特定模块的变更只需 `git log --grep="fix(auth)"`。

---

### ❌ 反模式 3：直接 push 到 main

```bash
git checkout main
# 改了代码...
git add .
git commit -m "quick fix"
git push origin main  # 绕过所有流程
```

**问题**：没有 Review 的代码直接进入 main，可能引入安全漏洞、破坏现有功能。如果团队其他人同时也在 main 上工作，直接陷入合并冲突。

### ✅ 正确做法：走 PR 流程

```bash
git checkout -b fix/login-timeout
# 改了代码...
git add -p
git commit -m "fix(auth): 修复登录超时未重试的问题"
git push origin fix/login-timeout
# 在 GitHub/GitLab 上创建 PR，等 Review 后合入
```

**理由**：所有变更经过 Review，任何合并到 main 的代码都有第二双眼睛看过。即使只有一个人开发，PR 流程也迫使自己重新审视改动。

---

## 四、示例

### 场景 1：新功能开发的完整流程

**需求**：为博客系统新增"文章收藏"功能。

| 步骤 | 命令 | 说明 |
|------|------|------|
| 1. 从 main 切分支 | `git checkout -b feature/article-bookmark` | 起点最新，分支名清晰 |
| 2. 开发 + 原子提交 | `git commit -m "feat(article): 新增收藏数据模型"` → `git commit -m "feat(article): 实现收藏/取消收藏 API"` | 两个独立逻辑分开提交 |
| 3. 推送前自查 | `git diff main...feature/article-bookmark` | 确认没有无关改动混入 |
| 4. 创建 PR | PR 描述：做了什么（收藏功能）、为什么（用户需求 #56）、怎么验证（`npm test` + 手动测试 3 个场景） | Review 者一目了然 |
| 5. Review 后 Squash Merge | `git merge --squash feature/article-bookmark` | 两个 commit 压缩为一个有意义的提交 |
| 6. 删除分支 | `git branch -d feature/article-bookmark` | 保持仓库整洁 |

### 场景 2：紧急 Hotfix

**需求**：生产环境支付回调失败，需紧急修复。

| | 反例 | 正例 |
|---|------|------|
| 做法 | 直接在 main 上改代码，`git push --force` | `git checkout -b hotfix/payment-callback main` → 修复 → PR → 合入 → 同步回 develop |
| 说明 | force push 覆盖了别人的提交，引发更大的事故 | hotfix 分支从 main 切出，修复后通过正常流程合入，再 cherry-pick 或 merge 到 develop，确保两边的修复都生效 |

---

## 五、工具推荐

| 工具 | 用途 | 推荐度 |
|------|------|--------|
| Commitlint | CI 中校验 commit message 格式 | 推荐 |
| husky + lint-staged | 提交前自动运行 lint/format | 推荐 |
| gh / glab CLI | 命令行创建 PR、查看 Review 状态 | 可选 |
| GitLens (VS Code) | 行级 blame、历史可视化 | 可选 |
| conventional-changelog | 从 commit 历史自动生成 CHANGELOG | 可选 |

---

## 六、检查清单

- [ ] 是否从最新的 `main` 创建了功能分支？
- [ ] 分支名是否符合 `feature/xxx` / `fix/xxx` 格式？
- [ ] commit message 是否符合 Conventional Commits 格式？
- [ ] 每个 commit 是否只做了一件事？
- [ ] PR 描述是否包含：做了什么、为什么、怎么验证？
- [ ] PR 变更量是否控制在 500 行以内？
- [ ] 是否有遗留的 `WIP` commit？
- [ ] 是否有人 Review 并通过了（至少 1 Approve）？
- [ ] 合并后是否删除了功能分支？
- [ ] 是否避免了 `git push --force` 到共享分支？

---

## 更新记录

| 日期 | 版本 | 变更说明 |
|------|------|---------|
| 2026-05-26 | v1.0 | 按统一模板改造：新增核心原则（为什么）、反模式（3组）、完整场景示例、工具推荐、检查清单（10项） |
