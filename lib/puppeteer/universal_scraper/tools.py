"""
通用抓取器 - LangChain 工具集成
让 Agent 能够使用通用抓取功能
"""

from langchain_core.tools import StructuredTool
from playwright.async_api import Browser
from typing import List, Dict, Optional
from .scraper import UniversalScraper, create_scraper_config


def get_universal_scraping_tools(browser: Browser) -> List[StructuredTool]:
    """
    创建通用抓取工具集
    
    Args:
        browser: Playwright 浏览器实例
        
    Returns:
        工具列表
    """
    
    async def get_current_page():
        """获取当前活跃页面"""
        if not browser.contexts:
            raise RuntimeError("No browser context found")
        context = browser.contexts[0]
        if not context.pages:
            raise RuntimeError("No pages open")
        return context.pages[-1]
    
    # ==========================================
    # 工具 1: 通用数据抓取（简化版）
    # ==========================================
    
    async def scrape_web_data(
        url: str,
        fields: str,
        container_selector: str,
        next_button_selector: str = "",
        delay: float = 3.0,
        max_pages: int = 1,
        filename: str = "scraped_data.json"
    ) -> str:
        """
        通用网页数据抓取工具。
        
        Args:
            url: 目标网址
            fields: 字段配置（JSON字符串），格式: {"字段名": "CSS选择器"}
            container_selector: 数据项容器的CSS选择器
            next_button_selector: 下一页按钮CSS选择器（可选）
            delay: 页面等待时间（秒）
            max_pages: 最大抓取页数
            filename: 保存的文件名
            
        Returns:
            抓取结果摘要
        
        Example:
            fields = '{"标题": "h3 a", "投票数": ".vote-count"}'
            container_selector = ".list-group-item"
        """
        try:
            import json
            
            # 解析字段配置
            try:
                fields_dict = json.loads(fields)
            except:
                return "❌ 字段配置解析失败，请确保是有效的JSON格式"
            
            page = await get_current_page()
            
            # 创建配置
            config = create_scraper_config(
                url=url,
                fields=fields_dict,
                container_selector=container_selector,
                next_button_selector=next_button_selector if next_button_selector else None,
                delay=delay,
                max_pages=max_pages
            )
            
            # 执行抓取
            scraper = UniversalScraper(page, config)
            data = await scraper.scrape()
            
            # 保存数据
            scraper.save_to_json(filename)
            
            return f"✅ 成功抓取 {len(data)} 条数据，已保存到 {filename}"
            
        except Exception as e:
            return f"❌ 抓取失败: {str(e)}"
    
    # ==========================================
    # 工具 2: 高级抓取（支持更多配置）
    # ==========================================
    
    async def scrape_web_data_advanced(
        url: str,
        fields_json: str,
        container_selector: str,
        next_button_selector: str = "",
        page_range_start: int = 1,
        page_range_end: int = 1,
        delay: float = 3.0,
        filename: str = "scraped_data.json"
    ) -> str:
        """
        高级通用抓取工具，支持页码范围。
        
        Args:
            url: 目标网址
            fields_json: 字段配置JSON字符串
            container_selector: 容器选择器
            next_button_selector: 下一页按钮选择器
            page_range_start: 起始页码
            page_range_end: 结束页码
            delay: 页面延迟时间
            filename: 保存文件名
            
        Returns:
            抓取结果
        """
        try:
            import json
            
            # 解析字段
            fields_dict = json.loads(fields_json)
            
            page = await get_current_page()
            
            # 创建配置
            page_range = (page_range_start, page_range_end) if page_range_end > page_range_start else None
            
            config = create_scraper_config(
                url=url,
                fields=fields_dict,
                container_selector=container_selector,
                next_button_selector=next_button_selector if next_button_selector else None,
                page_range=page_range,
                delay=delay,
                max_pages=page_range_end if page_range else 0
            )
            
            # 执行抓取
            scraper = UniversalScraper(page, config)
            data = await scraper.scrape()
            
            # 保存
            scraper.save_to_json(filename)
            
            return f"✅ 抓取完成：{len(data)} 条数据 → {filename}"
            
        except Exception as e:
            return f"❌ 错误: {str(e)}"
    
    # ==========================================
    # 工具 3: 预览抓取（不保存）
    # ==========================================
    
    async def preview_scrape(
        url: str,
        fields: str,
        container_selector: str,
        limit: int = 3
    ) -> str:
        """
        预览抓取结果（只抓取前几条，不保存文件）。
        用于测试选择器是否正确。
        
        Args:
            url: 目标网址
            fields: 字段配置JSON
            container_selector: 容器选择器
            limit: 预览条数
            
        Returns:
            预览数据
        """
        try:
            import json
            
            fields_dict = json.loads(fields)
            page = await get_current_page()
            
            # 创建配置（不分页）
            config = create_scraper_config(
                url=url,
                fields=fields_dict,
                container_selector=container_selector,
                delay=2.0
            )
            
            # 抓取
            scraper = UniversalScraper(page, config)
            await page.goto(url)
            await page.wait_for_selector(container_selector, timeout=10000)
            
            data = await scraper.scrape_current_page()
            
            # 返回前几条
            preview_data = data[:limit]
            
            result = f"📊 预览抓取结果（前 {len(preview_data)} 条）:\n\n"
            result += json.dumps(preview_data, ensure_ascii=False, indent=2)
            
            return result
            
        except Exception as e:
            return f"❌ 预览失败: {str(e)}"
    
    # ==========================================
    # 创建工具列表
    # ==========================================
    
    tools = [
        StructuredTool.from_function(
            func=None,
            coroutine=scrape_web_data,
            name="scrape_web_data",
            description=(
                "通用网页数据抓取工具。支持自定义字段、分页抓取。"
                "需要提供：URL、字段配置（JSON）、容器选择器。"
                "可选：下一页按钮、延迟时间、最大页数。"
            )
        ),
        StructuredTool.from_function(
            func=None,
            coroutine=scrape_web_data_advanced,
            name="scrape_web_data_advanced",
            description=(
                "高级通用抓取工具，支持页码范围控制。"
                "适用于需要精确控制抓取页码范围的场景。"
            )
        ),
        StructuredTool.from_function(
            func=None,
            coroutine=preview_scrape,
            name="preview_scrape",
            description=(
                "预览抓取结果，用于测试选择器是否正确。"
                "只抓取前几条数据，不保存文件。"
            )
        )
    ]
    
    return tools
