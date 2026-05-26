# 文档规范

---

## 一、项目必写文档

### 1.1 README.md
```markdown
# 项目名称
一句话描述项目

## 快速开始 - 如何5分钟跑起来
## 功能特性 - 核心功能列表
## 技术栈 - 使用的技术
## 目录结构 - 项目文件组织
## 贡献指南 - 如何参与开发
```

### 1.2 CHANGELOG.md
```markdown
## v1.2.0 (2026-05-20)
### Added - 新增功能
### Changed - 变更
### Fixed - 修复
### Deprecated - 即将废弃
### Removed - 已移除
### Security - 安全修复
```

### 1.3 CONTRIBUTING.md
- 开发环境搭建 / 代码规范说明 / 提交流程 / PR规范

---

## 二、代码注释文档

### 2.1 函数注释
```python
def create_order(user_id: str, product_id: str, quantity: int) -> Order:
    """创建订单。
    Args: user_id/ product_id/ quantity
    Returns: 创建的订单对象
    Raises: ValueError(库存不足) / UserNotFoundError
    """
```

### 2.2 类注释
```python
class OrderService:
    """订单服务，负责订单的创建、查询、取消。
    使用示例: service = OrderService(db)
    """
```

---

## 三、接口文档模板
```markdown
## POST /api/orders - 创建新订单
### 请求头: Authorization: Bearer <token>
### 请求体: {"product_id":"prod_123","quantity":2,"remark":"加急"}
### 成功响应 (201): {"code":0,"data":{"order_id":"ord_456","status":"pending"}}
### 错误码: 40001参数错误 / 40002商品不存在 / 40003库存不足
```

---

## 四、设计文档
**何时写**: 需求不清晰 / 复杂功能(3+模块) / 重大架构变更
**模板**: 背景→目标→方案→影响范围→风险

---

## 五、文件命名
| 类型 | 格式 | 示例 |
|------|------|------|
| 普通文档 | 描述性名称 | `架构设计.md` |
| 日期相关 | YYYY-MM-DD前缀 | `2026-05-20-会议纪要.md` |
| 版本相关 | v+版本号 | `v2.0-更新说明.md` |

命名原则: 禁止空格用-连接 | 禁止特殊字符

---

## 六、文档维护
- **更新时机**: 功能变更同步更新 / 发现过时立即修复 / 每季度检查
- **废弃处理**: 移到 `archive/` / 头部标注废弃日期 / 不直接删除
- **工具**: Markdown / Mermaid(流程图) / 语雀/Notion/Confluence
