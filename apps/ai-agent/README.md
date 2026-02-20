# ai-agent

`ai-agent` 提供 LangGraph Agent 能力与工具定义，供 `apps/gateway` 直接导入调用。

## 目录

- `src/agent.py`: Agent 构建与流式执行入口
- `src/tools.py`: 工具集合（天气、搜索、计算器、ComponentDoc MCP）
- `src/skill_loader.py`: Skill 加载逻辑

## 依赖安装

在仓库根目录执行：

```bash
bun run setup:python
```

或在当前目录执行：

```bash
uv sync
```

## 环境变量

在仓库根目录执行：

```bash
cp apps/ai-agent/.env.example apps/ai-agent/.env
```

必填项：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `MODEL_NAME`

## 运行说明

当前 `main.py` 仅用于基础烟测：

```bash
uv run python main.py
```

实际业务由 `apps/gateway` 通过导入 `src/agent.py` 驱动，不需要单独对外启动 Agent 服务。

## 与 MCP 的关系

`src/tools.py` 默认访问 `http://127.0.0.1:9527/mcp`，因此使用组件文档工具时，需要先启动 `packages/mcp/ComponentDoc/main.py`。
