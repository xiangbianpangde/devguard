# API 设计规范

> 定义 RESTful API 的 URL 设计、请求响应格式、错误码体系、版本管理和安全策略，确保接口一致、可预测、易于集成。

---

## 适用范围

- **项目类型**：所有提供 HTTP API 的服务（后端/微服务/BFF）
- **技术栈**：语言无关，RESTful 风格为主
- **团队规模**：1 人以上均适用（接口是团队间的契约）

---

## 一、核心原则

### 原则 1：资源导向，而非操作导向

API 的 URL 表达"对什么资源做什么操作"，而非"执行什么函数"。用 HTTP 方法表达动作，用名词表达资源。

**为什么**：操作导向的 URL（如 `/getUser`、`/createOrder`）每新增一个操作就要加一个新路径，最终 URL 列表和函数列表一样长。资源导向让 URL 数量 = 资源类型数，HTTP 方法组合出全部操作，接口集合小而稳定。

### 原则 2：约定优于配置

团队内统一响应格式、错误码、分页参数命名。调用方一旦对接过一个接口，其他接口都是同一种模式。

**为什么**：如果每个接口用不同的响应结构（有时 `data` 有时 `result`，有时 `code: 0` 有时 `success: true`），前端需要为每个接口写定制解析逻辑。统一约定让前端可以用一个拦截器处理所有请求。

### 原则 3：向后兼容是底线

API 的新版本不能破坏已有调用方的行为。新增字段可以，删除/重命名字段不行。废弃接口需提前通知并给出迁移时间。

**为什么**：API 的调用方（前端、第三方、其他服务）有自己的发布节奏。不兼容变更意味着所有调用方必须与你同步升级，这在微服务架构中是不可能的。

---

## 二、具体规则

### 2.1 URL 设计

```
GET    /api/v1/users              # 获取用户列表
GET    /api/v1/users/:id          # 获取单个用户
POST   /api/v1/users              # 创建用户
PUT    /api/v1/users/:id          # 全量更新用户
PATCH  /api/v1/users/:id          # 部分更新用户
DELETE /api/v1/users/:id          # 删除用户

# 子资源
GET    /api/v1/users/:id/orders   # 某用户的订单列表
```

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| 资源名用名词复数 | `/users` 而非 `/getUser` 或 `/user` | 必须 |
| 用 HTTP 方法表达动作 | `POST /users` 创建，`DELETE /users/:id` 删除 | 必须 |
| URL 使用 kebab-case | `/user-profiles` 而非 `/userProfiles` 或 `/user_profiles` | 必须 |
| 层级不超过 3 层 | `/a/:id/b/:id/c` 可接受，`/a/:id/b/:id/c/:id/d` 需重构 | 建议 |
| 避免动词在 URL 中 | 用 `POST /orders/:id/cancel` 而非 `/cancelOrder`（RPC 风格特殊操作例外） | 建议 |

### 2.2 请求与响应格式

**统一成功响应**：

```json
{
  "code": 0,
  "message": "ok",
  "data": { ... }
}
```

**统一列表响应**：

