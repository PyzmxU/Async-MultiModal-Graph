import os
import urllib.parse
from langchain_core.tools import tool
from playwright.async_api import async_playwright

# ==========================================
# 0. 异步核心架构：单例异步浏览器管家
# ==========================================
class AsyncBrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    async def start(self):
        """显式启动：必须在主程序的 asyncio 循环内被调用"""
        if self.browser is None:
            print("\n[⚙️ 异步底层] 正在事件循环中启动全局 Chromium 内核...")
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.page = await self.browser.new_page()
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
        return self.page

    async def get_page(self):
        """获取页面对象，确保已启动"""
        if self.page is None:
            await self.start()
        return self.page

    async def close(self):
        """显式销毁资源"""
        if self.browser:
            print("\n[⚙️ 异步底层] Agent 任务结束，正在安全释放 Chromium 资源...")
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

# 实例化全局单例（此时并未真正启动内核）
browser_manager = AsyncBrowserManager()

# ==========================================
# 工具 1：异步浏览器文本提取工具
# ==========================================
# 💡 注意：不仅函数要变成 async def，里面所有的动作都要加上 await
@tool
async def search_baidu_text(query: str) -> str:
    """
    当需要通过百度搜索信息并读取网页文字内容时调用此工具。
    参数 query 为搜索关键词。
    """
    print(f"\n[👁️ 文本传感器] (Async) 正在阅读百度搜索结果: {query}")
    
    safe_query = urllib.parse.quote(query)
    url = f"https://www.baidu.com/s?wd={safe_query}"
    
    try:
        page = await browser_manager.get_page()
        await page.goto(url, timeout=15000)
        await page.wait_for_load_state("networkidle", timeout=10000)
        
        text_content = await page.inner_text("body")
        
        idx = text_content.find(query)
        snippet = text_content[max(0, idx - 50): min(len(text_content), idx + 800)] if idx != -1 else text_content[:1000]
        
        return f"数据读取成功。\n当前访问的 URL 为: {url}\n网页核心文字内容:\n{snippet}"
            
    except Exception as e:
        return f"文本抓取失败: {str(e)}"

# ==========================================
# 工具 2：异步零延迟热截图工具
# ==========================================
@tool
async def take_webpage_screenshot(url: str, save_name: str = "screenshot.png") -> str:
    """
    仅当用户明确要求对某个网页进行【截图、拍照】时调用此工具。
    """
    save_path = os.path.abspath(save_name)
    
    try:
        page = await browser_manager.get_page()
        
        # 异步热截图判断
        if page.url == url or urllib.parse.unquote(page.url) == urllib.parse.unquote(url):
            print(f"\n[⚡️ 视觉传感器] (Async) 网页已就绪，触发零网络延迟【热截图】: {save_name}")
        else:
            print(f"\n[📸 视觉传感器] (Async) 正在跨页面跳转并截图: {url}")
            await page.goto(url, timeout=15000)
            await page.wait_for_load_state("networkidle", timeout=10000)
            
        await page.screenshot(path=save_path, full_page=True)
        return f"截图物理保存成功！路径为：{save_path}"
            
    except Exception as e:
        return f"截图失败: {str(e)}"

# 导出工具
agent_tools = [search_baidu_text, take_webpage_screenshot]