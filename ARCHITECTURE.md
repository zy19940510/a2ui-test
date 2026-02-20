# A2UI-Test: SSE 流式渲染框架设计文档

> **最后更新**: 2026-02-20  
> **版本**: v1.2 - Monorepo 结构重构（apps + a2ui-web 包）

## 一、项目概述

### 1.1 目标

构建一个支持 SSE (Server-Sent Events) 流式渲染的全栈框架，实现：

- ✅ Agent 执行过程中的**工具调用**、**思考过程**、**输出消息**实时流式传输到前端
- ✅ **A2UI 0.8 协议**支持，动态生成富交互 UI 组件
- ✅ **Skill Loader 系统**，从 `.claude/skills/` 动态加载 Agent 技能
- ✅ 完整的端到端流式体验（类似 ChatGPT）

### 1.2 技术栈

| 层级       | 技术                           | 说明                           |
| ---------- | ------------------------------ | ------------------------------ |
| 前端       | React + Next.js 15             | SSE 消费、流式 UI 渲染、A2UI 组件 |
| 中转微服务 | Python + FastAPI               | SSE 转发、协议转换、A2UI 解析   |
| Agent      | LangChain + LangGraph          | 智能代理、工具调用、Skill 动态加载 |
| LLM        | Claude Sonnet 4.5              | 推理引擎，支持流式输出          |
| 工具集成   | Open-Meteo API + DuckDuckGo    | 天气查询、网络搜索              |

### 1.3 项目结构

```
~/code/a2ui-test/
├── README.md
├── docs/
│   ├── ARCHITECTURE.md            # 本文档
│   └── LLM_CONFIGURATION.md       # LLM 配置指南
├── .claude/
│   └── skills/                    # Agent 技能库
│       └── a2ui/
│           └── SKILL.md
├── apps/
│   ├── ai-agent/                  # LangGraph Agent
│   │   ├── pyproject.toml
│   │   ├── main.py                # CLI 入口
│   │   └── src/
│   │       ├── agent.py
│   │       ├── tools.py
│   │       └── skill_loader.py
│   ├── gateway/                   # FastAPI 中转服务
│   │   ├── pyproject.toml
│   │   ├── main.py
│   │   └── src/routes/
│   │       ├── chat.py
│   │       └── health.py
│   └── web/                       # Next.js 前端
│       ├── package.json
│       ├── app/
│       ├── a2ui-components/
│       ├── hooks/
│       └── lib/
├── packages/
│   ├── a2ui-web/                  # a2ui-web 全量包
│   │   ├── a2ui-react-renderer/
│   │   ├── animations/
│   │   ├── assets/
│   │   ├── config-postcss/
│   │   ├── config-tailwind/
│   │   ├── config-typescript/
│   │   ├── lit-core/
│   │   ├── shadcn-ui/
│   │   └── utils/
│   ├── docs/
│   └── mcp/
```

---

## 二、核心架构图

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              Architecture Overview                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     HTTP/SSE      ┌──────────────┐    async call    ┌──────────────┐
│              │ ───────────────▶  │              │ ───────────────▶ │              │
│   Frontend   │                   │   Gateway    │                  │    Agent     │
│  (Next.js)   │ ◀─────────────── │  (FastAPI)   │ ◀─────────────── │ (LangGraph)  │
│              │   SSE Stream      │              │  astream_events  │              │
└──────────────┘                   └──────────────┘                  └──────────────┘
      │                                   │                                │
      │                                   │                                │
      ▼                                   ▼                                ▼
┌──────────────┐                  ┌──────────────┐                 ┌──────────────┐
│ A2UI         │                  │ A2UI Parser  │                 │ Skill Loader │
│ Renderer     │                  │ extract_     │                 │ .claude/     │
│ (Custom)     │                  │ a2ui_json    │                 │ skills/a2ui  │
└──────────────┘                  └──────────────┘                 └──────────────┘
      │                                                                    │
      ▼                                                                    ▼
