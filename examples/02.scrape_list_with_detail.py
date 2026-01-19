"""
在已打开的页面上执行列表+详情页合并抓取
测试文件
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))

from browser import BrowserManager
from puppeteer.universal_scraper import create_scraper_config
from puppeteer.merged_scraper import MergedScraper, create_merged_scraper_config


async def test_merged_scraper():
    """
    测试场景：在已打开的页面上进行列表+详情页合并抓取
    
    准备工作：
    1. 启动 Chrome: chrome.exe --remote-debugging-port=9222
    2. 打开要抓取的列表页（如 SegmentFault 搜索结果）
    """
    print("\n" + "="*60)
    print("🎯 测试：列表页+详情页合并抓取")
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
            print("\n💡 请先启动Chrome并打开目标页面:")
            print("   1. chrome.exe --remote-debugging-port=9222")
            print("   2. 打开列表页（如 SegmentFault）")
            return
        
        # 连接到目标页面
        print("🔍 查找目标页面...\n")
        page = await bm.get_or_create_page(target_url="segmentfault.com")
        
        if not page:
            print("❌ 未找到 SegmentFault 页面")
            print("\n💡 请在Chrome中打开 https://segmentfault.com/")
            return
        
        print(f"✅ 连接到页面: {page.url}")
        print(f"   标题: {await page.title()}\n")
        
        # ========== 配置列表页抓取 ==========
        list_config = create_scraper_config(
            url=page.url,  # 使用当前页面的URL
            fields={
                "标题": "h3 a.text-body",
                "摘要": ".excerpt",
                "投票数": ".num-card .font-size-16",
                "详情链接": "h3 a.text-body"  # 用于提取详情页URL
            },
            container_selector=".list-group-item",
            next_button_selector="a.page-link[rel='next']",  # 下一页按钮
            delay=3.0,
            max_pages=2  # 测试抓取2页
        )
        
        # ========== 配置详情页抓取 ==========
        merged_config = create_merged_scraper_config(
            list_config=list_config,
            detail_fields={
                "文章内容": ".article-content",
                "作者": ".user-info .name a",
                "发布时间": ".article-meta time",
                "浏览量": ".article-meta .views",
                "标签": ".taglist--inline .tag"
            },
            detail_container_selector=".article-content",  # 等待详情页容器加载
            detail_url_field="详情链接",  # 对应列表配置中的字段
            detail_url_attribute="href",  # 提取href属性作为URL
            navigation_mode="go_back",  # 使用返回按钮
            back_wait_time=2.0,  # 返回列表页等待2秒
            detail_page_wait_time=2.0,  # 详情页加载等待2秒
            max_detail_retries=2,  # 失败重试2次
            continue_on_error=True  # 单个详情页失败后继续
        )
        
        # ========== 执行抓取 ==========
        scraper = MergedScraper(page, merged_config)
        
        # 从当前页面开始抓取（不重新导航）
        data = await scraper.scrape_from_current_page()
        
        # ========== 保存数据 ==========
        if data:
            scraper.save_to_json("test_merged_data.json")
            
            # 显示部分数据预览
            print(f"\n{'='*60}")
            print(f"📊 数据预览（前2条）")
            print(f"{'='*60}")
            
            for i, item in enumerate(data[:2], 1):
                print(f"\n第 {i} 条:")
                print(f"  列表数据:")
                for key, value in item['list_data'].items():
                    print(f"    {key}: {str(value)[:50]}")
                print(f"  详情数据:")
                for key, value in item['detail_data'].items():
                    print(f"    {key}: {str(value)[:50]}")
                print(f"  状态: {item['metadata']['scrape_status']}")
        else:
            print("\n⚠️ 未抓取到数据")


async def main():
    print("\n⚠️ 准备工作:")
    print("   1. 启动 Chrome: chrome.exe --remote-debugging-port=9222")
    print("   2. 打开要抓取的网页（如 SegmentFault）")
    print("   3. 确保页面已完全加载")
    
    input("\n准备好后按回车开始测试...")
    
    try:
        await test_merged_scraper()
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
