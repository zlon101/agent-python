"""
测试 GitHub Trending 抓取修复
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from browser import BrowserManager
from puppeteer import get_browser_tools

load_dotenv()


async def test_github_trending():
    """测试 GitHub Trending 专用工具"""
    print("\n" + "="*60)
    print("🧪 测试 GitHub Trending 抓取修复")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        browser = bm.get_browser()
        
        # 获取工具（包含新的 scrape_github_trending）
        tools = get_browser_tools(browser)
        
        print(f"✅ 加载了 {len(tools)} 个工具:")
        for tool in tools:
            print(f"   - {tool.name}")
        
        # 验证新工具存在
        github_tool = next((t for t in tools if t.name == "scrape_github_trending"), None)
        if github_tool:
            print(f"\n✅ 找到 GitHub Trending 工具!")
            print(f"   描述: {github_tool.description}\n")
        else:
            print("\n❌ 未找到 GitHub Trending 工具\n")
            return
        
        # 导航到 GitHub Trending
        page = await bm.get_or_create_page()
        print("🌐 访问 GitHub Trending...")
        await page.goto("https://github.com/trending")
        await asyncio.sleep(3)
        
        # 直接调用工具
        print("🔧 调用 scrape_github_trending 工具...\n")
        result = await github_tool.ainvoke({
            "filename": "github_trending_test.json",
            "limit": 10
        })
        
        print(f"\n📊 结果: {result}")
        
        # 验证文件
        import json
        if os.path.exists("github_trending_test.json"):
            with open("github_trending_test.json", "r", encoding="utf-8") as f:
                data = json.load(f)
            
            print(f"\n✅ 文件验证:")
            print(f"   总项目数: {data['metadata']['total_repositories']}")
            print(f"   数据条目: {len(data['data'])}")
            
            if data['data']:
                print(f"\n📄 第一个项目:")
                first = data['data'][0]
                for key, value in first.items():
                    print(f"   {key}: {value}")
        else:
            print("\n❌ 文件未生成")


if __name__ == "__main__":
    asyncio.run(test_github_trending())
