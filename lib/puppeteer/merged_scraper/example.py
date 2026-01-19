"""
合并抓取器使用示例
Example Usage of Merged Scraper
"""

import asyncio
import sys
from pathlib import Path

# 添加lib到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from browser import BrowserManager
from puppeteer.universal_scraper import create_scraper_config
from puppeteer.merged_scraper import (
    MergedScraper,
    MergedScraperConfig,
    create_merged_scraper_config
)


async def example_1_basic_usage():
    """
    示例1：基础使用 - 抓取文章列表和详情页
    """
    print("\n" + "="*60)
    print("示例1：基础使用 - 文章列表 + 详情页")
    print("="*60)
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        page = await bm.get_or_create_page()
        
        # 配置列表页抓取
        list_config = create_scraper_config(
            url="https://segmentfault.com/",
            fields={
                "标题": "h3 a.text-body",
                "摘要": ".excerpt",
                "投票": ".num-card .font-size-16",
                "详情链接": "h3 a.text-body"  # 这个字段会被用来提取href
            },
            container_selector=".list-group-item",
            next_button_selector="a.page-link[rel='next']",
            delay=3.0,
            max_pages=2  # 只抓2页作为示例
        )
        
        # 配置详情页抓取
        merged_config = create_merged_scraper_config(
            list_config=list_config,
            detail_fields={
                "文章内容": ".article-content",
                "作者": ".user-info .name",
                "发布时间": ".article-meta time",
                "浏览量": ".article-meta .views"
            },
            detail_container_selector=".article-content",  # 用于等待详情页加载
            detail_url_field="详情链接",  # 对应列表配置中的字段名
            detail_url_attribute="href",
            navigation_mode="go_back",
            back_wait_time=2.0,
            detail_page_wait_time=2.0,
            max_detail_retries=2,
            continue_on_error=True
        )
        
        # 创建抓取器并执行
        scraper = MergedScraper(page, merged_config)
        data = await scraper.scrape()
        
        # 保存数据
        scraper.save_to_json("example_1_merged_data.json")
        
        # 查看部分数据
        if data:
            print(f"\n预览第一条数据：")
            print(f"列表数据: {data[0]['list_data']}")
            print(f"详情数据: {data[0]['detail_data']}")
            print(f"元数据: {data[0]['metadata']}")


async def example_2_opened_page():
    """
    示例2：在已打开的页面上抓取
    """
    print("\n" + "="*60)
    print("示例2：在已打开的页面上抓取")
    print("="*60)
    
    async with BrowserManager(mode="connect") as bm:
        # 列出所有打开的页面
        pages_info = await bm.list_all_pages()
        print(f"\n当前打开的标签页 ({len(pages_info)} 个):")
        for i, info in enumerate(pages_info, 1):
            print(f"{i}. {info['title'][:50]}")
            print(f"   {info['url']}\n")
        
        if not pages_info:
            print("❌ 没有找到打开的标签页")
            return
        
        # 连接到目标页面
        page = await bm.get_or_create_page(target_url="segmentfault.com")
        
        if not page:
            print("❌ 未找到目标页面")
            return
        
        print(f"✅ 连接到页面: {page.url}")
        
        # 配置列表页
        list_config = create_scraper_config(
            url=page.url,  # 使用当前页面URL
            fields={
                "标题": "h3 a.text-body",
                "详情链接": "h3 a.text-body"
            },
            container_selector=".list-group-item",
            next_button_selector="a.page-link[rel='next']",
            delay=2.0,
            max_pages=1  # 只抓1页
        )
        
        # 配置详情页
        merged_config = create_merged_scraper_config(
            list_config=list_config,
            detail_fields={
                "内容": ".article-content",
                "作者": ".user-info .name"
            },
            detail_container_selector=".article-content",
            detail_url_field="详情链接",
            detail_url_attribute="href",
            continue_on_error=True
        )
        
        # 从当前页面开始抓取
        scraper = MergedScraper(page, merged_config)
        data = await scraper.scrape_from_current_page()
        
        scraper.save_to_json("example_2_merged_data.json")


