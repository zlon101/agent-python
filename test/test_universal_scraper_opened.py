"""
测试浏览器管理器的新功能 - 查找和连接到指定 URL 的标签页
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from browser import BrowserManager


async def test_find_page_by_url():
    """测试查找指定 URL 的页面"""
    print("\n" + "="*60)
    print("🧪 测试查找指定 URL 的标签页")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        # 列出所有打开的页面
        pages_info = await bm.list_all_pages()
        
        print(f"📋 当前打开的标签页 ({len(pages_info)} 个):\n")
        for i, info in enumerate(pages_info, 1):
            print(f"{i}. {info['title']}")
            print(f"   URL: {info['url']}")
            print(f"   Context: {info['context_index']}, Page: {info['page_index']}\n")
        
        if not pages_info:
            print("⚠️ 没有找到打开的标签页")
            print("💡 请先在 Chrome 中打开一些网页")
            return
        
        # 测试查找页面
        print("\n" + "="*60)
        print("🔍 测试查找功能")
        print("="*60 + "\n")
        
        # 测试 1: 部分匹配
        test_urls = [
            "segmentfault.com",
            "github.com",
            "google.com"
        ]
        
        for url in test_urls:
            print(f"查找包含 '{url}' 的页面...")
            page = await bm.find_page_by_url(url)
            if page:
                print(f"✅ 找到: {page.url}")
                print(f"   标题: {await page.title()}\n")
            else:
                print(f"❌ 未找到\n")
        
        # 测试 2: 精确匹配
        if pages_info:
            exact_url = pages_info[0]['url']
            print(f"精确查找: {exact_url}...")
            page = await bm.find_page_by_url(exact_url, exact_match=True)
            if page:
                print(f"✅ 精确匹配成功\n")
            else:
                print(f"❌ 精确匹配失败\n")


async def test_get_page_with_url():
    """测试 get_or_create_page 的新参数"""
    print("\n" + "="*60)
    print("🧪 测试 get_or_create_page(target_url)")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        # 列出当前页面
        pages_info = await bm.list_all_pages()
        print(f"📋 当前有 {len(pages_info)} 个标签页\n")
        
        # 场景 1: 查找已存在的页面
        print("场景 1: 查找已存在的 SegmentFault 页面")
        print("-" * 60)
        
        page = await bm.get_or_create_page(target_url="segmentfault.com")
        print(f"返回的页面: {page.url}")
        print(f"标题: {await page.title()}\n")
        
        # 场景 2: 查找不存在的页面（回退到默认行为）
        print("场景 2: 查找不存在的页面")
        print("-" * 60)
        
        page = await bm.get_or_create_page(target_url="非常罕见的网址xyz123")
        print(f"返回的页面: {page.url}")
        print(f"标题: {await page.title()}\n")
        
        # 场景 3: 不指定 URL（原始行为）
        print("场景 3: 不指定 URL（使用默认行为）")
        print("-" * 60)
        
        page = await bm.get_or_create_page()
        print(f"返回的页面: {page.url}")
        print(f"标题: {await page.title()}\n")



# 连接到已经打开的页面，解析页面数据
async def test_with_scraper():
    """测试在抓取器中使用新功能"""
    print("\n" + "="*60)
    print("🧪 在抓取器中使用 - 直接在已打开的标签页操作")
    print("="*60 + "\n")
    
    from puppeteer import UniversalScraper, create_scraper_config
    
    async with BrowserManager(mode="connect") as bm:
        # 连接到已经打开的 SegmentFault 页面
        page = await bm.get_or_create_page(target_url="segmentfault.com")
        
        print(f"✅ 连接到页面: {page.url}\n")
        
        # 直接在这个页面上执行抓取
        config = create_scraper_config(
            url=page.url,  # 使用当前页面的 URL
            fields={
                # "标题": "h3 a.text-body",
                # "投票数": ".num-card .font-size-16"
                "标题": "h5",
                "时间": ".mb-0.font-size-14"
            },
            container_selector=".row div.list-group li",
            delay=2.0
        )
        
        scraper = UniversalScraper(page, config)
        
        # 不需要导航，直接抓取当前页面
        print("🔍 抓取当前页面数据...")
        data = await scraper.scrape_from_current_page()
        scraper.save_to_json("test_解析已经打开的页面.json")
        
        
        print(f"\n✅ 成功抓取 {len(data)} 条数据")
        print(f"\n📊 前3条数据:")
        for i, item in enumerate(data[:3], 1):
            print(f"\n{i}. {item}")


"""交互式页面查找器"""
async def interactive_page_finder():
    print("\n" + "="*60)
    print("🔍 交互式页面查找器")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        while True:
            # 列出所有页面
            pages_info = await bm.list_all_pages()
            
            print(f"\n📋 当前打开的标签页 ({len(pages_info)} 个):\n")
            for i, info in enumerate(pages_info, 1):
                status = "❌ 已关闭" if info['is_closed'] else "✅ 活跃"
                print(f"{i}. [{status}] {info['title'][:50]}")
                print(f"   {info['url']}\n")
            
            # 用户输入
            print("\n操作选项:")
            print("  1. 输入 URL 关键词查找页面")
            print("  2. 输入 'refresh' 刷新列表")
            print("  3. 输入 'quit' 退出")
            
            choice = input("\n> ").strip()
            
            if choice.lower() == 'quit':
                break
            elif choice.lower() == 'refresh':
                continue
            else:
                # 查找页面
                page = await bm.find_page_by_url(choice)
                if page:
                    print(f"\n✅ 找到页面!")
                    print(f"   URL: {page.url}")
                    print(f"   标题: {await page.title()}")
                    
                    # 询问是否在这个页面上操作
                    action = input("\n是否切换到此页面? (y/n): ").strip()
                    if action.lower() == 'y':
                        await page.bring_to_front()
                        print("✅ 已切换到该页面")
                else:
                    print(f"\n❌ 未找到包含 '{choice}' 的页面")


async def main():
    """主菜单"""
    tests = {
        "1": ("查找指定 URL 的页面", test_find_page_by_url),
        "2": ("测试 get_or_create_page 新功能", test_get_page_with_url),
        "3": ("在抓取器中使用", test_with_scraper),
        "4": ("交互式页面查找器", interactive_page_finder)
    }
    
    print("\n" + "="*60)
    print("🧪 浏览器管理器新功能测试")
    print("="*60)
    print("\n可用测试:")
    for key, (name, _) in tests.items():
        print(f"   {key}. {name}")
    
    print("\n⚠️ 注意: 这些测试需要在 connect 模式下运行")
    print("   请先启动 Chrome: chrome.exe --remote-debugging-port=9222")
    print("   并打开一些网页（如 SegmentFault、GitHub 等）\n")
    
    choice = input("选择测试 (1-4): ").strip()
    
    if choice in tests:
        name, func = tests[choice]
        print(f"\n🚀 运行测试: {name}")
        try:
            await func()
        except ConnectionError as e:
            print(f"\n❌ 连接失败: {e}")
            print("\n💡 解决方法:")
            print("   1. 启动 Chrome: chrome.exe --remote-debugging-port=9222")
            print("   2. 重新运行测试")
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    asyncio.run(main())