┌──────────────┐                                                   ┌──────────────┐
│ Weather      │                                                   │   Tools      │
│ Card         │                                                   │   - weather  │
│ Custom       │                                                   │   - search   │
│ Components   │                                                   │   - calc     │
└──────────────┘                                                   └──────────────┘
```

---

## 三、核心流程图

### 3.1 完整请求流程（含 A2UI）

```
┌─────────┐                    ┌─────────┐                    ┌─────────┐
│ Browser │                    │ Gateway │                    │  Agent  │
└────┬────┘                    └────┬────┘                    └────┬────┘
     │                              │                              │
     │  1. POST /chat/stream        │                              │
     │  { message: "天气卡片" }     │                              │
     │ ────────────────────────────▶│                              │
     │                              │                              │
     │  2. SSE Connection           │  3. agent.astream_events()   │
     │     Content-Type:            │     + load_skill("a2ui")     │
     │     text/event-stream        │ ────────────────────────────▶│
     │ ◀────────────────────────────│                              │
     │                              │                              │
     │                              │  4. on_chat_model_start      │
     │                              │ ◀────────────────────────────│
     │  5. event: processing        │                              │
     │     data: {"status":"ok"}    │                              │
     │ ◀────────────────────────────│                              │
     │                              │                              │
     │                              │  6. on_tool_start            │
     │                              │     (weather)                │
     │                              │ ◀────────────────────────────│
     │  7. event: tool_call         │                              │
     │     data: {"name":"weather"} │                              │
     │ ◀────────────────────────────│                              │
     │                              │                              │
     │                              │  8. on_tool_end              │
     │                              │ ◀────────────────────────────│
     │  9. event: tool_result       │                              │
     │     data: {"result":"25°C"}  │                              │
     │ ◀────────────────────────────│                              │
     │                              │                              │
     │                              │  10. on_chat_model_stream    │
     │                              │      (文本 + A2UI JSON)      │
     │                              │ ◀────────────────────────────│
     │  11. event: message          │                              │
     │      data: {"chunk":"成都"}  │                              │
     │ ◀────────────────────────────│                              │
     │                              │                              │
     │  12. event: message          │                              │
     │      data: {"chunk":"今天"}  │                              │
     │ ◀────────────────────────────│                              │
     │                              │                              │
     │                              │  13. on_chain_end            │
     │                              │ ◀────────────────────────────│
     │                              │  14. extract_a2ui_json()     │
     │                              │      解析 ---a2ui_JSON---    │
     │  15. event: a2ui             │                              │
     │      data: {surfaceUpdate}   │                              │
     │ ◀────────────────────────────│                              │
     │                              │                              │
     │  16. event: done             │                              │
     │      data: {}                │                              │
     │ ◀────────────────────────────│                              │
     │                              │                              │
     ▼                              ▼                              ▼
```

### 3.2 事件类型映射

| LangGraph 事件         | Gateway 转换  | 前端展示           |
| ---------------------- | ------------- | ------------------ |
| `on_chat_model_start`  | `processing`  | 显示光标 loading   |
| `on_tool_start`        | `tool_call`   | 显示工具调用卡片   |
| `on_tool_end`          | `tool_result` | 显示工具结果       |
| `on_chat_model_stream` | `message`     | 流式显示文本       |
| *(解析后)*             | `a2ui`        | 渲染 A2UI 组件     |
| `on_chain_end`         | `done`        | 完成标记           |

---

## 四、核心模块详解

### 4.1 Skill Loader 系统

**目的**: 动态加载 `.claude/skills/` 中的技能文档，注入到 Agent 的 System Message。

**实现**: `apps/ai-agent/src/skill_loader.py`

```python
class SkillLoader:
    def load_skill(self, skill_name: str, args: str = "") -> dict:
        """
        从 .claude/skills/{skill_name}/SKILL.md 加载技能

        Returns:
            {
                "success": bool,
                "name": str,
                "description": str,
                "content": str,  # 完整的 skill 内容（注入 LLM）
                "base_dir": str,
                "frontmatter": dict
            }
        """
```

**Skill 文件格式**:

```markdown
---
name: a2ui
description: Generate A2UI 0.8 protocol compliant UI code
---

# A2UI Development Skill

## Protocol Version
This skill targets **A2UI Protocol v0.8** (Stable Release).

