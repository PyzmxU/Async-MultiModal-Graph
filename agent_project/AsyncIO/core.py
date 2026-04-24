from typing import Annotated
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# 导入刚才定义的工具列表
from tools import agent_tools

def create_agent_app():
    """工厂函数：用于构建并返回编译好的 Agent 应用"""
    
    # 1. 实例化模型并绑定工具
    llm = ChatOpenAI(model="qwen3.5-plus", temperature=0)
    llm_with_tools = llm.bind_tools(agent_tools)

    # 2. 定义状态
    class State(TypedDict):
        messages: Annotated[list[BaseMessage], add_messages]

    # 3. 定义大模型处理节点
    # def chatbot(state: State):
    #     print("\n[🧠 大模型思考中...]")
    #     return {"messages": [llm_with_tools.invoke(state["messages"])]}
    # ... 前面的代码保持不变 ...

    # 3. 定义异步大模型处理节点
    async def chatbot(state: State):
        print("\n[🧠 大模型思考中...] (Async)")
        # 💡 注意：将 invoke 改为 ainvoke (异步调用)
        response = await llm_with_tools.ainvoke(state["messages"])
        return {"messages": [response]}

# ... 后面的建图代码保持不变 ...

    # 4. 构建图谱
    graph_builder = StateGraph(State)
    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_node("tools", ToolNode(tools=agent_tools))

    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_conditional_edges("chatbot", tools_condition)
    graph_builder.add_edge("tools", "chatbot")

    # 返回编译后的应用
    return graph_builder.compile()