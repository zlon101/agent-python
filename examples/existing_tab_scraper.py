"""
实战示例：使用新功能在已打开的标签页上直接抓取数据
场景：用户已经在浏览器中打开了 SegmentFault，想直接抓取数据
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from browser import BrowserManager
from puppeteer import UniversalScraper, create_scraper_config


async def scrape_from_existing_tab():
    """
    从已打开的标签页抓取数据
    
    优势：
    1. 无需重新加载页面，节省时间
    2. 保留用户的登录状态和操作历史
    3. 可以继续用户当前的浏览位置
    """
    print("\n" + "="*60)
    print("🎯 实战：从已打开的标签页抓取数据")
    print("="*60 + "\n")
    
    try:
        async with BrowserManager(mode="connect") as bm:
            # 步骤 1: 显示所有打开的标签页
            print("📋 第一步：查看所有打开的标签页\n")
            pages_info = await bm.list_all_pages()
            
            if not pages_info:
                print("❌ 没有找到打开的标签页")
                print("\n💡 解决方法:")
                print("   1. 启动 Chrome: chrome.exe --remote-debugging-port=9222")
                print("   2. 打开一些网页（如 SegmentFault）")
                print("   3. 重新运行此脚本")
                return
            
            print(f"找到 {len(pages_info)} 个标签页:\n")
            for i, info in enumerate(pages_info, 1):
                print(f"{i}. {info['title'][:60]}")
                print(f"   {info['url']}\n")
            
            # 步骤 2: 查找 SegmentFault 页面
            print("🔍 第二步：查找 SegmentFault 页面\n")
            page = await bm.get_or_create_page(target_url="segmentfault.com")
            
            print(f"✅ 连接到页面: {page.url}")
            print(f"   标题: {await page.title()}\n")
            
            # 步骤 3: 配置抓取器
            print("⚙️  第三步：配置抓取器\n")
            config = create_scraper_config(
                url=page.url,  # 使用当前页面的 URL
                fields={
                    "标题": "h3 a.text-body",
                    "投票数量": ".num-card .font-size-16",
                    "阅读数量": ".num-card.text-secondary .font-size-16"
                },
                container_selector=".list-group-item",
                delay=2.0
            )
            
            print("配置完成:")
            print(f"   URL: {config.url}")
            print(f"   容器: {config.container_selector}")
            print(f"   字段数: {len(config.fields)}\n")
            
            # 步骤 4: 执行抓取
            print("🚀 第四步：抓取当前页面数据\n")
            scraper = UniversalScraper(page, config)
            
            # 直接抓取当前页面（不需要导航，节省时间）
            data = await scraper.scrape_current_page()
            
            # 步骤 5: 显示结果
            print("\n" + "="*60)
            print("✅ 抓取完成")
            print("="*60)
            print(f"   总条目: {len(data)}")
            
            if data:
                print(f"\n📊 数据示例（前3条）:\n")
                for i, item in enumerate(data[:3], 1):
                    print(f"{i}. 标题: {item.get('标题', 'N/A')}")
                    print(f"   投票: {item.get('投票数量', 'N/A')}")
                    print(f"   阅读: {item.get('阅读数量', 'N/A')}\n")
                
                # 保存数据
                scraper.save_to_json("existing_tab_data.json")
            else:
                print("\n⚠️ 未抓取到数据，可能需要调整选择器")
            
    except ConnectionError as e:
        print(f"\n❌ 连接失败: {e}")
        print("\n💡 解决方法:")
        print("   1. 启动 Chrome 并开启远程调试")
        print("      chrome.exe --remote-debugging-port=9222")
        print("   2. 重新运行此脚本")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


async def scrape_multiple_tabs():
    """
    批量抓取多个已打开的标签页
    """
    print("\n" + "="*60)
    print("🎯 实战：批量抓取多个标签页")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        # 定义要抓取的网站配置
        site_configs = {
            "segmentfault.com": {
                "fields": {
                    "标题": "h3 a.text-body",
                    "投票": ".num-card .font-size-16"
                },
                "container": ".list-group-item"
            },
            "github.com/trending": {
                "fields": {
                    "项目名": "h2 a",
                    "描述": "p.col-9"
                },
                "container": "article.Box-row"
            }
        }
        
        results = {}
        
        for url_pattern, config_data in site_configs.items():
            print(f"🔍 查找 {url_pattern} 页面...")
            
            page = await bm.find_page_by_url(url_pattern)
            
            if page:
                print(f"✅ 找到: {page.url}")
                print(f"   抓取数据...\n")
                
                # 配置抓取器
                config = create_scraper_config(
                    url=page.url,
                    fields=config_data["fields"],
                    container_selector=config_data["container"],
                    delay=2.0
                )
                
                scraper = UniversalScraper(page, config)
                data = await scraper.scrape_current_page()
                
                results[url_pattern] = data
                print(f"   ✓ 抓取了 {len(data)} 条数据\n")
            else:
                print(f"❌ 未找到页面\n")
        
        # 显示汇总
        print("="*60)
        print("📊 抓取汇总")
        print("="*60)
        for url, data in results.items():
            print(f"{url}: {len(data)} 条数据")


async def smart_scraper():
    """
    智能抓取器：自动判断是使用已打开的页面还是新打开
    """
    print("\n" + "="*60)
    print("🎯 实战：智能抓取器")
    print("="*60 + "\n")
    
    target_url = "https://segmentfault.com/"
    
    async with BrowserManager(mode="connect") as bm:
        print(f"🎯 目标: {target_url}\n")
        
        # 尝试查找已打开的页面
        page = await bm.get_or_create_page(target_url="segmentfault.com")
        
        # 检查 URL 是否匹配
        current_url = page.url.lower()
        
        if "segmentfault.com" in current_url:
            print("✅ 使用已打开的页面")
            print(f"   当前 URL: {page.url}")
            print("   ⚡ 节省了页面加载时间\n")
        else:
            print("⚠️ 页面不匹配，需要导航")
            print(f"   当前 URL: {page.url}")
            print(f"   目标 URL: {target_url}")
            print("   正在导航...\n")
            await page.goto(target_url)
            await asyncio.sleep(3)
            print("✅ 导航完成\n")
        
        # 继续抓取
        config = create_scraper_config(
            url=target_url,
            fields={
                "标题": "h3 a.text-body"
            },
            container_selector=".list-group-item",
            delay=2.0
        )
        
        scraper = UniversalScraper(page, config)
        data = await scraper.scrape_current_page()
        
        print(f"✅ 抓取完成: {len(data)} 条数据")


async def interactive_tab_scraper():
    """
    交互式：让用户选择要抓取的标签页
    """
    print("\n" + "="*60)
    print("🎯 实战：交互式标签页抓取")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        # 列出所有标签页
        pages_info = await bm.list_all_pages()
        
        if not pages_info:
            print("❌ 没有找到打开的标签页")
            return
        
        print("📋 可用的标签页:\n")
        for i, info in enumerate(pages_info, 1):
            print(f"{i}. {info['title'][:60]}")
            print(f"   {info['url']}\n")
        
        # 用户选择
        try:
            choice = int(input("选择要抓取的标签页 (输入编号): ")) - 1
            
            if 0 <= choice < len(pages_info):
                target_url = pages_info[choice]['url']
                
                # 连接到选中的页面
                page = await bm.find_page_by_url(target_url, exact_match=True)
                
                if page:
                    print(f"\n✅ 已连接到: {await page.title()}")
                    print(f"   URL: {page.url}\n")
                    
                    # 用户配置抓取参数
                    print("请配置抓取参数:")
                    container = input("容器选择器 (如 .list-group-item): ").strip()
                    field_selector = input("标题选择器 (如 h3 a): ").strip()
                    
                    if container and field_selector:
                        config = create_scraper_config(
                            url=page.url,
                            fields={"标题": field_selector},
                            container_selector=container,
                            delay=2.0
                        )
                        
                        scraper = UniversalScraper(page, config)
                        print("\n🚀 开始抓取...\n")
                        data = await scraper.scrape_current_page()
                        
                        print(f"✅ 抓取完成: {len(data)} 条数据")
                        
                        if data:
                            print("\n前3条数据:")
                            for i, item in enumerate(data[:3], 1):
                                print(f"{i}. {item}")
                    else:
                        print("❌ 配置不完整")
                else:
                    print("❌ 无法连接到页面")
            else:
                print("❌ 无效选择")
        except ValueError:
            print("❌ 请输入有效的数字")
        except Exception as e:
            print(f"❌ 错误: {e}")


async def main():
    """主菜单"""
    examples = {
        "1": ("从已打开标签页抓取", scrape_from_existing_tab),
        "2": ("批量抓取多个标签页", scrape_multiple_tabs),
        "3": ("智能抓取器", smart_scraper),
        "4": ("交互式标签页抓取", interactive_tab_scraper)
    }
    
    print("\n" + "="*60)
    print("🎓 新功能实战示例")
    print("="*60)
    print("\n可用示例:")
    for key, (name, _) in examples.items():
        print(f"   {key}. {name}")
    
    print("\n⚠️ 准备工作:")
    print("   1. 启动 Chrome: chrome.exe --remote-debugging-port=9222")
    print("   2. 打开一些网页（SegmentFault、GitHub 等）")
    print("   3. 选择一个示例运行\n")
    
    choice = input("选择示例 (1-4): ").strip()
    
    if choice in examples:
        name, func = examples[choice]
        print(f"\n🚀 运行示例: {name}")
        await func()
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    asyncio.run(main())
