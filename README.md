# A2UI Test Monorepo

[English](./README_EN.md) | 简体中文

A2UI Test 是一个开源的 Monorepo 全栈示例，包含 Web 前端、Gateway 网关、AI Agent，以及供 Agent 消费的 ComponentDoc MCP 服务。

## 当前结构（最新）

```text
a2ui-test/
├── ARCHITECTURE.md
├── README.md
├── README_EN.md
├── apps/
│   ├── web/                    # Next.js 16 + React 19
│   ├── gateway/                # FastAPI SSE 网关
│   └── ai-agent/               # LangGraph Agent 能力与工具
├── packages/
│   ├── a2ui-web/               # 从 a2ui-component 并入的 UI/配置包
│   └── mcp/
│       └── ComponentDoc/
│           ├── main.py         # MCP 服务入口（9527）
│           └── docs/           # 组件文档（MCP 消费）
├── package.json                # workspace 与根脚本
└── bun.lock
```

## 技术栈

- Web: Next.js 16.1.6 + React 19 + Tailwind CSS 4
- Gateway: FastAPI + SSE
- Agent: LangGraph + LangChain OpenAI-compatible
- MCP: FastMCP（ComponentDoc）
- Workspace: Bun Workspaces + uv

## 前置要求

- Bun >= 1.3
- Python >= 3.13
- uv

## 安装依赖

在仓库根目录执行：

```bash
bun run setup
```

等价命令：

```bash
bun install
bun run setup:python
```

## 环境变量

Agent 使用 `apps/ai-agent/.env`：

```bash
cp apps/ai-agent/.env.example apps/ai-agent/.env
```

需要配置：

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `MODEL_NAME`

如果你使用的是 `ONE_API_KEY / ONE_BASE_URL`，请映射到 `OPENAI_*` 变量。

## 启动（开发模式）

在根目录使用脚本：

```bash
# 一键启动 MCP + Gateway + Web
bun run dev
```

也可以分开启动：

```bash
bun run dev:mcp
bun run dev:gateway
bun run dev:web
```

## 常用命令

```bash
# 预构建 a2ui-web 依赖包
bun run build:a2ui-web

# Web 检查与构建
bun run lint:web
bun run build:web
```

## 访问地址

- Web: <http://localhost:3000>
- Weather Demo: <http://localhost:3000/weather>
- Gateway Health: <http://localhost:8000/api/health>
- Gateway Docs: <http://localhost:8000/docs>
- MCP Endpoint: <http://127.0.0.1:9527/mcp>

## 相关文档

- 架构文档: [ARCHITECTURE.md](./ARCHITECTURE.md)
- Web 说明: [apps/web/README.md](./apps/web/README.md)
- Gateway 说明: [apps/gateway/README.md](./apps/gateway/README.md)
- Agent 说明: [apps/ai-agent/README.md](./apps/ai-agent/README.md)
- ComponentDoc 说明: [packages/mcp/ComponentDoc/README.md](./packages/mcp/ComponentDoc/README.md)