```json
{
  "code": 0,
  "data": {
    "items": [ ... ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

**统一错误响应**：

```json
{
  "code": 40001,
  "message": "参数错误：缺少必填字段 email",
  "data": null
}
```

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| 统一外层结构 | 所有响应含 `code`、`message`、`data` 三个字段 | 必须 |
| `code: 0` 表示成功 | 非 0 表示错误，前端统一拦截 | 必须 |
| 列表返回 total | 前端需要知道总数来渲染分页组件 | 必须 |

### 2.3 HTTP 状态码

| 状态码 | 含义 | 使用场景 |
|--------|------|---------|
| 200 | OK | GET/PUT/PATCH 成功 |
| 201 | Created | POST 创建资源成功 |
| 204 | No Content | DELETE 成功，无响应体 |
| 400 | Bad Request | 请求参数不合法 |
| 401 | Unauthorized | 未认证或 Token 过期 |
| 403 | Forbidden | 已认证但权限不足 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突（如重复创建） |
| 422 | Unprocessable Entity | 参数格式正确但语义错误（如余额不足） |
| 429 | Too Many Requests | 触发限流 |
| 500 | Internal Server Error | 服务端未知错误 |

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| HTTP 状态码与 body code 一致 | 不要返回 HTTP 200 + body `code: 50000` | 必须 |
| 业务错误用 4xx 系列 | 用户能通过修改请求解决的错误 | 必须 |

### 2.4 错误码设计

格式：`<HTTP 状态码><2 位模块码><2 位具体错误>`

| 错误码 | HTTP | 含义 |
|--------|------|------|
| 40001 | 400 | 缺少必填参数 |
| 40002 | 400 | 参数格式错误 |
| 40101 | 401 | Token 过期 |
| 40102 | 401 | Token 无效 |
| 40301 | 403 | 无此资源访问权限 |
| 40401 | 404 | 用户不存在 |
| 40402 | 404 | 订单不存在 |
| 40901 | 409 | 用户名已存在 |
| 42201 | 422 | 库存不足 |
| 42901 | 429 | 请求频率超限 |
| 50001 | 500 | 数据库连接失败 |
| 50002 | 500 | 第三方服务超时 |

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| 每种错误有唯一错误码 | 前端可根据错误码做差异化处理 | 必须 |
| 错误码不可重复使用 | 废弃的错误码保留在文档中，不分配给新错误 | 必须 |
| message 对开发者友好 | 包含具体字段名和期望格式，而非"参数错误" | 必须 |

### 2.5 分页、排序、过滤

```
GET /api/v1/users?page=1&page_size=20
GET /api/v1/users?status=active&role=admin
GET /api/v1/users?sort_by=created_at&sort_order=desc
GET /api/v1/users?search=张三
```

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| 分页参数统一 | `page` + `page_size`，或 `offset` + `limit`，全项目选一种 | 必须 |
| page 从 1 开始 | 不是从 0，与用户直觉一致 | 必须 |
| page_size 设上限 | 默认 20，最大 100 | 必须 |
| 排序用 `sort_by` + `sort_order` | `sort_order` 取 `asc` / `desc` | 建议 |
| 过滤用查询参数 | `?status=active` 而非 `/users/active` | 必须 |

### 2.6 版本管理

| 策略 | 示例 | 适用场景 |
|------|------|---------|
| URL 路径版本（推荐） | `/api/v1/users`、`/api/v2/users` | 大多数场景，简单直观 |
| Header 版本 | `Accept: application/vnd.api.v2+json` | 需要细粒度内容协商 |
| Query 参数版本 | `/api/users?version=2` | 不推荐（容易被忽略） |

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| 主版本号变化 = 不兼容变更 | `v1` → `v2` 表示破坏性升级 | 必须 |
| 同时维护至少 2 个大版本 | 给调用方至少一个版本的缓冲期 | 建议 |
| 废弃接口提前公告 | 标注 `@deprecated`，给出迁移指引和截止日期 | 建议 |

### 2.7 安全

| 规则 | 说明 | 强制程度 |
|------|------|---------|
| 认证用 Bearer Token | `Authorization: Bearer <token>` | 必须 |
| 所有接口默认需认证 | 公开接口（登录/注册）显式标注例外 | 必须 |
| 敏感操作需二次确认 | 删除/转账/修改权限等需额外验证 | 建议 |
| 速率限制 | 每用户 60 req/min，响应头返回 `X-RateLimit-*` | 建议 |
| 输入参数严格校验 | 类型/长度/格式/范围，白名单优先 | 必须 |
| CORS 白名单 | 只允许已知域名的跨域请求 | 必须 |

---

## 三、反模式

### ❌ 反模式 1：动词 URL

```
GET  /api/getUserList
POST /api/createOrder
POST /api/deleteUser
```

**问题**：URL 里包含动词 `get`/`create`/`delete`，而 HTTP 方法已经表达了这些语义。结果一个简单的 CRUD 资源需要 4 个完全不同的 URL。

### ✅ 正确做法：资源 + HTTP 方法

```
GET    /api/users          # 获取列表
POST   /api/users          # 创建
GET    /api/users/:id      # 获取详情
DELETE /api/users/:id      # 删除
```

**理由**：URL 只表达"用户"这个资源，HTTP 方法表达操作。调用方看到 `/api/users` 就知道用 GET 查列表、POST 创建，不需要查文档。

---

### ❌ 反模式 2：响应格式不一致

```json
// 接口 A 成功响应
{ "success": true, "result": { "id": 1, "name": "张三" } }

// 接口 B 成功响应
{ "code": 200, "data": { "id": 1, "name": "张三" } }

// 接口 A 错误响应
{ "error": "用户不存在" }

