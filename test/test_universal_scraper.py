"""
快速测试通用抓取器
验证基本功能是否正常
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from browser import BrowserManager
from puppeteer import UniversalScraper, create_scraper_config

load_dotenv()
cdp_url = os.getenv("CDP_URL")

async def test_basic_scraping():
    """测试基础抓取功能"""
    print("\n" + "="*60)
    print("🧪 测试通用抓取器 - 基础功能")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect", cdp_url=cdp_url, headless=False) as bm:
        page = await bm.get_or_create_page()
        
        # 测试配置
        config = create_scraper_config(
            url="https://segmentfault.com/",
            fields={
                "标题": "h3 a.text-body",
                "投票数": ".num-card .font-size-16",
                "阅读数": ".reads1 .font-size-16"
            },
            container_selector=".list-card-bg .list-group.list-group-flush .list-group-item",
            delay=3.0
        )
        
        print("📋 配置:")
        print(f"   URL: {config.url}")
        print(f"   容器: {config.container_selector}")
        print(f"   字段: {[f.name for f in config.fields]}")
        print(f"   延迟: {config.delay}s\n")
        
        # 执行抓取
        print("🚀 开始抓取...\n")
        scraper = UniversalScraper(page, config)
        data = await scraper.scrape()
        
        # 验证结果
        print("\n" + "="*60)
        print("📊 测试结果")
        print("="*60)
        
        if data:
            print(f"✅ 成功抓取 {len(data)} 条数据")
            print(f"\n📄 第一条数据:")
            for key, value in data[0].items():
                print(f"   {key}: {value}")
            
            # 保存测试数据
            scraper.save_to_json("test_output.json")
        else:
            print("❌ 抓取失败，未获取到数据")
        
        print("="*60 + "\n")


async def test_pagination():
    """测试分页功能"""
    print("\n" + "="*60)
    print("🧪 测试通用抓取器 - 分页功能")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        page = await bm.get_or_create_page()
        
        config = create_scraper_config(
            url="https://segmentfault.com/",
            fields={
                "标题": "h3 a.text-body",
                "投票数": ".num-card .font-size-16",
                "阅读数": ".reads1 .font-size-16"
            },
            container_selector=".list-card-bg .list-group.list-group-flush .list-group-item",
            next_button_selector=".bg-white .page-item:last-child .page-link",
            delay=4.0,
            max_pages=2
        )
        
        print("📋 分页配置:")
        print(f"   下一页按钮: {config.next_button_selector}")
        print(f"   最大页数: {config.max_pages}")
        print(f"   延迟: {config.delay}s\n")
        
        print("🚀 开始分页抓取...\n")
        scraper = UniversalScraper(page, config)
        data = await scraper.scrape()
        
        print("\n" + "="*60)
        print("📊 分页测试结果")
        print("="*60)
        
        if data:
            print(f"✅ 成功抓取 {len(data)} 条数据（跨 {config.max_pages} 页）")
            scraper.save_to_json("test_pagination.json")
        else:
            print("❌ 分页抓取失败")
        
        print("="*60 + "\n")


async def main():
    """主测试函数"""
    tests = {
        "1": ("基础抓取", test_basic_scraping),
        "2": ("分页抓取", test_pagination),
        "3": ("全部测试", None)
    }
    
    print("\n" + "="*60)
    print("🧪 通用抓取器测试")
    print("="*60)
    print("\n可用测试:")
    for key, (name, _) in tests.items():
        print(f"   {key}. {name}")
    
    choice = input("\n选择测试 (1-3): ").strip()
    
    if choice == "3":
        for name, func in [(n, f) for n, f in tests.values() if f]:
            await func()
            await asyncio.sleep(2)
    elif choice in tests and tests[choice][1]:
        name, func = tests[choice]
        await func()
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    asyncio.run(main())