[详细文档...]
```

**使用场景**:
- Agent 启动时自动加载 `a2ui` skill
- Skill 文档定义了 A2UI 0.8 协议规范
- 告诉 LLM 如何生成符合协议的 JSON

### 4.2 A2UI 协议解析

**目的**: 从 LLM 输出中提取 A2UI JSON 消息并发送给前端。

**实现**: `apps/gateway/src/routes/chat.py`

```python
def extract_a2ui_json(text: str) -> list:
    """
    从 LLM 输出中提取 A2UI JSON

    格式:
    [conversational text]

    ---a2ui_JSON---

    [A2UI JSON array]
    """
    pattern = r'---a2ui_JSON---\s*([\s\S]*?)(?:---|$)'
    match = re.search(pattern, text, re.IGNORECASE)

    if match:
        json_text = match.group(1).strip()
        # 移除可能的 markdown 代码块
        json_text = re.sub(r'^```json\s*', '', json_text, flags=re.MULTILINE)
        json_text = re.sub(r'\s*```$', '', json_text, flags=re.MULTILINE)
        messages = json.loads(json_text)
        return messages
    return []
```

**A2UI 消息格式示例**:

```json
[
  {
    "surfaceUpdate": {
      "surfaceId": "weather-card",
      "components": [
        {"id": "root", "component": {"WeatherCard": {"temperature": 25, "city": "成都"}}}
      ]
    }
  },
  {
    "beginRendering": {"surfaceId": "weather-card"}
  }
]
```

### 4.3 前端 A2UI 渲染

**自定义组件注册**: `apps/web/lib/customCatalog.ts`

```typescript
import { WeatherCard } from "@/a2ui-components/weather";

const customCatalog = {
  kind: "A2UI-component-catalog",
  name: "custom-components",
  version: "1.0.0",
  components: {
    WeatherCard: {
      inputs: {
        temperature: { type: "number" },
        city: { type: "string" },
        // ...
      },
    },
  },
};
```

**渲染器集成**: `apps/web/app/page.tsx`

```tsx
import { A2UIRenderer } from "@anthropic-ai/a2ui-react-renderer";

<A2UIRenderer
  messages={a2uiMessages}
  customCatalog={customCatalog}
  customComponents={{
    WeatherCard: WeatherCard,
  }}
/>
```

### 4.4 工具系统

**工具定义**: `apps/ai-agent/src/tools.py`

```python
from langchain_core.tools import tool

@tool
def get_weather(city: str) -> str:
    """查询城市天气（Open-Meteo API）"""
    # 调用 Open-Meteo API
    return json.dumps(weather_data)

@tool
def search(query: str) -> str:
    """搜索互联网（DuckDuckGo）"""
    # 调用 DuckDuckGo 搜索
    return search_results

@tool
def calculator(expression: str) -> str:
    """计算数学表达式"""
    return str(eval(expression))
```

**工具绑定到 Agent**:

```python
def create_agent():
    tools = get_tools()
    llm_with_tools = llm.bind_tools(tools)
    # ...
```

---

## 五、关键设计决策

### 5.1 为什么选择 SSE 而不是 WebSocket？

| 维度       | SSE                   | WebSocket    |
| ---------- | --------------------- | ------------ |
| 复杂度     | 简单，基于 HTTP       | 需要握手协议 |
| 单向/双向  | 单向（服务器→客户端） | 双向         |
| 自动重连   | 浏览器原生支持        | 需手动实现   |
| 适用场景   | 流式输出（LLM）       | 实时聊天     |
| 本项目需求 | 足够                  | 过度设计     |

**决策：SSE 更适合 Agent 输出流式传输场景**

### 5.2 为什么需要 Gateway 中转层？

```
                    ❌ 直连方案（不推荐）
┌──────────┐                           ┌──────────┐
│ Frontend │ ─────── 直接调用 ────────▶ │  Agent   │
└──────────┘                           └──────────┘
问题：
- 前端暴露 LLM API Key
- 无法统一处理认证/限流
- Agent 变更影响前端

                    ✅ Gateway 方案（推荐）