// 接口 B 错误响应
{ "code": 404, "message": "Not Found" }
```

**问题**：前端需要为每个接口写不同的解析逻辑。错误处理无法用统一的拦截器，每个调用处都要判断不同的字段。

### ✅ 正确做法：统一外层结构

```json
// 所有成功响应
{ "code": 0, "message": "ok", "data": { ... } }

// 所有错误响应
{ "code": 40401, "message": "用户不存在", "data": null }
```

**理由**：前端一个 axios/fetch 拦截器处理所有接口：`code === 0` 则取 `data`，否则根据 `code` 展示对应提示。

---

### ❌ 反模式 3：不兼容的版本升级

```diff
# v1 接口
GET /api/v1/users/:id
- Response: { "name": "张三", "age": 28 }

# v2 接口（"顺便"把 name 改成 fullName）
GET /api/v2/users/:id
- Response: { "fullName": "张三", "age": 28 }
```

**问题**：调用 v1 的前端还没升级，v1 接口却被悄悄改了字段名，导致生产事故。

### ✅ 正确做法：新旧版本共存

```
# v1（保持不变）
GET /api/v1/users/:id  →  { "name": "张三", "age": 28 }

# v2（新增字段，旧字段保留）
GET /api/v2/users/:id  →  { "name": "张三", "fullName": "张三", "age": 28, "email": "..." }
```

**理由**：新版本增加字段，不删除旧字段。等所有调用方迁移到 v2 后（监控 v1 调用量为 0），再下线 v1 并清理旧字段。

---

## 四、示例

### 场景 1：订单列表接口设计

**需求**：客户端需要分页查询订单，支持按状态过滤和按时间排序。

```
GET /api/v1/orders?page=1&page_size=20&status=pending&sort_by=created_at&sort_order=desc
```

**响应**：

```json
{
  "code": 0,
  "data": {
    "items": [
      { "id": "ord_001", "status": "pending", "amount": 99.00, "created_at": "2026-05-26T10:00:00Z" }
    ],
    "total": 1,
    "page": 1,
    "page_size": 20
  }
}
```

| | 反例 | 正例 |
|---|------|------|
| URL | `/api/getOrderList?p=1&s=20&st=pending` | `/api/v1/orders?page=1&page_size=20&status=pending&sort_by=created_at&sort_order=desc` |
| 说明 | 动词 URL + 缩写参数，新人看不懂 | 资源 URL + 自解释参数，无需文档也能猜出用法 |

### 场景 2：创建资源返回完整对象

**需求**：前端创建订单后需要立即展示订单详情。

| | 反例 | 正例 |
|---|------|------|
| 响应 | `POST /orders` 返回 `{ "code": 0, "data": { "id": "ord_001" } }` | 返回 `{ "code": 0, "data": { "id": "ord_001", "status": "pending", ...所有字段 } }` |
| 说明 | 前端拿到 id 后要再发一次 GET 请求获取详情，多一次网络往返 | 一次请求返回全部数据，前端直接渲染；减少延迟，降低服务端负载 |

---

## 五、工具推荐

| 工具 | 用途 | 推荐度 |
|------|------|--------|
| OpenAPI 3.x (Swagger) | API 文档自动生成 + 交互式调试 | 推荐 |
| Postman / Apifox | 接口测试 + 团队协作 + Mock 服务 | 推荐 |
| Spectral | OpenAPI 规范 lint，检查命名/格式一致性 | 可选 |
| Pact | 消费者驱动契约测试（CDC） | 可选 |

---

## 六、检查清单

- [ ] URL 是否使用名词复数 + kebab-case？（没有动词、没有驼峰）
- [ ] HTTP 方法是否正确表达了操作意图？（GET 读/POST 创建/PUT 全量更新/PATCH 部分更新/DELETE 删除）
- [ ] 所有响应是否使用统一外层结构？（`code` + `message` + `data`）
- [ ] 错误码是否唯一且不可重复使用？
- [ ] 分页参数是否统一（`page` + `page_size`）？
- [ ] 是否所有接口默认需要认证？
- [ ] 输入参数是否都做了校验（类型/长度/范围）？
- [ ] 是否避免了不兼容的字段删除/重命名？
- [ ] 速率限制是否配置？
- [ ] CORS 是否只允许已知域名？

---

## 更新记录

| 日期 | 版本 | 变更说明 |
|------|------|---------|
| 2026-05-26 | v1.0 | 按统一模板改造：新增核心原则（为什么）、反模式（3组）、完整场景示例、工具推荐、检查清单（10项） |
