# API 设计规范

---

## 一、RESTful 设计

### 1.1 URL 命名

```
GET    /api/users           # 获取列表
GET    /api/users/:id       # 获取详情
POST   /api/users           # 创建
PUT    /api/users/:id       # 全量更新
PATCH  /api/users/:id       # 部分更新
DELETE /api/users/:id       # 删除
```

### 1.2 命名规则
- 使用名词复数：`/users` 而不是 `/getUser`
- 层级关系：`/users/:id/orders`
- 使用 kebab-case：`/user-profiles`（如必须用多词）
- 不使用动词：用 `POST /users` 而不是 `POST /createUser`

### 1.3 分页、过滤、排序

```
GET /api/users?page=1&page_size=20
GET /api/users?status=active&role=admin
GET /api/users?sort_by=created_at&sort_order=desc
GET /api/users?search=张三
```

---

## 二、请求与响应

### 2.1 统一响应格式

**成功**
```json
{
  "code": 0,
  "message": "ok",
  "data": { ... }
}
```

**列表**
```json
{
  "code": 0,
  "message": "ok",
  "data": {
    "items": [...],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

**错误**
```json
{
  "code": 40001,
  "message": "参数错误：用户名不能为空",
  "data": null
}
```

### 2.2 HTTP 状态码

| 状态码 | 含义 | 使用场景 |
|--------|------|---------|
| 200 | OK | 请求成功 |
| 201 | Created | 创建成功 |
| 204 | No Content | 删除成功 |
| 400 | Bad Request | 参数错误 |
| 401 | Unauthorized | 未认证 |
| 403 | Forbidden | 无权限 |
| 404 | Not Found | 资源不存在 |
| 409 | Conflict | 资源冲突（重复创建） |
| 422 | Unprocessable Entity | 语义错误 |
| 429 | Too Many Requests | 频率限制 |
| 500 | Internal Server Error | 服务器内部错误 |

### 2.3 错误码设计

```
格式: <模块码><错误类型码>

模块码:
  10xxx - 通用
  20xxx - 用户
  30xxx - 订单
  40xxx - 商品

错误类型:
  x01 - 参数错误
  x02 - 资源不存在
  x03 - 权限不足
  x04 - 业务规则限制
```

---

## 三、版本管理

### 3.1 URL 版本（推荐）
```
GET /api/v1/users
GET /api/v2/users
```

### 3.2 Header 版本
```
GET /api/users
Accept: application/vnd.company.v2+json
```

### 3.3 版本策略
- 主版本号变化表示不兼容变更
- 保持至少 2 个大版本的兼容期
- 旧版本废弃前给足迁移时间

---

## 四、安全

### 4.1 认证
```
Authorization: Bearer <token>
```

### 4.2 防护
- 所有接口默认需要认证（除非明确标为公开）
- 敏感操作需要二次确认
- 实施速率限制（60 req/min）
- 输入参数做严格校验

### 4.3 CORS
```json
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, POST, PUT, DELETE
Access-Control-Allow-Headers: Content-Type, Authorization
```

---

## 五、接口文档

### 5.1 每个接口应包含
- 路径和方法
- 请求参数（Query/Body/Path）
- 响应示例（成功 + 失败）
- 认证要求
- 错误码说明

### 5.2 推荐工具
- OpenAPI (Swagger)
- Postman Collection
- Apifox
