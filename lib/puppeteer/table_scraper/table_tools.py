"""
表格抓取工具 - 集成到 LangChain Agent
让 Agent 能够自主识别和抓取分页表格
"""

from langchain_core.tools import StructuredTool
from playwright.async_api import Browser, Page
from .table_scraper import TableScraper
from typing import List


def get_table_scraping_tools(browser: Browser) -> List[StructuredTool]:
    """
    创建表格抓取工具集
    
    Args:
        browser: Playwright 浏览器实例
        
    Returns:
        List[StructuredTool]: 工具列表
    """
    
    async def get_current_page() -> Page:
        """获取当前活跃页面"""
        if not browser.contexts:
            raise RuntimeError("No browser context found")
        context = browser.contexts[0]
        if not context.pages:
            raise RuntimeError("No pages open")
        return context.pages[-1]
    
    # ==========================================
    # 工具 1: 提取当前页表格
    # ==========================================
    
    async def extract_current_table(
        table_selector: str = "table",
        save_as: str = "table_data.csv"
    ) -> str:
        """
        Extract table data from the current page.
        
        Args:
            table_selector: CSS selector for the table (default: "table")
            save_as: Filename to save the data (CSV or JSON)
            
        Returns:
            Summary of extracted data
        """
        try:
            page = await get_current_page()
            scraper = TableScraper(page)
            
            # 提取表格
            data = await scraper.extract_table(table_selector=table_selector)
            scraper.all_data.append(data)
            
            # 保存数据
            if save_as.endswith('.json'):
                scraper.save_to_json(save_as)
            else:
                scraper.save_to_csv(save_as)
            
            return f"✅ Extracted {data.total_rows} rows with {len(data.headers)} columns. Saved to {save_as}"
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # ==========================================
    # 工具 2: 按钮分页抓取
    # ==========================================
    
    async def scrape_table_with_pagination(
        table_selector: str = "table",
        next_button_selector: str = "button.next",
        max_pages: int = 5,
        save_as: str = "paginated_data.csv"
    ) -> str:
        """
        Scrape a paginated table using a "next" button.
        
        Args:
            table_selector: CSS selector for the table
            next_button_selector: CSS selector for the next page button
            max_pages: Maximum number of pages to scrape
            save_as: Filename to save the data
            
        Returns:
            Summary of scraped data
        """
        try:
            page = await get_current_page()
            scraper = TableScraper(page)
            
            # 抓取所有页面
            await scraper.scrape_with_button_pagination(
                table_selector=table_selector,
                next_button_selector=next_button_selector,
                max_pages=max_pages,
                wait_time=2.0
            )
            
            # 保存数据
            if save_as.endswith('.json'):
                scraper.save_to_json(save_as)
            else:
                scraper.save_to_csv(save_as)
            
            merged = scraper.merge_all_data()
            return f"✅ Scraped {merged['total_pages']} pages with {merged['total_rows']} total rows. Saved to {save_as}"
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # ==========================================
    # 工具 3: URL 参数分页抓取
    # ==========================================
    
    async def scrape_table_with_url_params(
        base_url: str,
        table_selector: str = "table",
        page_param: str = "page",
        max_pages: int = 10,
        save_as: str = "url_paginated_data.csv"
    ) -> str:
        """
        Scrape a paginated table using URL parameters (e.g., ?page=1).
        
        Args:
            base_url: Base URL of the page
            table_selector: CSS selector for the table
            page_param: URL parameter name for pagination
            max_pages: Maximum number of pages to scrape
            save_as: Filename to save the data
            
        Returns:
            Summary of scraped data
        """
        try:
            page = await get_current_page()
            scraper = TableScraper(page)
            
            # 抓取所有页面
            await scraper.scrape_with_url_params(
                base_url=base_url,
                table_selector=table_selector,
                page_param=page_param,
                start_page=1,
                max_pages=max_pages,
                wait_time=1.5
            )
            
            # 保存数据
            if save_as.endswith('.json'):
                scraper.save_to_json(save_as)
            else:
                scraper.save_to_csv(save_as)
            
            merged = scraper.merge_all_data()
            return f"✅ Scraped {merged['total_pages']} pages with {merged['total_rows']} total rows. Saved to {save_as}"
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # ==========================================
    # 工具 4: 分析表格结构
    # ==========================================
    
    async def analyze_table_structure(
        table_selector: str = "table"
    ) -> str:
        """
        Analyze the structure of a table on the current page.
        Useful for understanding table format before scraping.
        
        Args:
            table_selector: CSS selector for the table
            
        Returns:
            Table structure information
        """
        try:
            page = await get_current_page()
            scraper = TableScraper(page)
            
            # 提取表格
            data = await scraper.extract_table(table_selector=table_selector)
            
            # 分析结构
            analysis = f"""
📊 Table Structure Analysis:
   - Headers: {len(data.headers)} columns
   - Column names: {', '.join(data.headers)}
   - Total rows: {data.total_rows}
   - Sample row: {data.rows[0] if data.rows else 'No data'}
"""
            return analysis
        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    # ==========================================
    # 创建工具列表
    # ==========================================
    
    tools = [
        StructuredTool.from_function(
            func=None,
            coroutine=extract_current_table,
            name="extract_table",
            description="Extract table data from the current page and save to a file (CSV or JSON)."
        ),
        StructuredTool.from_function(
            func=None,
            coroutine=scrape_table_with_pagination,
            name="scrape_paginated_table",
            description="Scrape a paginated table using a 'next' button. Automatically collects data from multiple pages."
        ),
        StructuredTool.from_function(
            func=None,
            coroutine=scrape_table_with_url_params,
            name="scrape_table_url_pagination",
            description="Scrape a paginated table using URL parameters (e.g., ?page=1, ?page=2)."
        ),
        StructuredTool.from_function(
            func=None,
            coroutine=analyze_table_structure,
            name="analyze_table",
            description="Analyze table structure to understand its format before scraping."
        )
    ]
    
    return tools