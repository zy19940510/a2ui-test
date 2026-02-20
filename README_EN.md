# A2UI Test Monorepo

English | [简体中文](./README.md)

A2UI Test is an open-source monorepo full-stack sample, including a Web app, Gateway, AI Agent, and a ComponentDoc MCP service used by agent tools.

## Current Structure (Latest)

```text
a2ui-test/
├── ARCHITECTURE.md
├── README.md
├── README_EN.md
├── apps/
│   ├── web/                    # Next.js 16 + React 19
│   ├── gateway/                # FastAPI SSE gateway
│   └── ai-agent/               # LangGraph agent logic and tools
├── packages/
│   ├── a2ui-web/               # UI/config packages migrated from a2ui-component
│   └── mcp/
│       └── ComponentDoc/
│           ├── main.py         # MCP server entry (port 9527)
│           └── docs/           # Component docs consumed by MCP
├── package.json                # workspace and root scripts
└── bun.lock
```

## Tech Stack

- Web: Next.js 16.1.6 + React 19 + Tailwind CSS 4
- Gateway: FastAPI + SSE
- Agent: LangGraph + LangChain OpenAI-compatible
- MCP: FastMCP (ComponentDoc)
- Workspace: Bun Workspaces + uv

## Prerequisites

- Bun >= 1.3
- Python >= 3.13
- uv

## Install Dependencies

Run in repo root:

```bash
bun run setup
```

Equivalent commands:

```bash
bun install
bun run setup:python
```

## Environment Variables

Agent reads `apps/ai-agent/.env`:

```bash
cp apps/ai-agent/.env.example apps/ai-agent/.env
```

Required keys:

- `OPENAI_API_KEY`
- `OPENAI_BASE_URL`
- `MODEL_NAME`

If your provider uses `ONE_API_KEY / ONE_BASE_URL`, map them to `OPENAI_*` keys.

## Start (Development)

Use root scripts:

```bash
# Start MCP + Gateway + Web together
bun run dev
```

Or run them separately:

```bash
bun run dev:mcp
bun run dev:gateway
bun run dev:web
```

## Common Commands

```bash
# Build a2ui-web package dependencies
bun run build:a2ui-web

# Web checks and build
bun run lint:web
bun run build:web
```

## Endpoints

- Web: <http://localhost:3000>
- Weather Demo: <http://localhost:3000/weather>
- Gateway Health: <http://localhost:8000/api/health>
- Gateway Docs: <http://localhost:8000/docs>
- MCP Endpoint: <http://127.0.0.1:9527/mcp>

## Related Docs

- Architecture: [ARCHITECTURE.md](./ARCHITECTURE.md)
- Web: [apps/web/README.md](./apps/web/README.md)
- Gateway: [apps/gateway/README.md](./apps/gateway/README.md)
- Agent: [apps/ai-agent/README.md](./apps/ai-agent/README.md)
- ComponentDoc: [packages/mcp/ComponentDoc/README.md](./packages/mcp/ComponentDoc/README.md)
