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

            if not browser.contexts or not browser.contexts[0].pages:
                return "请先导航到网页"
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

    # 3. 定义 GitHub Trending 专用工具
    async def scrape_github_trending_func(filename: str = "github_trending.json", limit: int = 25) -> str:
        """
        Scrape GitHub Trending repositories and save to JSON file.
        Works specifically with GitHub Trending page structure.
        """
        try:
            import json
            
            if not browser.contexts or not browser.contexts[0].pages:
                return "Please navigate to GitHub Trending first."
            
            page = browser.contexts[0].pages[0]
            
            # 等待页面加载
            await page.wait_for_selector("article.Box-row", timeout=10000)
            
            # 提取所有项目
            articles = await page.locator("article.Box-row").all()
            
            data = []
            for i, article in enumerate(articles[:limit], 1):
                try:
                    # 项目名
                    repo_elem = article.locator("h2 a")
                    repo_name = await repo_elem.text_content() if await repo_elem.count() > 0 else "N/A"
                    repo_name = repo_name.strip().replace("\n", "").replace("  ", "") if repo_name else "N/A"
                    
                    repo_url = await repo_elem.get_attribute("href") if await repo_elem.count() > 0 else "N/A"
                    
                    # 描述
                    desc_elem = article.locator("p.col-9")
                    description = await desc_elem.text_content() if await desc_elem.count() > 0 else "N/A"
                    description = description.strip() if description else "N/A"
                    
                    # 语言
                    lang_elem = article.locator("span[itemprop='programmingLanguage']")
                    language = await lang_elem.text_content() if await lang_elem.count() > 0 else "N/A"
                    
                    # 今日星数
                    stars_elem = article.locator("span.d-inline-block.float-sm-right")
                    stars_today = await stars_elem.text_content() if await stars_elem.count() > 0 else "N/A"
                    stars_today = stars_today.strip() if stars_today else "N/A"
                    
                    # 总星数
                    total_stars_elem = article.locator("svg.octicon-star").locator("xpath=following-sibling::*[1]")
                    total_stars = await total_stars_elem.text_content() if await total_stars_elem.count() > 0 else "N/A"
                    total_stars = total_stars.strip() if total_stars else "N/A"
                    
                    data.append({
                        "rank": i,
                        "repository": repo_name,
                        "url": f"https://github.com{repo_url}" if repo_url and not repo_url.startswith("http") else repo_url,
                        "description": description,
                        "language": language,
                        "total_stars": total_stars,
                        "stars_today": stars_today
                    })
                    
                except Exception as e:
                    print(f"⚠️ Skip item {i}: {e}")
                    continue
            
            # 保存到 JSON
            output = {
                "metadata": {
                    "total_repositories": len(data),
                    "source": "GitHub Trending"
                },
                "data": data
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(output, f, ensure_ascii=False, indent=2)
            
            return f"✅ Successfully scraped {len(data)} trending repositories. Saved to {filename}"
            
        except Exception as e:
            return f"❌ Error scraping GitHub Trending: {str(e)}"

    github_trending_tool = StructuredTool.from_function(
        func=None,
        coroutine=scrape_github_trending_func,
        name="scrape_github_trending",
        description="Scrape GitHub Trending repositories and save to JSON. Must be on GitHub Trending page first.",
    )

    return standard_tools + [screenshot_tool, github_trending_tool]
