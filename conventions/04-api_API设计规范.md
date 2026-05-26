# API 设计规范

---

## 一、RESTful 设计

### 1.1 URL 命名
```
GET    /api/users           # 列表
GET    /api/users/:id       # 详情
POST   /api/users           # 创建
PUT    /api/users/:id       # 全量更新
PATCH  /api/users/:id       # 部分更新
DELETE /api/users/:id       # 删除
```

### 1.2 命名规则
- 名词复数：`/users` 而不是 `/getUser`
- 层级关系：`/users/:id/orders`
- kebab-case：`/user-profiles`
- 不用动词：`POST /users` 而不是 `POST /createUser`

### 1.3 分页过滤排序
```
GET /api/users?page=1&page_size=20
GET /api/users?status=active&role=admin
GET /api/users?sort_by=created_at&sort_order=desc
GET /api/users?search=张三
```

---

## 二、请求与响应

### 2.1 统一格式
**成功**: `{"code":0,"message":"ok","data":{...}}`
**列表**: `{"code":0,"data":{"items":[...],"total":100,"page":1,"page_size":20}}`
**错误**: `{"code":40001,"message":"参数错误","data":null}`

### 2.2 HTTP 状态码
| 码 | 含义 | 码 | 含义 |
|----|------|----|------|
| 200 | OK | 400 | Bad Request |
| 201 | Created | 401 | Unauthorized |
| 204 | No Content | 403 | Forbidden |
| 404 | Not Found | 409 | Conflict |
| 422 | Unprocessable | 429 | Rate Limit |
| 500 | Server Error | | |

### 2.3 错误码设计
格式: `<模块码><错误类型码>`
模块码: 10xxx通用 20xxx用户 30xxx订单 40xxx商品
错误类型: x01参数 x02不存在 x03权限 x04业务规则

---

## 三、版本管理
- URL版本（推荐）: `GET /api/v1/users`
- Header版本: `Accept: application/vnd.company.v2+json`
- 策略: 主版本号=不兼容变更，保持至少2个大版本兼容期

---

## 四、安全
- 认证: `Authorization: Bearer <token>`
- 所有接口默认需要认证（公开接口除外）
- 敏感操作需二次确认
- 速率限制（60 req/min）
- 输入参数严格校验
- CORS 白名单配置

---

## 五、接口文档
每个接口应包含: 路径和方法、请求参数、响应示例（成功+失败）、认证要求、错误码说明
推荐工具: OpenAPI (Swagger) / Postman Collection / Apifox
