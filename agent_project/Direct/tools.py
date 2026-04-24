import os
import urllib.parse
import atexit
from langchain_core.tools import tool
from playwright.sync_api import sync_playwright

# ==========================================
# 0. 核心架构：全局浏览器资源池 (单例模式)
# ==========================================
class BrowserManager:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None

    def get_page(self):
        """懒加载：只有在第一次有工具请求时，才真正唤醒内核"""
        if self.browser is None:
            print("\n[⚙️ 系统底层] 正在冷启动全局 Chromium 内核 (整个生命周期仅执行一次)...")
            # 注意这里用的是 start() 而不是 with，这样能让它一直活着
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(headless=True)
            self.page = self.browser.new_page()
            self.page.set_viewport_size({"width": 1920, "height": 1080})
        return self.page

    def close(self):
        """销毁资源"""
        if self.browser:
            print("\n[⚙️ 系统底层] Agent 任务结束，正在释放 Chromium 资源...")
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

# 实例化全局单例
browser_manager = BrowserManager()

# 注册钩子：当 Python 脚本执行结束时，自动清理后台浏览器，防止内存泄漏
atexit.register(browser_manager.close)


# ==========================================
# 工具 1：纯粹的浏览器文本提取工具
# ==========================================
@tool
def search_baidu_text(query: str) -> str:
    """
    当需要通过百度搜索信息并读取网页文字内容时调用此工具。
    参数 query 为搜索关键词（如：三亚天气）。
    """
    print(f"\n[👁️ 文本传感器] 正在阅读百度搜索结果: {query}")
    
    safe_query = urllib.parse.quote(query)
    url = f"https://www.baidu.com/s?wd={safe_query}"
    
    try:
        # 直接从资源池获取那唯一存活的页面
        page = browser_manager.get_page()
        page.goto(url, timeout=15000)
        page.wait_for_load_state("networkidle", timeout=10000)
        
        text_content = page.inner_text("body")
        idx = text_content.find(query)
        snippet = text_content[max(0, idx - 50): min(len(text_content), idx + 800)] if idx != -1 else text_content[:1000]
        
        return f"数据读取成功。\n当前访问的网页 URL 为: {url}\n网页核心文字内容:\n{snippet}"
            
    except Exception as e:
        return f"文本抓取失败: {str(e)}"

# ==========================================
# 工具 2：带“热截图”优化逻辑的视觉工具
# ==========================================
@tool
def take_webpage_screenshot(url: str, save_name: str = "screenshot.png") -> str:
    """
    仅当用户明确要求对某个网页进行【截图、拍照、保存画面】时调用此工具。
    参数 url 必须是完整的网页链接。
    """
    save_path = os.path.abspath(save_name)
    
    try:
        page = browser_manager.get_page()
        
        # 💡 顶级性能优化：零延迟热截图
        # 判断当前浏览器是不是刚好就在你要截的那个网页上
        if page.url == url or urllib.parse.unquote(page.url) == urllib.parse.unquote(url):
            print(f"\n[⚡️ 视觉传感器] 网页已在屏幕上就绪，直接执行零网络延迟【热截图】: {save_name}")
        else:
            print(f"\n[📸 视觉传感器] 正在跨页面跳转并截图: {url}")
            page.goto(url, timeout=15000)
            page.wait_for_load_state("networkidle", timeout=10000)
            
        page.screenshot(path=save_path, full_page=True)
        return f"截图物理保存成功！路径为：{save_path}"
            
    except Exception as e:
        return f"截图失败: {str(e)}"

# 导出工具
agent_tools = [search_baidu_text, take_webpage_screenshot]