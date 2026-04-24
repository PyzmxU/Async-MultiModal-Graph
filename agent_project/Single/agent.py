import os

import os

# ==========================================
# 0. 强制设置 SOCKS5 代理 (必须在代码最开头)
# ==========================================
proxy_url = "socks5://127.0.0.1:10809" 

os.environ["HTTP_PROXY"] = proxy_url
os.environ["HTTPS_PROXY"] = proxy_url
os.environ["ALL_PROXY"] = proxy_url
from typing import Annotated
from typing_extensions import TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# ==========================================
# 0. 配置大模型 (这里以兼容 OpenAI 格式的第三方 API 为例)
# ==========================================
os.environ["OPENAI_API_KEY"] = "" # 替换为实际的 Key
os.environ["OPENAI_API_BASE"] = "https://e593-34-11-110-212.ngrok-free.app/v1" # 例如使用 DeepSeek

llm = ChatOpenAI(model="deepseek-chat", temperature=0)

# ==========================================
# 1. 定义工具 (Tool) - Agent 的“手”
# ==========================================
@tool
def multiply(a: int, b: int) -> int:
    """当需要计算两个数字的乘积时，请调用此工具。"""
    print(f"\n[🔧 工具执行中...] 正在计算 {a} * {b}")
    return a * b

tools = [multiply]
# 将工具绑定给大模型，让它知道自己有这个能力
llm_with_tools = llm.bind_tools(tools)

# ==========================================
# 2. 定义状态 (State) - Agent 的“记忆”
# ==========================================
class State(TypedDict):
    # add_messages 会自动将新消息追加到列表中，而不是覆盖
    messages: Annotated[list[BaseMessage], add_messages]

# ==========================================
# 3. 定义节点 (Nodes) - Agent 的“大脑处理区”
# ==========================================
def chatbot(state: State):
    print("\n[🧠 大模型思考中...]")
    # 把当前所有对话状态丢给大模型，让它决定下一步
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

# ==========================================
# 4. 构建图谱 (Graph) - 将一切连接起来
# ==========================================
graph_builder = StateGraph(State)

# 添加节点
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[multiply])
graph_builder.add_node("tools", tool_node)

# 添加连线规则
graph_builder.add_edge(START, "chatbot")

# 这是核心黑科技：条件边。
# 如果模型输出包含工具调用，它会自动走向 "tools" 节点；否则走向 END 结束流转。
graph_builder.add_conditional_edges(
    "chatbot",
    tools_condition,
)
# 工具执行完后，必须把结果送回给 chatbot 节点让它做最终总结
graph_builder.add_edge("tools", "chatbot")

# 编译成可执行应用
app = graph_builder.compile()

# ==========================================
# 5. 运行测试
# ==========================================
if __name__ == "__main__":
    user_input = "你好，请帮我算一下 345 乘以 678 等于多少？不要自己口算，请使用工具。"
    print(f"👨‍💻 用户输入: {user_input}")
    
    # 触发图谱流转
    events = app.stream(
        {"messages": [HumanMessage(content=user_input)]},
        stream_mode="values"
    )
    
    for event in events:
        message = event["messages"][-1]
        if message.content:
            print(f"🤖 Agent: {message.content}")