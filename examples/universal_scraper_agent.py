"""
Agent 集成示例 - 通用数据抓取
让 LLM Agent 使用通用抓取工具
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from browser import BrowserManager
from custom_agent import create_custom_agent
from puppeteer import get_browser_tools, get_universal_scraping_tools

load_dotenv()


async def agent_universal_scrape(task: str):
    """
    使用 Agent 执行通用抓取任务
    
    Args:
        task: 用户任务描述
    """
    print("\n" + "="*60)
    print("🤖 Agent 通用数据抓取")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        browser = bm.get_browser()
        
        # 获取所有工具
        browser_tools = get_browser_tools(browser)
        scraping_tools = get_universal_scraping_tools(browser)
        all_tools = browser_tools + scraping_tools
        
        print(f"🔧 加载了 {len(all_tools)} 个工具")
        print(f"   通用抓取工具: {len(scraping_tools)} 个")
        for tool in scraping_tools:
            print(f"   - {tool.name}")
        print()
        
        # 创建 Agent（自定义 prompt）
        system_prompt = """
You are an intelligent web scraping agent with universal data extraction capabilities.

CAPABILITIES:
1. Navigate to any web page
2. Extract data using custom CSS selectors
3. Handle pagination (button-based or URL-based)
4. Save data in JSON format
5. Preview scraping results before full extraction

AVAILABLE TOOLS:
- scrape_web_data: 通用抓取工具（支持分页）
- scrape_web_data_advanced: 高级抓取（支持页码范围）
- preview_scrape: 预览抓取结果（用于测试选择器）

WORKFLOW:
1. 理解用户需求：
   - 目标URL
   - 需要提取的字段和对应的CSS选择器
   - 是否需要分页
   - 延迟时间和页数限制

2. 构建字段配置：
   - 将字段配置转换为JSON格式：{"字段名": "CSS选择器"}
   - 确保选择器准确

3. 选择合适的工具：
   - 简单场景：使用 scrape_web_data
   - 需要精确控制页码：使用 scrape_web_data_advanced
   - 测试选择器：先使用 preview_scrape

4. 执行抓取并报告结果

IMPORTANT TIPS:
- 字段配置必须是有效的JSON格式
- 容器选择器应该准确定位到每个数据项
- 分页按钮选择器要精确，避免点击错误的元素
- 合理设置延迟时间，避免请求过快
- 如果不确定选择器，可以先用 preview_scrape 测试

EXAMPLE:
User: "抓取 SegmentFault 首页文章，包括标题和投票数"
Agent思路:
1. URL: https://segmentfault.com/
2. 字段配置: {"标题": "h3 a.text-body", "投票数": ".num-card .font-size-16"}
3. 容器选择器: .list-group-item
4. 调用 scrape_web_data 工具
"""
        
        agent = create_custom_agent(
            tools=all_tools,
            system_prompt=system_prompt,
            model=os.getenv("AGENT_MODEL", "qwen-plus")
        )
        
        # 执行任务
        print(f"🎯 任务: {task}\n")
        print("🤖 Agent 正在工作...\n")
        
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
# 预定义任务
# ==========================================

TASKS = {
    "1": {
        "name": "SegmentFault 文章列表",
        "task": """
抓取 SegmentFault 首页文章列表数据：
- URL: https://segmentfault.com/
- 容器选择器: .list-group-item
- 需要提取的字段：
  * 标题: h3 a.text-body
  * 投票数量: .num-card .font-size-16
  * 阅读数量: .num-card.text-secondary .font-size-16
- 下一页按钮: a.page-link[rel='next']
- 抓取2页，每页停留5秒
- 保存为 segmentfault_result.json
"""
    },
    
    "2": {
        "name": "GitHub Trending",
        "task": """
抓取 GitHub Trending 页面：
- URL: https://github.com/trending
- 容器选择器: article.Box-row
- 提取字段：
  * 项目名: h2 a
  * 描述: p.col-9
  * 语言: span[itemprop='programmingLanguage']
- 单页抓取，停留3秒
- 保存为 github_trending_universal.json
"""
    },
    
    "3": {
        "name": "Hacker News",
        "task": """
抓取 Hacker News 首页：
- URL: https://news.ycombinator.com/
- 容器选择器: .athing
- 字段：
  * 标题: .titleline > a
  * 分数: .score
- 单页抓取
- 保存为 hackernews.json
"""
    },
    
    "4": {
        "name": "预览测试",
        "task": """
预览 SegmentFault 首页的抓取结果：
- URL: https://segmentfault.com/
- 容器选择器: .list-group-item
- 字段: {"标题": "h3 a.text-body"}
- 使用 preview_scrape 工具，只看前3条
"""
    },
    
    "5": {
        "name": "自定义任务",
        "task": None
    }
}


async def main():
    """主函数"""
    print("\n" + "="*60)
    print("🎓 Agent 通用抓取任务")
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
        print("\n请输入自定义任务描述:")
        print("示例格式：")
        print("---")
        print("抓取 [URL] 页面")
        print("容器选择器: [CSS选择器]")
        print("字段: {\"字段名\": \"CSS选择器\"}")
        print("分页: [可选]")
        print("---")
        task = input("\n> ").strip()
        if not task:
            print("❌ 任务不能为空")
            return
    else:
        task = task_info["task"]
        print(f"\n📋 选择任务: {task_info['name']}")
    
    # 执行任务
    await agent_universal_scrape(task)


if __name__ == "__main__":
    asyncio.run(main())
