import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from langchain_core.tools import tool

import urllib.request
import urllib.parse
import re
from langchain_core.tools import tool
import os
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright

import os
import urllib.parse
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright

@tool
def baidu_weather_screenshot_and_summary(city: str) -> str:
    """
    当用户要求查询某个城市天气，并且明确要求【截图/拍照】并【总结】时，必须调用此终极工具。
    参数 city 为纯中文城市名，如“三亚”。
    工具会一次性完成：打开网页、截取网页画面保存，并返回网页的文字内容供模型总结。
    """
    print(f"\n[📸+👁️ 复合传感器启动...] 正在前往百度获取 {city} 天气，准备截图与阅读...")
    
    query = f"{city}天气"
    safe_query = urllib.parse.quote(query)
    url = f"https://www.baidu.com/s?wd={safe_query}"
    save_path = os.path.abspath(f"{city}_weather.png")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            # 1. 访问网页
            page.goto(url, timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # 2. 核心动作一：按下快门，保存底片
            page.screenshot(path=save_path, full_page=True)
            print(f" -> 截图已保存至: {save_path}")
            
            # 3. 核心动作二：提取可见文本，充当大模型的“眼睛”
            text_content = page.inner_text("body")
            
            browser.close()
            
            # 找到天气核心区（防止几万字的文本撑爆内存）
            idx = text_content.find(f"{city}天气")
            snippet = text_content[max(0, idx - 50): min(len(text_content), idx + 800)] if idx != -1 else text_content[:1000]
            
            # 4. 把路径和文本一起返回给大模型
            return f"执行成功！截图已物理保存至：{save_path}。\n网页核心文字内容如下：\n{snippet}\n请告诉用户截图已保存，并根据上述文字为用户总结天气情况。"
            
    except Exception as e:
        return f"任务执行失败: {str(e)}"

@tool
def search_arxiv_papers(query: str, max_results: int = 3) -> str:
    """当需要查找学术论文、前沿算法研究时必须调用此工具。传入英文 query。"""
    print(f"\n[🌍 联网检索中...] 正在 Arxiv 数据库搜索: {query}")
    safe_query = query.replace(' ', '+')
    url = f"http://export.arxiv.org/api/query?search_query=all:{safe_query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    try:
        with urllib.request.urlopen(url, timeout=15) as response:
            xml_data = response.read()
        root = ET.fromstring(xml_data)
        results = []
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip()
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip()
            results.append(f"【标题】: {title}\n【摘要】: {summary[:300]}...\n")
        return "\n---\n".join(results) if results else "未检索到相关论文。"
    except Exception as e:
        return f"检索失败: {str(e)}"

@tool
def get_weather(city: str) -> str:
    """当询问某个城市的天气时必须调用此工具。传入中文城市名。"""
    print(f"\n[🌤️ 气象卫星连接中...] 正在获取 {city} 的实时天气")
    safe_city = urllib.parse.quote(city)
    url = f"https://wttr.in/{safe_city}?format=3"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'curl/7.68.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            weather_data = response.read().decode('utf-8').strip()
        return f"查询成功，数据为：{weather_data}" if weather_data else "天气数据获取为空。"
    except Exception as e:
        return f"获取天气失败: {str(e)}"



@tool
def get_weather_from_baidu(city: str) -> str:
    """
    当需要查询城市天气时必须调用此工具。
    该工具会通过百度搜索(www.baidu.com)实时抓取网页数据。
    参数 city 必须是纯中文城市名称，如“南京”。
    """
    print(f"\n[🔍 百度搜索中...] 正在硬抓取 {city} 的天气网页数据")
    
    # 构造百度搜索URL，比如：南京天气
    query = f"{city}天气"
    safe_query = urllib.parse.quote(query)
    url = f"https://www.baidu.com/s?wd={safe_query}"
    
    # ⚠️ 极度关键：必须伪装成真实的高级浏览器，否则百度会直接返回 403 拦截或安全验证码
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        # 伪造一个来源，降低被反爬识别的概率
        'Referer': 'https://www.baidu.com/'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html_data = response.read().decode('utf-8')
            
        # ==========================================
        # 暴力清洗 HTML (暴力美学：丢给大模型处理)
        # ==========================================
        # 1. 剔除所有 CSS 样式和 JS 脚本
        clean_text = re.sub(r'<style.*?>.*?</style>', '', html_data, flags=re.IGNORECASE|re.DOTALL)
        clean_text = re.sub(r'<script.*?>.*?</script>', '', clean_text, flags=re.IGNORECASE|re.DOTALL)
        # 2. 剔除所有 HTML 尖括号标签，仅保留页面上的可见文字
        clean_text = re.sub(r'<[^>]+>', ' ', clean_text)
        # 3. 压缩连续的空格和换行
        clean_text = re.sub(r'\s+', ' ', clean_text)
        
        # 为了防止百度的整个网页撑爆大模型的上下文限制（Token溢出）
        # 我们只截取关键词首次出现位置附近的核心文本段落
        idx = clean_text.find(f"{city}天气")
        if idx != -1:
            # 截取该关键字前 50 字符到后 800 字符的生肉文本
            start = max(0, idx - 50)
            end = min(len(clean_text), idx + 800)
            snippet = clean_text[start:end]
            return f"百度网页抓取成功，提取的生肉文本如下：\n{snippet}\n请从中仔细提取气温、天气状况等信息回答用户。"
        else:
            return "抓取成功，但网页源码中未找到明显的结构化天气段落，可能遇到了百度的动态反爬渲染。"

    except Exception as e:
        return f"百度搜索请求失败，网络或反爬报错: {str(e)}"
# 核心导出点：统一将所有可用工具打包成一个列表
# agent_tools = [search_arxiv_papers, get_weather, get_weather_from_baidu]



from langchain_core.tools import tool
from playwright.sync_api import sync_playwright

@tool
def browse_webpage(url: str) -> str:
    """
    当需要访问特定网页并提取其文字内容时调用此工具。
    参数 url 必须是完整的网址 (以 http 或 https 开头)。
    该工具会启动真实浏览器渲染网页，能绕过绝大多数动态反爬。
    """
    print(f"\n[🌐 唤醒浏览器中...] 正在打开网页: {url}")
    
    try:
        with sync_playwright() as p:
            # 启动无头浏览器 (headless=True 表示不弹出实体窗口，后台静默运行)
            # 如果你想亲眼看着它打开网页，可以改成 headless=False
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 设置一个超时时间（比如15秒），防止网页卡死
            page.goto(url, timeout=15000)
            
            # 霸道指令：等待页面网络空闲（也就是 JS 数据基本加载完了）
            page.wait_for_load_state("networkidle", timeout=10000)
            
            # 提取整个页面的纯文本（Playwright 会自动过滤掉 HTML 标签，只留人眼可见的字）
            text_content = page.inner_text("body")
            
            browser.close()
            
            # 截取前 2000 个字符返回，防止超长文本撑爆大模型内存
            return f"网页内容抓取成功:\n{text_content[:2000]}...\n请根据以上内容回答用户。"
            
    except Exception as e:
        return f"浏览器访问 {url} 失败: {str(e)}"
    

@tool
def take_webpage_screenshot(url: str, save_name: str = "web_screenshot.png") -> str:
    """
    当用户要求给某个网页截图、拍照或保存网页画面时，必须调用此工具。
    参数 url 必须是完整的网址 (以 http 或 https 开头)。
    参数 save_name 是保存的图片文件名，默认为 web_screenshot.png。
    工具会启动真实浏览器加载网页，并截取整个网页的长图保存到本地。
    """
    print(f"\n[📸 视觉传感器启动...] 正在前往 {url} 执行全页面截图任务")
    
    # 获取当前工作目录的绝对路径，确保知道图片保存在哪
    save_path = os.path.abspath(save_name)
    
    try:
        with sync_playwright() as p:
            # 启动无头浏览器
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            
            # 设置浏览器视窗大小（模拟宽屏显示器，这样截图不会是手机版的窄版）
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            # 访问网页并等待网络基本空闲
            page.goto(url, timeout=20000)
            page.wait_for_load_state("networkidle", timeout=15000)
            
            # 💡 核心魔法：全网页长截图
            # full_page=True 会自动向下滚动到底部，把整个长网页截下来
            page.screenshot(path=save_path, full_page=True)
            
            browser.close()
            
            return f"任务圆满完成！已成功截取网页画面，并保存在您的电脑上：{save_path}。请提醒用户去该路径查看。"
            
    except Exception as e:
        return f"截图任务失败，错误原因: {str(e)}"

agent_tools = [search_arxiv_papers,  baidu_weather_screenshot_and_summary]