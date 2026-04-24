# ⚠️ 第一步：必须最先导入并执行环境配置，否则后面的网络请求会报错！
from config import setup_env
setup_env()

# 第二步：导入构建好的核心应用
from langchain_core.messages import HumanMessage
from core import create_agent_app

if __name__ == "__main__":
    # 初始化 Agent
    app = create_agent_app()
    
    # 我们测试一个需要同时触发多个动作的复杂指令
    user_input = "使用浏览器打开百度搜索今天的三亚天气并截图，并总结。"
    
    print(f"👨‍💻 用户输入: {user_input}")
    
    # 触发流转
    events = app.stream(
        {"messages": [HumanMessage(content=user_input)]},
        stream_mode="values"
    )
    
    for event in events:
        message = event["messages"][-1]
        if message.content:
            print(f"🤖 Agent: {message.content}")