"""
分页表格抓取示例
演示如何使用 TableScraper 收集不同类型的分页表格
"""

import asyncio
from dotenv import load_dotenv
from lib.browser import BrowserManager
from .table_scraper import TableScraper

load_dotenv()


# ==========================================
# 示例 1: 使用"下一页"按钮的分页表格
# ==========================================

async def example_button_pagination():
    """
    示例：抓取使用"下一页"按钮的表格
    适用于：电商网站、新闻列表等
    """
    print("\n" + "="*60)
    print("📌 示例 1: 按钮分页")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        page = await bm.get_or_create_page()
        scraper = TableScraper(page)
        
        # 1. 导航到目标页面
        url = "https://example.com/products"  # 替换为实际 URL
        print(f"🌐 访问: {url}")
        await page.goto(url)
        
        # 2. 抓取所有页面
        await scraper.scrape_with_button_pagination(
            table_selector="table.product-list",  # 表格选择器
            next_button_selector="button.next-page",  # 下一页按钮
            max_pages=5,  # 最多抓取 5 页
            wait_time=2.0  # 每页等待 2 秒
        )
        
        # 3. 保存数据
        scraper.save_to_csv("products.csv")
        scraper.save_to_json("products.json")


# ==========================================
# 示例 2: 使用页码的分页表格
# ==========================================

async def example_number_pagination():
    """
    示例：抓取使用页码（1, 2, 3...）的表格
    适用于：论坛、博客等
    """
    print("\n" + "="*60)
    print("📌 示例 2: 页码分页")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        page = await bm.get_or_create_page()
        scraper = TableScraper(page)
        
        # 1. 导航到第一页
        url = "https://example.com/articles"
        print(f"🌐 访问: {url}")
        await page.goto(url)
        
        # 2. 抓取所有页面
        await scraper.scrape_with_page_numbers(
            table_selector="table#articles",
            page_number_selector="a[data-page='{page}']",  # {page} 会被替换
            max_pages=10,
            wait_time=1.5
        )
        
        # 3. 保存数据
        scraper.save_to_csv("articles.csv")


# ==========================================
# 示例 3: 使用 URL 参数的分页表格
# ==========================================

async def example_url_pagination():
    """
    示例：抓取使用 URL 参数的表格（?page=1）
    适用于：API 结果、搜索结果等
    """
    print("\n" + "="*60)
    print("📌 示例 3: URL 参数分页")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        page = await bm.get_or_create_page()
        scraper = TableScraper(page)
        
        # 抓取所有页面
        await scraper.scrape_with_url_params(
            base_url="https://example.com/search?q=python",
            table_selector="table.results",
            page_param="page",
            start_page=1,
            max_pages=20,
            wait_time=1.0
        )
        
        # 保存数据
        scraper.save_to_json("search_results.json")


# ==========================================
# 示例 4: 自定义表格选择器
# ==========================================

async def example_custom_selectors():
    """
    示例：使用自定义选择器提取特定格式的表格
    """
    print("\n" + "="*60)
    print("📌 示例 4: 自定义选择器")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        page = await bm.get_or_create_page()
        scraper = TableScraper(page)
        
        # 导航到页面
        await page.goto("https://example.com/data")
        
        # 提取单页数据（自定义选择器）
        data = await scraper.extract_table(
            table_selector="div.data-table",  # 不是标准 <table>
            headers_selector="div.header span",  # 自定义表头
            rows_selector="div.row",  # 自定义行
            cells_selector="div.cell"  # 自定义单元格
        )
        
        print(f"✅ 提取到 {data.total_rows} 行数据")
        print(f"表头: {data.headers}")


# ==========================================
# 示例 5: 实战 - 抓取 GitHub Trending
# ==========================================

async def example_github_trending():
    """
    实战示例：抓取 GitHub Trending 表格
    """
    print("\n" + "="*60)
    print("📌 示例 5: GitHub Trending 实战")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        page = await bm.get_or_create_page()
        scraper = TableScraper(page)
        
        # 1. 访问 GitHub Trending
        url = "https://github.com/trending"
        print(f"🌐 访问: {url}")
        await page.goto(url)
        
        # 2. 等待表格加载
        await page.wait_for_selector("article.Box-row", timeout=10000)
        
        # 3. 自定义提取逻辑（GitHub 不是标准表格）
        print("📊 提取项目列表...")
        
        articles = await page.locator("article.Box-row").all()
        
        headers = ["Rank", "Repository", "Description", "Language", "Stars Today"]
        rows = []
        
        for i, article in enumerate(articles[:25], 1):  # 前 25 个
            try:
                # 提取项目名
                repo_name = await article.locator("h2 a").text_content()
                repo_name = repo_name.strip().replace("\n", "").replace("  ", "")
                
                # 提取描述
                desc_elem = article.locator("p")
                description = await desc_elem.text_content() if await desc_elem.count() > 0 else "N/A"
                description = description.strip() if description else "N/A"
                
                # 提取语言
                lang_elem = article.locator("span[itemprop='programmingLanguage']")
                language = await lang_elem.text_content() if await lang_elem.count() > 0 else "N/A"
                
                # 提取今日星数
                stars_elem = article.locator("span.float-sm-right")
                stars = await stars_elem.text_content() if await stars_elem.count() > 0 else "N/A"
                stars = stars.strip()
                
                rows.append([str(i), repo_name, description, language, stars])
                
            except Exception as e:
                print(f"⚠️  跳过项目 {i}: {e}")
                continue
        
        # 4. 手动创建 TableData
        from table_scraper import TableData
        data = TableData(
            headers=headers,
            rows=rows,
            page_number=1,
            total_rows=len(rows)
        )
        scraper.all_data.append(data)
        
        # 5. 保存数据
        scraper.save_to_csv("github_trending.csv")
        scraper.save_to_json("github_trending.json")
        
        print(f"\n✅ 成功提取 {len(rows)} 个项目")


# ==========================================
# 示例 6: 处理动态加载的表格
# ==========================================

async def example_dynamic_table():
    """
    示例：处理通过 JavaScript 动态加载的表格
    """
    print("\n" + "="*60)
    print("📌 示例 6: 动态加载表格")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        page = await bm.get_or_create_page()
        scraper = TableScraper(page)
        
        # 访问页面
        await page.goto("https://example.com/dynamic-table")
        
        # 等待 JavaScript 加载完成
        await page.wait_for_load_state("networkidle")
        
        # 等待特定元素出现
        await page.wait_for_selector("table tbody tr", timeout=15000)
        
        # 提取数据
        data = await scraper.extract_table()
        
        print(f"✅ 提取 {data.total_rows} 行数据")
        scraper.save_to_csv("dynamic_data.csv")


# ==========================================
# 主菜单
# ==========================================

async def main():
    """主菜单"""
    examples = {
        "1": ("按钮分页", example_button_pagination),
        "2": ("页码分页", example_number_pagination),
        "3": ("URL 参数分页", example_url_pagination),
        "4": ("自定义选择器", example_custom_selectors),
        "5": ("GitHub Trending 实战", example_github_trending),
        "6": ("动态加载表格", example_dynamic_table)
    }
    
    print("\n" + "="*60)
    print("🎓 分页表格抓取示例")
    print("="*60)
    print("\n可用示例:")
    for key, (name, _) in examples.items():
        print(f"   {key}. {name}")
    
    choice = input("\n选择示例 (1-6): ").strip()
    
    if choice in examples:
        name, func = examples[choice]
        print(f"\n🚀 运行示例: {name}")
        await func()
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    asyncio.run(main())