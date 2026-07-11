# 代码理解示例

> **👤 人类参考** | 对应规范：`conventions/08-code-understanding_代码理解与图谱规范.md`（v3.0）
> 技术栈：Python 3.10+ | 教学用途
> 更新: 2026-07-11

## 目录结构

```
code-understanding/
├── README-代码理解示例.md     # 本文件
└── call_graph_example.py     # AST 遍历构建调用图（教学演示）
```

## 文件说明

| 文件 | 说明 |
|------|------|
| `call_graph_example.py` | 用 Python AST 演示 CodeGraph 底层原理——如何从源码抽取函数/类节点和调用关系。这是教学用途的轻量实现，真实项目请使用 CodeGraph（tree-sitter + SQLite+FTS5 + MCP）。 |

## 快速运行

```bash
# 构建当前目录的调用图
python call_graph_example.py .

# 输出示例：
#   实体: 15 个（函数: 10, 类: 5）
#   关系: 23 条（调用: 18）
#   ⚠ 孤儿节点: 2 个
#   🔥 Top 5 被调用最多的函数: ...
```

## 真实项目使用

| 用途 | 工具 | 安装 |
|------|------|------|
| AI 编码助手用（AI 图谱） | [CodeGraph](https://github.com/colbymchenry/codegraph) | `curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh \| sh` |
| 人交互式浏览（人的图谱） | [Understand-Anything](https://github.com/Lum1104/Understand-Anything) | `/plugin install understand-anything` |

详见规范 §一（CodeGraph）和 §二（Understand-Anything）。
