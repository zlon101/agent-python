"""
Agent 自动抓取分页表格示例
让 LLM Agent 自主识别表格并收集数据
"""

import asyncio
import sys
from dotenv import load_dotenv
from pathlib import Path
from langchain_core.messages import HumanMessage


from lib.browser import BrowserManager
from lib.custom_agent import create_custom_agent
from lib.puppeteer import get_browser_tools, get_table_scraping_tools

load_dotenv()


async def agent_scrape_table(task: str):
    """
    使用 Agent 自动抓取表格
    
    Args:
        task: 用户任务描述
    """
    print("\n" + "="*60)
    print("🤖 Agent 自动抓取表格")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect") as bm:
        browser = bm.get_browser()
        
        # 获取所有工具（浏览器 + 表格抓取）
        browser_tools = get_browser_tools(browser)
        table_tools = get_table_scraping_tools(browser)
        all_tools = browser_tools + table_tools
        
        print(f"🔧 加载了 {len(all_tools)} 个工具")
        print(f"   其中 {len(table_tools)} 个表格工具:")
        for tool in table_tools:
            print(f"   - {tool.name}")
        print()
        
        # 创建 Agent（使用自定义 prompt）
        system_prompt = """
You are an intelligent web scraping agent specialized in extracting table data.

CAPABILITIES:
1. Navigate to web pages
2. Identify table structures
3. Extract data from single or paginated tables
4. Save data to CSV or JSON files

WORKFLOW:
1. Navigate to the target URL
2. Use 'analyze_table' to understand the table structure
3. Choose the appropriate scraping method:
   - Single page: use 'extract_table'
   - Button pagination: use 'scrape_paginated_table'
   - URL pagination: use 'scrape_table_url_pagination'
4. Save the results with a descriptive filename

IMPORTANT TIPS:
- Always analyze the table structure first
- Look for pagination elements (buttons, page numbers, URLs)
- Use appropriate CSS selectors for tables
- Handle errors gracefully
"""
        
        agent = create_custom_agent(
            tools=all_tools,
            system_prompt=system_prompt
        )
        
        # 执行任务
        print(f"🎯 任务: {task}\n")
        print("🤖 Agent 正在思考...\n")
        
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=task)]}
        )
        
        # 显示结果
        print("\n" + "="*60)
        print("✅ Agent 完成")
        print("="*60)
        print(result["messages"][-1].content)
        print("="*60 + "\n")


# ==========================================
# 预定义任务示例
# ==========================================

TASKS = {
    "1": {
        "name": "抓取 Wikipedia 表格",
        "task": """
Go to https://en.wikipedia.org/wiki/List_of_countries_by_population_(United_Nations).
Find the main population table and extract all data.
Save it as 'world_population.csv'.
"""
    },
    
    "2": {
        "name": "抓取 GitHub Trending",
        "task": """
Go to https://github.com/trending.
Extract information about trending repositories including:
- Repository name
- Description
- Stars today
Save as 'github_trending.json'.
"""
    },
    
    "3": {
        "name": "抓取分页产品列表",
        "task": """
Go to the e-commerce website and find the product listing table.
The table has pagination with a "Next" button.
Scrape the first 3 pages of products.
Save as 'products.csv'.
(Note: You need to provide a real URL)
"""
    },
    
    "4": {
        "name": "分析表格结构",
        "task": """
Go to https://example.com/data-table (replace with your URL).
Analyze the table structure and tell me:
- How many columns
- What are the column names
- How many rows
- Is there pagination?
"""
    },
    
    "5": {
        "name": "自定义任务",
        "task": None  # 用户输入
    }
}


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("🎓 Agent 自动抓取表格 - 任务选择")
    print("="*60)
    print("\n可用任务:")
    for key, info in TASKS.items():
        print(f"   {key}. {info['name']}")
    
    choice = input("\n选择任务 (1-5): ").strip()
    
    if choice not in TASKS:
        print("❌ 无效选择")
        return
    
    task_info = TASKS[choice]
    
    if choice == "5":
        print("\n请输入自定义任务:")
        task = input("> ").strip()
        if not task:
            print("❌ 任务不能为空")
            return
    else:
        task = task_info["task"]
        print(f"\n📋 选择任务: {task_info['name']}")
    
    # 执行任务
    await agent_scrape_table(task)


# ==========================================
# 快速测试函数
# ==========================================

async def quick_test():
    """快速测试 - 抓取 Example.com 演示表格"""
    task = """
Navigate to a website with a data table.
Analyze the table structure.
Then extract the table data and save as 'test_table.csv'.
"""
    await agent_scrape_table(task)


if __name__ == "__main__":
    # 选择运行模式
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        asyncio.run(quick_test())
    else:
        asyncio.run(main())