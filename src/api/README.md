# API 设计示例

> 对应规范：`conventions/04-api_API设计规范.md`
> 运行：`pip install fastapi uvicorn && uvicorn main:app --reload`

一个完整的 RESTful API 微服务，演示：
- URL 设计（资源名词 + HTTP 方法）
- 统一响应格式（code + message + data）
- 错误码体系
- 分页/排序/过滤
- 输入校验 + 白名单

运行后访问 http://localhost:8000/docs 查看交互式 API 文档。
