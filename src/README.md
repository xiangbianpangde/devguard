# 示例代码库 (src/)

> 对应 BDD 规格：`docs/specs/08-examples.md`

本目录是**规范的可运行示例**，每个子目录对应一份规范文档，演示"规范怎么落地成代码"。

## ⚠️ 组织方式说明

本目录**按规范维度分目录**（每个规范一个文件夹），这是为了让示例与 `conventions/` 一一对应、便于查阅——**它不是推荐的产品代码结构**。

真实项目应按 `conventions/01-architecture_架构设计规范.md` 的建议组织：

- 业务复杂 → 按业务域分（`src/user/`、`src/order/`…）
- 项目简单 → 按技术层次分（`src/controllers/`、`src/services/`…）

`src/architecture/` 子目录内部演示的才是真实可用的分层结构。

## 目录索引

| 子目录 | 对应规范 | 演示内容 |
|--------|---------|---------|
| `architecture/` | 01-架构设计 | 四层架构（表现→应用→领域←基础设施）+ 依赖注入 |
| `coding/` | 02-代码编写 | 命名正反例、错误处理、安全编码 |
| `git/` | 03-Git协作 | .gitignore、pre-commit、commitlint 配置 |
| `api/` | 04-API设计 | FastAPI：URL/统一响应/错误码/分页/校验 |
| `testing/` | 05-测试 | pytest 单元测试（正常/边界/异常）+ Mock 策略 |
| `documentation/` | 06-文档 | Keep a Changelog、公共 API docstring |

## 运行方式

每个子目录有独立 `README.md` 说明依赖与运行命令。语言统一用 **Python**（参考实现），跨语言差异在规范正文中说明，示例不重复实现（见 `docs/specs/08-examples.md` 场景 3）。

```bash
# 架构示例
python -m src.architecture.main
# 测试示例
pytest src/testing/
# API 示例（需 pip install fastapi uvicorn）
cd src/api && uvicorn main:app --reload
```
