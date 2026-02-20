# ComponentDoc MCP

ComponentDoc 是一个 FastMCP 服务，提供组件文档查询能力，供 `apps/ai-agent/src/tools.py` 调用。

## 文档来源

服务读取当前目录下的 `docs/*.md`：

- `packages/mcp/ComponentDoc/docs/*.md`

这些文档由 MCP 直接消费，不再使用旧的 `packages/docs` 路径。

## 提供的工具

- `list_components`: 列出组件名
- `get_component(name)`: 获取单个组件完整文档
- `search_components(keyword, top_k=5)`: 关键词搜索组件

## 安装与启动

在仓库根目录执行：

```bash
bun run setup:python
bun run dev:mcp
```

等价本地命令（在当前目录）：

```bash
uv sync
uv run python main.py
```

默认地址：

- `http://127.0.0.1:9527/mcp`

## 本地烟测

```bash
uv run python - <<'PY'
from main import _load_docs
print('docs:', len(_load_docs()))
PY
```