┌──────────┐       ┌──────────┐       ┌──────────┐
│ Frontend │ ────▶ │ Gateway  │ ────▶ │  Agent   │
└──────────┘       └──────────┘       └──────────┘
优势：
- API Key 安全存储在后端
- 统一认证、限流、日志
- 协议转换和事件标准化（A2UI 解析）
- 可扩展多个 Agent
```

### 5.3 LangGraph `astream_events` vs `astream`

| 方法               | 输出内容       | 适用场景                   |
| ------------------ | -------------- | -------------------------- |
| `astream()`        | 最终状态 delta | 只需要结果                 |
| `astream_events()` | 所有中间事件   | **需要工具调用、思考过程** |

**决策：使用 `astream_events(version="v2")` 获取完整执行过程**

### 5.4 A2UI 协议分隔符设计

**问题**: LLM 输出中如何区分文本和 A2UI JSON？

**解决方案**: 使用明确的分隔符

```
[Conversational text from LLM]

---a2ui_JSON---

[A2UI JSON array]
```

**优势**:
- 简单明确，正则匹配容易
- 允许 LLM 同时输出对话文本和 UI 组件
- 支持流式输出（解析在流结束后）

### 5.5 工具调用 ID 精确匹配

**问题**: 多个工具并发调用时，如何匹配结果？

**解决方案**: 使用 `event["run_id"]` 作为唯一标识

```typescript
// 工具调用时保存 ID
{
  id: event.data.id,  // run_id
  name: "weather",
  isRunning: true
}

// 结果返回时精确匹配
toolCalls.map(tool => {
  if (tool.id === event.data.id) {
    return { ...tool, result: event.data.content.result, isRunning: false };
  }
  return tool;
})
```

---

## 六、API 设计文档

### 6.1 Gateway API

#### POST /api/chat/stream

发起流式对话请求，返回 SSE 流（含 A2UI 消息）。

**Request:**

```typescript
POST /api/chat/stream
Content-Type: application/json

{
  "message": string,           // 用户消息
  "conversation_id"?: string   // 会话 ID（可选）
}
```

**Response (SSE Stream):**

```
HTTP/1.1 200 OK
Content-Type: text/event-stream
Cache-Control: no-cache
Connection: keep-alive

event: processing
data: {"id":"p1","content":{"status":"processing"}}

event: tool_call
data: {"id":"tc1","content":{"name":"get_weather","args":{"city":"成都"}}}

event: tool_result
data: {"id":"tc1","content":{"result":"{\"temperature\":25,\"city\":\"成都\"}"}}

event: message
data: {"id":"m1","content":{"chunk":"成都今天"}}

event: message
data: {"id":"m2","content":{"chunk":"天气晴朗"}}

event: a2ui
data: {"surfaceUpdate":{"surfaceId":"weather","components":[...]}}

event: a2ui
data: {"beginRendering":{"surfaceId":"weather"}}

event: done
data: {"id":"done","content":{}}
```

#### GET /api/health

健康检查端点。

**Response:**

```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

---

## 七、运行与测试

### 7.1 启动服务

```bash
# Terminal 1: 启动 Gateway
cd apps/gateway
uv run uvicorn main:app --reload --port 8000

# Terminal 2: 启动前端
cd apps/web
npm run dev
```

### 7.2 测试场景

#### 场景 1: 基本对话

```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "你好"}' \
  --no-buffer
```

**预期**:
- `event: processing`
- `event: message` (流式文本)
- `event: done`

#### 场景 2: 工具调用

```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "查询成都天气"}' \
  --no-buffer
```

**预期**:
- `event: processing`
- `event: tool_call` (name: get_weather)
- `event: tool_result` (天气数据)
- `event: message` (文本描述)
- `event: done`

#### 场景 3: A2UI 组件生成

```bash
curl -X POST http://localhost:8000/api/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"message": "生成一个成都天气卡片"}' \
  --no-buffer
```

**预期**:
- `event: processing`
- `event: tool_call` (获取天气)
- `event: tool_result`
- `event: message` (文本)
- `event: a2ui` (surfaceUpdate)
- `event: a2ui` (beginRendering)
- `event: done`

---

## 八、扩展指南

### 8.1 添加新工具

1. 在 `apps/ai-agent/src/tools.py` 添加:

```python
@tool
def my_new_tool(param: str) -> str:
    """工具描述"""
    # 实现逻辑
    return result
```

2. 在 `get_tools()` 中返回:

```python
def get_tools():
    return [get_weather, search, calculator, my_new_tool]
```

