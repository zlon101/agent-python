"""
在已打开的页面上进行分页抓取
演示如何连接到已打开的页面并进行分页数据采集
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from browser import BrowserManager
from puppeteer import UniversalScraper, create_scraper_config


async def scrape_opened_page_with_pagination():
    """
    场景：在已打开的页面上进行分页抓取
    
    步骤：
    1. 连接到已打开的 Chrome
    2. 查找目标页面
    3. 在当前页面上进行分页抓取
    """
    print("\n" + "="*60)
    print("🎯 在已打开的页面上进行分页抓取")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        # 列出所有打开的页面
        pages_info = await bm.list_all_pages()
        
        print(f"📋 当前打开的标签页 ({len(pages_info)} 个):\n")
        for i, info in enumerate(pages_info, 1):
            print(f"{i}. {info['title'][:60]}")
            print(f"   {info['url']}\n")
        
        if not pages_info:
            print("❌ 没有找到打开的标签页")
            return
        
        # 连接到已打开的 SegmentFault 页面
        print("🔍 查找 SegmentFault 页面...\n")
        page = await bm.get_or_create_page(target_url="devops.aliyun.com")
        
        if not page:
            print("❌ 未找到 SegmentFault 页面")
            return
        
        print(f"✅ 连接到页面: {page.url}")
        print(f"   标题: {await page.title()}\n")
        
        # 配置抓取器（支持分页）
        config = create_scraper_config(
            url=page.url,  # 使用当前页面的 URL
            fields={
                "标题": ".yunxiao-projex-workitem-title",
                "人天": ".TextAndNumberModifier--statusName--yXxCXqU"
            },
            container_selector=".next-table-body tr.next-table-row",
            next_button_selector=".next-btn.next-pagination-item.next-next",  # 下一页按钮
            delay=4.0,  # 每页等待3秒
            max_pages=2  # 抓取2页
        )
        
        # 创建抓取器
        scraper = UniversalScraper(page, config)
        
        # ⭐ 关键：使用 scrape_from_current_page() 而不是 scrape()
        # 这样不会重新导航，直接在当前页面上抓取
        print("🚀 开始分页抓取...\n")
        data = await scraper.scrape_from_current_page()
        
        # 保存数据
        if data:
            scraper.save_to_json("test_云效任务类型人天统计.json")
            print(f"\n✅ 成功!")
            print(f"   总条数: {len(data)}")
        else:
            print("\n⚠️ 未抓取到数据")


async def main():
    print("\n⚠️ 准备工作:")
    print("   1. 启动 Chrome: chrome.exe --remote-debugging-port=9222")
    print("   2. 打开要抓取的网页（如 SegmentFault 搜索结果页）")
    
    try:
        await scrape_opened_page_with_pagination()
    except ConnectionError as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n💡 解决方法:")
        print("   1. 启动 Chrome: chrome.exe --remote-debugging-port=9222")
        print("   2. 重新运行")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
