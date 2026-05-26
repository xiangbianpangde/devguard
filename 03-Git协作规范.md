# Git 协作规范

---

## 一、分支策略

### 1.1 常用模型

**Git Flow（推荐大项目）**
```
main         ← 发布分支
├── develop  ← 开发主分支
│   ├── feature/xxx  ← 功能分支
│   └── fix/xxx      ← 修复分支
└── hotfix/xxx       ← 紧急修复分支
```

**GitHub Flow（推荐小项目）**
```
main         ← 随时可发布
└── feature/xxx  ← 所有开发在此
```

### 1.2 分支命名

```
feature/<描述>       新功能
fix/<描述>           Bug 修复
hotfix/<描述>        紧急修复
refactor/<描述>      重构
docs/<描述>          文档
chore/<描述>         工程配置
```

示例：
- `feature/user-login`
- `fix/order-timeout`
- `hotfix/payment-crash`

### 1.3 分支规则
- `main` / `master` 分支禁止直接 push
- 功能分支从 `main` 创建，合并后删除
- 分支命名使用 kebab-case

---

## 二、提交规范

### 2.1 Conventional Commits
```
<type>(<scope>): <description>

[body]

[footer]
```

| type | 说明 |
|------|------|
| feat | 新功能 |
| fix | Bug 修复 |
| refactor | 重构（不改变行为） |
| docs | 文档变更 |
| style | 格式调整（不影响逻辑） |
| test | 测试相关 |
| chore | 构建/依赖/工具变更 |
| perf | 性能优化 |

### 2.2 示例
```
feat(user): add login with OAuth2

- Support Google and GitHub OAuth
- Add session persistence
- Add rate limiting for login attempts

Closes #123
```

### 2.3 提交粒度
- 一个提交做一件事
- 提交信息用中文或英文，保证同项目统一
- 禁止 `WIP`、`fix bug`、`update` 等模糊提交

---

## 三、Commit 最佳实践

### 3.1 提交前
```bash
# 查看变更
git diff

# 查看暂存区
git diff --cached

# 分批提交（不把所有改动混在一次提交）
git add -p
```

### 3.2 保持历史整洁
```bash
# 合并多个小提交为一个（未 push 时）
git rebase -i HEAD~3
```

### 3.3 不要做的事
- 不要提交 `node_modules/`、`__pycache__/`、`.env`
- 不要提交大文件（> 10MB）到仓库
- 不要 `git push --force` 到共享分支

---

## 四、Code Review

### 4.1 提 PR 的人
- PR 描述：做了什么、为什么、怎么验证
- PR 尽量小（< 500 行变更）
- 提交前自己先审查一遍
- 关联对应 Issue

### 4.2 审查的人
- 24 小时内给出反馈
- 区分 "必须改" 和 "建议改"
- 具体指出问题，不笼统说"不好"
- 关注逻辑正确性 > 代码风格

### 4.3 审查清单
- [ ] 逻辑是否正确，边界条件是否覆盖
- [ ] 是否有安全漏洞（SQL注入、XSS等）
- [ ] 是否有性能问题（N+1查询、内存泄漏）
- [ ] 测试是否充分（正常+异常+边界）
- [ ] 是否有遗留的调试代码
- [ ] 命名是否清晰

---

## 五、合并策略

### 5.1 Merge（保留完整历史）
```bash
git checkout main
git merge --no-ff feature/xxx
```
适合：开源项目，需要保留完整历史

### 5.2 Squash（压缩为一个提交）
```bash
git checkout main
git merge --squash feature/xxx
```
适合：功能分支有大量小提交

### 5.3 Rebase（线性历史）
```bash
git checkout feature/xxx
git rebase main
git checkout main
git merge feature/xxx
```
适合：追求干净的线性历史

---

## 六、.gitignore 模板

```gitignore
# 依赖
node_modules/
__pycache__/
*.pyc
venv/
.venv/

# 环境变量
.env
.env.local

# IDE
.vscode/
.idea/
*.swp
*.swo

# 构建产物
dist/
build/
*.log

# 系统
.DS_Store
Thumbs.db
```
