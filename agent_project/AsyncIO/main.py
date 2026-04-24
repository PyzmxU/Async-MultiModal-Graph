import asyncio
from config import setup_env

# 必须第一步配置环境
setup_env()

from langchain_core.messages import HumanMessage
from core import create_agent_app
from tools import browser_manager

async def main():
    app = create_agent_app()
    user_input = "使用浏览器打开百度搜索三亚天气并截图，并总结。"
    
    print(f"👨‍💻 用户输入: {user_input}")
    
    try:
        # ⚠️ 极其关键：在整个状态机流转前，预先在当前的 event loop 中启动浏览器
        await browser_manager.start()
        
        # 触发异步图谱流转 (注意使用的是 astream)
        events = app.astream(
            {"messages": [HumanMessage(content=user_input)]},
            stream_mode="values"
        )
        
        # 异步遍历流输出
        async for event in events:
            message = event["messages"][-1]
            if message.content:
                print(f"🤖 Agent: {message.content}")
                
    except Exception as e:
        print(f"\n❌ 运行发生错误: {e}")
        
    finally:
        # 无论成功还是异常报错，最终强制执行安全清理，杜绝僵尸进程
        await browser_manager.close()

if __name__ == "__main__":
    # 启动 AsyncIO 事件循环
    asyncio.run(main())