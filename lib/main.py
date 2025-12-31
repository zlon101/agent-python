"""
主程序入口 - 浏览器 Agent
使用模块化架构，支持多种浏览器连接模式
"""

import os
import json
import asyncio
from typing import Literal, cast
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, messages_to_dict

# 导入自定义模块
from browser import BrowserManager
from custom_agent import create_custom_agent, add
from puppeteer import get_browser_tools

# 加载环境变量
load_dotenv()


async def run_agent_task(agent, task: str, save_log: bool = True):
    """
    执行 Agent 任务
    
    Args:
        agent: Agent 实例
        task: 任务描述
        save_log: 是否保存日志
    """
    print(f"\n🎯 Task: {task}")
    print("🤖 Agent is thinking...\n")
    
    try:
        # 执行任务
        result = await agent.ainvoke(
            {"messages": [HumanMessage(content=task)]}
        )
        
        # 获取最终答案
        last_message = result["messages"][-1]
        print("\n" + "="*60)
        print("📊 FINAL ANSWER")
        print("="*60)
        print(last_message.content)
        print("="*60 + "\n")
        
        # 保存日志
        if save_log:
            messages_dict = messages_to_dict(result["messages"])
            json_str = json.dumps(messages_dict, indent=2, ensure_ascii=False)
            
            log_file = "agent_log.json"
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(json_str)
            print(f"💾 Log saved to {log_file}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ Error executing task: {e}")
        import traceback
        traceback.print_exc()
        return None


async def main():
    """主函数"""
    
    # ==========================================
    # 配置区域
    # ==========================================
    
    # 浏览器模式选择
    BROWSER_MODE = cast(Literal["launch", "connect"], os.getenv("BROWSER_MODE", "connect"))
    
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    CDP_URL = os.getenv("CDP_URL", None)  # 例如 "http://localhost:9222"
    
    # Agent 配置
    MODEL = os.getenv("AGENT_MODEL", "qwen-plus")
    TEMPERATURE = float(os.getenv("AGENT_TEMPERATURE", "0.1"))
    
    # 任务定义
    TASK = """
    Go to https://segmentfault.com/. 
    Extract the main content title. 
    Then take a screenshot of the home page named 'sf_home.png'.
    """
    
    # ==========================================
    # 初始化浏览器
    # ==========================================
    
    print("="*60)
    print("🚀 Browser Agent Starting")
    print("="*60)
    print(f"Browser Mode: {BROWSER_MODE}")
    print(f"Model: {MODEL}")
    print("="*60 + "\n")
    
    async with BrowserManager(
        mode=BROWSER_MODE,
        headless=HEADLESS,
        cdp_url=CDP_URL
    ) as browser_manager:
        
        # 获取浏览器实例
        browser = browser_manager.get_browser()
        
        # 显示浏览器信息
        info = browser_manager.get_info()
        print(f"📊 Browser Info:")
        print(f"   Contexts: {info['contexts']}")
        print(f"   Total Pages: {info['total_pages']}")
        if info.get('cdp_url'):
            print(f"   CDP URL: {info['cdp_url']}")
        print()
        
        # ==========================================
        # 创建工具和 Agent
        # ==========================================
        
        # 获取浏览器工具
        browser_tools = get_browser_tools(browser)
        
        # 组合所有工具
        all_tools = [add] + browser_tools
        print(f"🔧 Loaded {len(all_tools)} tools:")
        for i, tool in enumerate(all_tools, 1):
            print(f"   {i}. {tool.name}")
        print()
        
        # 创建 Agent
        agent = create_custom_agent(
            tools=all_tools,
            model=MODEL,
            temperature=TEMPERATURE
        )
        print()
        
        # ==========================================
        # 执行任务
        # ==========================================
        
        result = await run_agent_task(agent, TASK)
        
        if result:
            print("✅ Task completed successfully!")
        else:
            print("❌ Task failed!")
    
    print("\n" + "="*60)
    print("👋 Agent Finished")
    print("="*60)


async def interactive_mode():
    """
    交互模式 - 持续接收用户输入
    """
    print("\n🎮 Interactive Mode")
    print("Type your task or 'quit' to exit\n")
    
    BROWSER_MODE = cast(Literal["launch", "connect"], os.getenv("BROWSER_MODE", "connect"))
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    
    async with BrowserManager(mode=BROWSER_MODE, headless=HEADLESS) as browser_manager:
        browser = browser_manager.get_browser()
        browser_tools = get_browser_tools(browser)
        all_tools = [add] + browser_tools
        
        agent = create_custom_agent(tools=all_tools)
        
        while True:
            try:
                task = input("\n💬 Your task: ").strip()
                
                if task.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not task:
                    continue
                
                await run_agent_task(agent, task, save_log=False)
                
            except KeyboardInterrupt:
                print("\n\n👋 Interrupted by user")
                break
            except Exception as e:
                print(f"❌ Error: {e}")


if __name__ == "__main__":
    # 选择模式
    MODE = os.getenv("RUN_MODE", "single")  # "single" 或 "interactive"
    
    if MODE == "interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(main())