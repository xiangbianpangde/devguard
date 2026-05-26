# 代码编写规范

---

## 一、命名规范

### 1.1 通用原则
- **见名知意**：名字应准确描述用途，避免 `data`、`info`、`temp` 等模糊命名
- **长度适中**：不过短（`a`、`b`）也不过长（超过 50 字符）
- **一致风格**：同一项目统一命名风格

### 1.2 命名对照表

| 元素 | 风格 | 示例 |
|------|------|------|
| 变量/函数 | camelCase / snake_case | `userName` / `user_name` |
| 类/接口/组件 | PascalCase | `UserService`、`UserCard` |
| 常量 | UPPER_SNAKE | `MAX_RETRY_COUNT` |
| 文件名 | kebab-case / snake_case | `user-service.ts` |
| 布尔变量 | is/has/can 前缀 | `isActive`、`hasPermission` |

### 1.3 文件名
- 用描述性全名，不用缩写（`userProfile.ts` 而不是 `usrPrf.ts`）
- 特殊文件：`index.ts` 作为目录入口，`__tests__` 放测试

---

## 二、代码结构

### 2.1 函数
- 单一职责，一个函数只做一件事
- 长度控制在 50 行以内（复杂逻辑除外）
- 参数不超过 4 个，超过用对象/结构体传参
- 优先纯函数（无副作用，相同输入相同输出）

### 2.2 类
- 遵循单一职责原则
- 成员变量不超过 7 个（超过考虑拆分）
- 公开方法在前，私有方法在后

### 2.3 文件
- 单文件建议不超过 500 行
- 超过考虑拆分为多个模块

---

## 三、注释规范

### 3.1 何时写注释
- **必须写**：复杂算法、业务规则、临时方案（TODO/HACK/FIXME）
- **建议写**：公共接口、关键决策原因
- **不写**：显而易见的代码（`i++ // 自增`）、过时注释

### 3.2 注释格式
```python
# 好：解释为什么
# 使用 B 树索引而非哈希索引，因为需要范围查询
def search_users(age_range):
    ...

# 差：重复代码
# 设置 name 为 "张三"
name = "张三"
```

### 3.3 TODO 标记
```python
# TODO(张三): 2026-06-01 前替换为异步实现
# FIXME: 并发场景下有 data race
# HACK: 临时绕过第三方库 bug，等 2.0 版本修复后移除
```

---

## 四、错误处理

### 4.1 基本原则
- 不要让程序静默失败
- 在最外层统一捕获未处理异常
- 错误信息要包含上下文（什么操作、什么数据、什么原因）

### 4.2 异常粒度
```python
# 好：具体异常
try:
    user = db.find_user(user_id)
except UserNotFoundError:
    return {"error": "用户不存在"}
except DatabaseTimeoutError:
    return {"error": "服务繁忙，请稍后再试"}

# 差：宽泛捕获
try:
    user = db.find_user(user_id)
except Exception:
    return {"error": "出错了"}
```

### 4.3 资源管理
```python
# 好：上下文管理器
with open("file.txt") as f:
    content = f.read()
```

---

## 五、安全规范

### 5.1 敏感信息
- 密钥/Token/密码 **绝对禁止硬编码**
- 数据库连接串通过环境变量注入
- `.env` 文件必须加入 `.gitignore`

### 5.2 输入校验
- 所有外部输入必须校验（API 参数、文件上传、URL 参数）
- 禁止信任客户端传来的任何数据
- 使用白名单校验而非黑名单

### 5.3 SQL 安全
```python
# 好：参数化查询
db.execute("SELECT * FROM users WHERE id = ?", [user_id])
# 差：字符串拼接（SQL 注入风险）
db.execute(f"SELECT * FROM users WHERE id = {user_id}")
```

### 5.4 日志安全
- 日志中**禁止**输出密码、Token、身份证号等敏感信息
- 敏感字段脱敏后输出：`phone=138****1234`

---

## 六、日志规范

### 6.1 日志级别
| 级别 | 用途 | 生产环境 |
|------|------|---------|
| DEBUG | 开发调试信息 | 关闭 |
| INFO | 关键业务流程节点 | 开启 |
| WARN | 可恢复的异常 | 开启 |
| ERROR | 需要关注的错误 | 开启 |

### 6.2 禁止
- 使用 `print()` 替代日志
- 在循环中打印大量日志
- 日志中没有关键上下文

---

## 七、代码审查标准

### 7.1 审查要点
- [ ] 逻辑是否正确
- [ ] 边界条件是否覆盖
- [ ] 是否有安全隐患
- [ ] 是否有性能问题
- [ ] 命名是否清晰
- [ ] 是否有过度设计
- [ ] 测试是否充分

### 7.2 禁入清单
- 被注释掉的代码块（直接删除）
- 调试代码（print、console.log）
- 硬编码的配置值
- 未处理 TODO 标记（除非有期限）
