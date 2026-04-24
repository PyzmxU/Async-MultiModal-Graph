import os

def setup_env():
    """初始化全局环境变量，必须在程序启动的最开始调用"""
    
    # 1. 代理配置
    proxy_url = "socks5h://127.0.0.1:10809" 
    os.environ["HTTP_PROXY"] = proxy_url
    os.environ["HTTPS_PROXY"] = proxy_url
    os.environ["ALL_PROXY"] = proxy_url

    # 2. 大模型 API 配置 (以硅基流动为例)
    os.environ["OPENAI_API_KEY"] = "" 
    os.environ["OPENAI_API_BASE"] = "https://coding.dashscope.aliyuncs.com/v1"