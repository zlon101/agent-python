"""
Puppeteer 工具模块
提供浏览器自动化功能给 LangChain Agent
"""

import asyncio
import json
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from langchain_core.tools import tool

# 检查是否安装了 playwright
try:
    from playwright.async_api import async_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    print("Playwright not available. Please install it using: pip install playwright")
    print("Then run: playwright install")


class BrowserConfig(BaseModel):
    """浏览器配置参数"""
    headless: bool = Field(default=True, description="是否以无头模式运行浏览器")
    timeout: int = Field(default=30000, description="页面操作超时时间（毫秒）")
    wait_for_load: bool = Field(default=True, description="是否等待页面加载完成")


@tool
def browse_web_page(url: str, query: Optional[str] = None) -> Dict[str, Any]:
    """
    使用浏览器访问网页并可选择性地查询特定信息

    Args:
        url: 要访问的网页URL
        query: 可选，要在页面上查找的特定信息或问题

    Returns:
        包含页面信息或查询结果的字典
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {"error": "Playwright is not available. Cannot browse web pages."}

    async def _browse_web_page():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                # 访问网页
                await page.goto(url, wait_until="networkidle" if BrowserConfig.wait_for_load else "domcontentloaded")

                if query:
                    # 如果有查询，尝试在页面中查找相关信息
                    content = await page.content()
                    # 这里可以添加更复杂的页面内容分析逻辑
                    result = f"Found information related to '{query}' on {url}"
                else:
                    # 否则返回页面标题和部分内容
                    title = await page.title()
                    content = await page.inner_text("body")
                    # 截取前1000个字符作为预览
                    preview = content[:1000] + "..." if len(content) > 1000 else content
                    result = {"title": title, "preview": preview}

                await browser.close()
                return result
            except Exception as e:
                await browser.close()
                return {"error": str(e)}

    # 由于 tool 装饰器期望同步函数，我们需要同步执行异步函数
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, _browse_web_page())
        return future.result()


@tool
def take_screenshot(url: str, full_page: bool = False) -> Dict[str, Any]:
    """
    对指定网页进行截图

    Args:
        url: 要截图的网页URL
        full_page: 是否截取整个页面（否则只截取可见部分）

    Returns:
        包含截图保存路径的字典
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {"error": "Playwright is not available. Cannot take screenshots."}

    async def _take_screenshot():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="networkidle")

                # 生成截图文件名
                import os
                import time
                timestamp = int(time.time())
                screenshot_path = f"screenshot_{timestamp}.png"

                # 截图
                await page.screenshot(path=screenshot_path, full_page=full_page)

                await browser.close()
                return {"screenshot_path": os.path.abspath(screenshot_path), "url": url}
            except Exception as e:
                await browser.close()
                return {"error": str(e)}

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, _take_screenshot())
        return future.result()


@tool
def extract_links(url: str) -> Dict[str, Any]:
    """
    从指定网页提取所有链接

    Args:
        url: 要提取链接的网页URL

    Returns:
        包含提取链接的字典
    """
    if not PLAYWRIGHT_AVAILABLE:
        return {"error": "Playwright is not available. Cannot extract links."}

    async def _extract_links():
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                await page.goto(url, wait_until="networkidle")

                # 提取所有链接
                links = await page.evaluate("""
                    () => {
                        const anchors = Array.from(document.querySelectorAll('a[href]'));
                        return anchors.map(anchor => ({
                            href: anchor.href,
                            text: anchor.innerText.trim()
                        }));
                    }
                """)

                await browser.close()
                return {"url": url, "links_count": len(links), "links": links[:20]}  # 只返回前20个链接
            except Exception as e:
                await browser.close()
                return {"error": str(e)}

    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, _extract_links())
        return future.result()


# 可以添加更多浏览器工具函数
# 例如：fill_form, click_element, get_page_content 等

def get_puppeteer_tools():
    """
    返回所有 Puppeteer 工具的列表，供 Agent 使用
    """
    tools = [browse_web_page, take_screenshot, extract_links]
    return tools