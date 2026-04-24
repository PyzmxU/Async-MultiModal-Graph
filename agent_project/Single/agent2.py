import os

# ==========================================
# 0. 强制设置 SOCKS5 代理 (必须在最开头)
# ==========================================
# 推荐使用 socks5h 以解决可能存在的 DNS 污染问题
# 请根据你实际的代理软件修改 10808 端口
proxy_url = "socks5://127.0.0.1:10809" 

os.environ["HTTP_PROXY"] = proxy_url
os.environ["HTTPS_PROXY"] = proxy_url
os.environ["ALL_PROXY"] = proxy_url

# ==========================================
# 1. 导入必要的库
# ==========================================
import urllib.request
import xml.etree.ElementTree as ET
from typing import Annotated
from typing_extensions import TypedDict

from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

# ==========================================
# 2. 配置大模型 (以硅基流动的 Qwen2.5-72B 为例)
# ==========================================
os.environ["OPENAI_API_KEY"] = "sk" 
os.environ["OPENAI_API_BASE"] = ""

llm = ChatOpenAI(model="Qwen/Qwen2.5-72B-Instruct", temperature=0)

# ==========================================
# 3. 定义外部工具：Arxiv 论文检索
# ==========================================
@tool
def search_arxiv_papers(query: str, max_results: int = 3) -> str:
    """
    当需要查找学术论文、前沿算法研究、或者文献综述时，必须调用此工具。
    输入参数 query 必须是精准的英文检索词。
    工具会实时联网返回最新的论文标题和核心摘要。
    """
    print(f"\n[🌍 联网检索中...] 正在 Arxiv 数据库搜索: {query}")
    
    # 格式化 URL，处理空格，调用真实的 Arxiv 开放 API
    safe_query = query.replace(' ', '+')
    url = f"http://export.arxiv.org/api/query?search_query=all:{safe_query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    
    try:
        # 设置超时时间，防止网络波动卡死
        with urllib.request.urlopen(url, timeout=15) as response:
            xml_data = response.read()
        
        # 解析返回的 XML 数据树
        root = ET.fromstring(xml_data)
        results = []
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
            
            # 截取摘要前300字符，防止信息量过载撑爆大模型上下文
            results.append(f"【标题】: {title}\n【摘要】: {summary[:300]}...\n")
            
        if not results:
            return "数据库中未检索到相关论文。"
        return "\n---\n".join(results)
    
    except Exception as e:
        return f"检索 API 调用失败，错误信息: {str(e)}"

# 将检索工具绑定给大模型大脑
tools = [search_arxiv_papers]
llm_with_tools = llm.bind_tools(tools)

# ==========================================
# 4. 构建 LangGraph 状态机 (Agent 核心骨架)
# ==========================================
class State(TypedDict):
    # 状态存储：维护多轮对话和工具调用的历史记录
    messages: Annotated[list[BaseMessage], add_messages]

def chatbot(state: State):
    print("\n[🧠 大模型思考中...]")
    return {"messages": [llm_with_tools.invoke(state["messages"])]}

graph_builder = StateGraph(State)

# 添加核心节点
graph_builder.add_node("chatbot", chatbot)
tool_node = ToolNode(tools=[search_arxiv_papers]) # 绑定真正的工具
graph_builder.add_node("tools", tool_node)

# 设计数据流转逻辑 (图的连线)
graph_builder.add_edge(START, "chatbot")
# 条件判断边：决定是走 tools 节点抓取数据，还是走向 END 输出结果
graph_builder.add_conditional_edges("chatbot", tools_condition)
# 工具执行完毕后，必须回传给 chatbot 节点进行信息汇总
graph_builder.add_edge("tools", "chatbot")

# 编译为可运行应用
app = graph_builder.compile()



# ==========================================
# 5. 运行测试
# ==========================================
if __name__ == "__main__":
    # 测试一个涉及复杂算法检索的任务
    user_input = "我最近在研究 Constrained Multi-objective Optimization (约束多目标优化)。请帮我检索 3 篇最新的相关英文论文，并用中文向我总结一下它们目前在用什么新机制处理约束问题？"
    print(f"👨‍💻 用户输入: {user_input}")
    
    # 触发状态机流转
    events = app.stream(
        {"messages": [HumanMessage(content=user_input)]},
        stream_mode="values"
    )
    
    for event in events:
        message = event["messages"][-1]
        # 只打印有实际文本输出的消息，过滤掉内部格式数据
        if message.content:
            print(f"🤖 Agent: {message.content}")