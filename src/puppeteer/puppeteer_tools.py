"""
Puppeteer/Playwright 工具模块
提供浏览器自动化功能给 LangChain Agent
"""

from typing import List
from langchain_core.tools import BaseTool, StructuredTool
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from playwright.async_api import Browser


def get_browser_tools(browser: Browser) -> List[BaseTool]:
    """
    基于传入的 Browser 实例，创建并返回一系列浏览器工具。
    """

    # 1. 初始化 LangChain 官方工具包
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
    standard_tools = toolkit.get_tools()

    # 2. 定义自定义截图工具
    async def take_screenshot_func(filename: str = "screenshot.png") -> str:
        """
        Take a screenshot of the current page and save it to a file.
        Useful when the user asks to capture the screen or see the page.
        """
        try:
            if not browser.contexts:
                return "No open browser context found. Please navigate to a page first."

            page = browser.contexts[0].pages[0]
            await page.screenshot(path=filename)
            return f"Screenshot successfully saved to {filename}"
        except Exception as e:
            return f"Failed to take screenshot: {str(e)}"

    screenshot_tool = StructuredTool.from_function(
        func=None,
        coroutine=take_screenshot_func,
        name="take_screenshot",
        description="Take a screenshot of the current page. Input should be a filename (e.g., 'home.png').",
    )

    return standard_tools + [screenshot_tool]
