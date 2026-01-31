from typing import Annotated, AsyncIterator
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode
from typing_extensions import TypedDict
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

try:
    from .tools import get_tools
except ImportError:
    from tools import get_tools

class State(TypedDict):
    messages: Annotated[list, add_messages]

def create_agent():
    """创建 LangGraph Agent"""
    # 从环境变量读取配置
    llm = ChatOpenAI(
        model=os.getenv("MODEL_NAME", "claude-sonnet-4-5-20250929"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        api_key=os.getenv("OPENAI_API_KEY"),
        temperature=0.7,
        streaming=True
    )

    tools = get_tools()
    # 绑定工具到 LLM
    llm_with_tools = llm.bind_tools(tools)

    def call_model(state: State):
        response = llm_with_tools.invoke(state["messages"])
        return {"messages": [response]}

    def should_continue(state: State):
        last_message = state["messages"][-1]
        if last_message.tool_calls:
            return "tools"
        return END

    # 构建图
    graph = StateGraph(State)
    graph.add_node("agent", call_model)
    graph.add_node("tools", ToolNode(tools))

    graph.add_edge(START, "agent")
    graph.add_conditional_edges("agent", should_continue)
    graph.add_edge("tools", "agent")

    return graph.compile()

async def run_agent_stream(
    message: str,
    conversation_id: str | None = None
) -> AsyncIterator[dict]:
    """流式运行 Agent"""
    agent = create_agent()

    async for event in agent.astream_events(
        {"messages": [{"role": "user", "content": message}]},
        version="v2"
    ):
        yield event