async def example_3_error_handling():
    """
    示例3：错误处理和容错
    """
    print("\n" + "="*60)
    print("示例3：错误处理和容错")
    print("="*60)
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        page = await bm.get_or_create_page()
        
        # 配置列表页
        list_config = create_scraper_config(
            url="https://segmentfault.com/",
            fields={
                "标题": "h3 a.text-body",
                "详情链接": "h3 a.text-body"
            },
            container_selector=".list-group-item",
            delay=2.0,
            max_pages=1
        )
        
        # 配置详情页（故意使用可能失败的选择器）
        merged_config = create_merged_scraper_config(
            list_config=list_config,
            detail_fields={
                "内容": ".article-content",
                "不存在的字段": ".non-existent-selector"  # 故意设置不存在的选择器
            },
            detail_container_selector=".article-content",
            detail_url_field="详情链接",
            detail_url_attribute="href",
            max_detail_retries=2,  # 重试2次
            continue_on_error=True  # 失败后继续
        )
        
        scraper = MergedScraper(page, merged_config)
        data = await scraper.scrape()
        
        # 查看统计信息
        stats = scraper.get_stats()
        print(f"\n统计信息：")
        print(f"成功: {stats['successful_details']}")
        print(f"失败: {stats['failed_details']}")
        print(f"跳过: {stats['skipped_details']}")
        
        scraper.save_to_json("example_3_merged_data.json")


async def example_4_custom_config():
    """
    示例4：高级配置
    """
    print("\n" + "="*60)
    print("示例4：高级配置")
    print("="*60)
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        page = await bm.get_or_create_page()
        
        # 使用MergedScraperConfig类进行详细配置
        from puppeteer.universal_scraper import FieldConfig, ScraperConfig
        
        list_config = ScraperConfig(
            url="https://segmentfault.com/",
            fields=[
                FieldConfig(name="标题", selector="h3 a.text-body"),
                FieldConfig(name="详情链接", selector="h3 a.text-body", attribute="href")
            ],
            container_selector=".list-group-item",
            next_button_selector="a.page-link[rel='next']",
            delay=2.0,
            max_pages=1
        )
        
        merged_config = MergedScraperConfig(
            list_config=list_config,
            detail_fields=[
                FieldConfig(name="内容", selector=".article-content"),
                FieldConfig(name="标签", selector=".tag", multiple=True)  # 提取多个标签
            ],
            detail_container_selector=".article-content",
            detail_url_field="详情链接",
            detail_url_attribute="href",
            back_wait_time=3.0,  # 返回列表页等待更长时间
            detail_page_wait_time=3.0,  # 详情页等待更长时间
            max_detail_retries=3,  # 重试3次
            continue_on_error=True,
            skip_invalid_urls=True,  # 跳过无效URL
            verify_list_page_state=True,  # 验证列表页状态
            save_partial_results=True  # 保存部分结果
        )
        
        scraper = MergedScraper(page, merged_config)
        data = await scraper.scrape()
        
        scraper.save_to_json("example_4_merged_data.json")


async def main():
    """主函数"""
    print("\n🎯 合并抓取器示例")
    print("选择要运行的示例：")
    print("1. 基础使用")
    print("2. 在已打开的页面上抓取（需要先启动Chrome）")
    print("3. 错误处理")
    print("4. 高级配置")
    
    choice = input("\n请输入选项 (1-4): ").strip()
    
    if choice == "1":
        await example_1_basic_usage()
    elif choice == "2":
        print("\n⚠️ 请确保已启动Chrome:")
        print("   chrome.exe --remote-debugging-port=9222")
        print("   并打开目标页面（如 SegmentFault）")
        input("\n按回车继续...")
        await example_2_opened_page()
    elif choice == "3":
        await example_3_error_handling()
    elif choice == "4":
        await example_4_custom_config()
    else:
        print("无效的选项")


if __name__ == "__main__":
    asyncio.run(main())