### 8.2 添加新 A2UI 组件

1. 创建组件: `apps/web/a2ui-components/my-component/index.tsx`

```tsx
export function MyComponent({ data }: { data: string }) {
  return <div>{data}</div>;
}
```

2. 注册到 catalog: `apps/web/lib/customCatalog.ts`

```typescript
components: {
  MyComponent: {
    inputs: {
      data: { type: "string" }
    }
  }
}
```

3. 添加到渲染器:

```tsx
<A2UIRenderer
  customComponents={{
    MyComponent: MyComponent
  }}
/>
```

### 8.3 添加新 Skill

1. 创建目录: `.claude/skills/my-skill/`

2. 编写 `SKILL.md`:

```markdown
---
name: my-skill
description: My custom skill
---

# My Skill

[详细文档...]
```

3. 在 Agent 中加载:

```python
skill_result = loader.load_skill("my-skill")
system_message += skill_result['content']
```

---

## 九、性能优化建议

### 9.1 前端优化

- **虚拟滚动**: 消息列表超过 100 条时使用 `react-window`
- **防抖输入**: 输入框使用 `debounce`
- **组件懒加载**: A2UI 组件使用 `React.lazy()`

### 9.2 后端优化

- **连接池**: 复用 HTTP 连接
- **缓存**: 天气数据缓存 5 分钟
- **限流**: 使用 `slowapi` 限制请求频率

### 9.3 LLM 优化

- **Prompt 优化**: 精简 System Message
- **模型选择**: 简单任务用 Claude Haiku
- **流式优先**: 始终使用 `streaming=True`

---

## 十、常见问题 (FAQ)

### Q1: A2UI JSON 没有被解析？

**检查**:
1. LLM 输出是否包含 `---a2ui_JSON---` 分隔符
2. JSON 格式是否正确（使用 `jq` 验证）
3. Gateway 日志是否有 `✅ Found X A2UI messages`

### Q2: 工具调用结果不显示？

**检查**:
1. 工具是否正确返回字符串
2. `tool_result` 事件的 `id` 是否匹配 `tool_call`
3. 前端 `handleSSEEvent` 中的 ID 匹配逻辑

### Q3: Skill 加载失败？

**检查**:
1. `.claude/skills/a2ui/SKILL.md` 文件是否存在
2. YAML frontmatter 格式是否正确
3. Agent 日志中的 `⚠️ Warning: Failed to load` 错误信息

### Q4: 如何调试 SSE 流？

**方法**:
1. 使用 `curl --no-buffer` 查看原始流
2. 浏览器 Network 面板过滤 `EventStream`
3. Gateway 中添加 `print()` 日志

---

## 十一、技术债务 & TODO

### 当前限制

- [ ] 暂无会话持久化（需要 Redis）
- [ ] 暂无用户认证（需要 JWT）
- [ ] A2UI 组件目录有限（需要扩展）
- [ ] 缺少完整的错误处理

### 下一步计划

1. **会话管理**: Redis 存储历史
2. **认证鉴权**: JWT Token + 用户管理
3. **多模型支持**: 路由到不同 LLM
4. **RAG 集成**: 知识库检索工具
5. **容器化**: Docker Compose 一键部署
6. **监控**: Prometheus + Grafana
7. **测试**: 单元测试 + 集成测试

---

## 十二、参考资源

### 官方文档

- [LangGraph Streaming](https://langchain-ai.github.io/langgraph/how-tos/streaming-tokens/)
- [FastAPI StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/)
- [A2UI Protocol Spec](https://github.com/google/A2UI/blob/main/specification/0.8/)
- [Open-Meteo API](https://open-meteo.com/en/docs)

### 库与工具

- [sse-starlette](https://github.com/sysid/sse-starlette)
- [MDN EventSource](https://developer.mozilla.org/en-US/docs/Web/API/EventSource)
- [A2UI React Renderer](https://github.com/anthropics/anthropic-sdk-typescript/tree/main/packages/a2ui-react-renderer)

### 社区

- [LangChain Discord](https://discord.gg/langchain)
- [Anthropic API Community](https://discord.gg/anthropic)

---

**文档版本**: v1.2  
**最后更新**: 2026-02-20  
**维护者**: A2UI-Test Team
