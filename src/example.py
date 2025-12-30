"""
使用示例 - 展示不同的浏览器 Agent 用法
"""

import asyncio
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from browser import BrowserManager
from custom_agent.agent_config import create_custom_agent
from puppeteer.puppeteer_tools import get_browser_tools
from custom_agent.agent_tools import add

load_dotenv()


# ==========================================
# 示例 1: 启动新浏览器
# ==========================================

async def example_launch_browser():
    """示例：启动新的 Chromium 浏览器"""
    print("\n" + "="*60)
    print("📌 Example 1: Launch New Browser")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        browser = bm.get_browser()
        tools = get_browser_tools(browser)
        agent = create_custom_agent(tools=tools)
        
        task = "Go to https://www.google.com and take a screenshot named 'google.png'"
        result = await agent.ainvoke({"messages": [HumanMessage(content=task)]})
        
        print(f"\n✅ Result: {result['messages'][-1].content}")


# ==========================================
# 示例 2: 连接已有 Chrome
# ==========================================

async def example_connect_chrome():
    """示例：连接到已有的 Chrome 实例"""
    print("\n" + "="*60)
    print("📌 Example 2: Connect to Existing Chrome")
    print("="*60 + "\n")
    
    try:
        async with BrowserManager(mode="connect") as bm:
            browser = bm.get_browser()
            tools = get_browser_tools(browser)
            agent = create_custom_agent(tools=tools)
            
            task = "Get the current page title and URL"
            result = await agent.ainvoke({"messages": [HumanMessage(content=task)]})
            
            print(f"\n✅ Result: {result['messages'][-1].content}")
    
    except ConnectionError as e:
        print(f"❌ {e}")
        print("\n💡 Start Chrome first with:")
        print("   chrome.exe --remote-debugging-port=9222")


# ==========================================
# 示例 3: 指定 CDP URL
# ==========================================

async def example_custom_cdp():
    """示例：使用自定义 CDP URL"""
    print("\n" + "="*60)
    print("📌 Example 3: Custom CDP URL")
    print("="*60 + "\n")
    
    cdp_url = "http://localhost:9222"
    
    try:
        async with BrowserManager(mode="connect", cdp_url=cdp_url) as bm:
            info = bm.get_info()
            print(f"📊 Browser Info: {info}")
    
    except ConnectionError as e:
        print(f"❌ {e}")


# ==========================================
# 示例 4: 多任务执行
# ==========================================

async def example_multiple_tasks():
    """示例：在同一个浏览器会话中执行多个任务"""
    print("\n" + "="*60)
    print("📌 Example 4: Multiple Tasks")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        browser = bm.get_browser()
        tools = get_browser_tools(browser)
        agent = create_custom_agent(tools=tools)
        
        tasks = [
            "Go to https://github.com and extract the main heading",
            "Navigate to https://stackoverflow.com and get the page title",
            "Take a screenshot named 'final.png'"
        ]
        
        for i, task in enumerate(tasks, 1):
            print(f"\n📝 Task {i}: {task}")
            result = await agent.ainvoke({"messages": [HumanMessage(content=task)]})
            print(f"✅ {result['messages'][-1].content}")


# ==========================================
# 示例 5: 获取浏览器信息
# ==========================================

async def example_browser_info():
    """示例：获取浏览器详细信息"""
    print("\n" + "="*60)
    print("📌 Example 5: Browser Information")
    print("="*60 + "\n")
    
    from browser.detector import get_chrome_pages
    
    async with BrowserManager(mode="connect") as bm:
        info = bm.get_info()
        
        print("🔍 Browser Status:")
        print(f"   Mode: {info['mode']}")
        print(f"   Contexts: {info['contexts']}")
        print(f"   Total Pages: {info['total_pages']}")
        
        if info.get('cdp_url'):
            print(f"\n🌐 CDP URL: {info['cdp_url']}")
            
            # 获取所有打开的页面
            pages = await get_chrome_pages(info['cdp_url'])
            print(f"\n📄 Open Pages ({len(pages)}):")
            for i, page in enumerate(pages, 1):
                print(f"   {i}. {page['title']}")
                print(f"      URL: {page['url']}")


# ==========================================
# 示例 6: 错误处理
# ==========================================

async def example_error_handling():
    """示例：优雅的错误处理"""
    print("\n" + "="*60)
    print("📌 Example 6: Error Handling")
    print("="*60 + "\n")
    
    try:
        # 尝试连接到不存在的端口
        async with BrowserManager(
            mode="connect",
            cdp_url="http://localhost:9999",
            cdp_ports=[]
        ) as bm:
            pass
    
    except ConnectionError as e:
        print(f"✅ Caught expected error: {e}")
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


# ==========================================
# 示例 7: 使用自定义工具
# ==========================================

async def example_custom_tools():
    """示例：添加自定义工具"""
    print("\n" + "="*60)
    print("📌 Example 7: Custom Tools")
    print("="*60 + "\n")
    
    from langchain_core.tools import tool
    
    @tool
    def calculate_percentage(value: float, total: float) -> str:
        """Calculate percentage of value out of total."""
        if total == 0:
            return "Cannot divide by zero"
        percentage = (value / total) * 100
        return f"{percentage:.2f}%"
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        browser = bm.get_browser()
        browser_tools = get_browser_tools(browser)
        
        # 添加自定义工具
        all_tools = browser_tools + [add, calculate_percentage]
        
        agent = create_custom_agent(tools=all_tools)
        
        task = "Calculate what percentage is 75 out of 300"
        result = await agent.ainvoke({"messages": [HumanMessage(content=task)]})
        
        print(f"\n✅ Result: {result['messages'][-1].content}")


# ==========================================
# 主函数 - 运行所有示例
# ==========================================

async def main():
    """运行所有示例"""
    examples = [
        ("Launch Browser", example_launch_browser),
        ("Connect Chrome", example_connect_chrome),
        ("Custom CDP", example_custom_cdp),
        ("Multiple Tasks", example_multiple_tasks),
        ("Browser Info", example_browser_info),
        ("Error Handling", example_error_handling),
        ("Custom Tools", example_custom_tools)
    ]
    
    print("\n" + "="*60)
    print("🎓 Browser Agent Examples")
    print("="*60)
    print("\nAvailable examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"   {i}. {name}")
    
    choice = input("\nSelect example (1-7, or 'all'): ").strip()
    
    if choice.lower() == 'all':
        for name, func in examples:
            await func()
            await asyncio.sleep(1)
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        name, func = examples[int(choice) - 1]
        await func()
    else:
        print("❌ Invalid choice")


if __name__ == "__main__":
    asyncio.run(main())