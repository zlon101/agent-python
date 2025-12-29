"""
Puppeteer 工具模块的辅助函数
"""

import asyncio
from typing import Optional
from playwright.async_api import async_playwright, Page, Browser


async def create_browser_session(headless: bool = True) -> tuple[Browser, Page]:
    """
    创建浏览器会话

    Args:
        headless: 是否以无头模式启动浏览器

    Returns:
        元组，包含浏览器实例和页面实例
    """
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    page = await browser.new_page()
    return browser, page


def sync_run_async(async_func):
    """
    同步运行异步函数的辅助函数
    由于 LangChain 的工具装饰器期望同步函数，我们需要这种方式来运行异步操作
    """
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future = executor.submit(asyncio.run, async_func())
        return future.result()


async def safe_page_operation(page: Page, operation_func, *args, **kwargs):
    """
    安全地执行页面操作，包含错误处理

    Args:
        page: Playwright 页面实例
        operation_func: 要执行的操作函数
        *args, **kwargs: 传递给操作函数的参数

    Returns:
        操作结果或错误信息
    """
    try:
        result = await operation_func(page, *args, **kwargs)
        return result
    except Exception as e:
        return {"error": str(e)}


async def wait_for_selector_safe(page: Page, selector: str, timeout: int = 30000):
    """
    安全地等待元素出现

    Args:
        page: Playwright 页面实例
        selector: CSS 选择器
        timeout: 超时时间（毫秒）

    Returns:
        元素或错误信息
    """
    try:
        element = await page.wait_for_selector(selector, timeout=timeout)
        return element
    except Exception as e:
        return {"error": f"Element not found: {str(e)}"}