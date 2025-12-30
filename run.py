#!/usr/bin/env python3
"""
快速启动脚本 - 提供简单的命令行界面
"""

import sys
import asyncio
import argparse
from pathlib import Path

# 添加 src 到 Python 路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from browser import BrowserManager
from custom_agent.agent_config import create_custom_agent
from puppeteer.puppeteer_tools import get_browser_tools
from custom_agent.agent_tools import add

load_dotenv()

async def run_task(args):
    """执行单个任务"""
    print(f"📋 Mode: {args.mode}")
    print(f"🎯 Task: {args.task}\n")
    
    try:
        async with BrowserManager(
            mode=args.mode,
            headless=args.headless,
            cdp_url=args.cdp_url
        ) as bm:
            browser = bm.get_browser()
            tools = get_browser_tools(browser) + [add]
            
            agent = create_custom_agent(
                tools=tools,
                model=args.model,
                temperature=args.temperature
            )
            
            from langchain_core.messages import HumanMessage
            
            print("🤖 Executing...\n")
            result = await agent.ainvoke(
                {"messages": [HumanMessage(content=args.task)]}
            )
            
            print("\n" + "="*60)
            print("✅ RESULT")
            print("="*60)
            print(result["messages"][-1].content)
            print("="*60)
    
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


async def run_interactive(args):
    """交互模式"""
    print("🎮 Interactive Mode - Type 'quit' to exit\n")
    
    try:
        async with BrowserManager(
            mode=args.mode,
            headless=args.headless,
            cdp_url=args.cdp_url
        ) as bm:
            browser = bm.get_browser()
            tools = get_browser_tools(browser) + [add]
            
            agent = create_custom_agent(
                tools=tools,
                model=args.model,
                temperature=args.temperature
            )
            
            from langchain_core.messages import HumanMessage
            
            while True:
                try:
                    task = input("\n💬 Your task: ").strip()
                    
                    if task.lower() in ['quit', 'exit', 'q']:
                        print("👋 Goodbye!")
                        break
                    
                    if not task:
                        continue
                    
                    print("🤖 Executing...\n")
                    result = await agent.ainvoke(
                        {"messages": [HumanMessage(content=task)]}
                    )
                    
                    print("\n✅ Result:")
                    print(result["messages"][-1].content)
                
                except KeyboardInterrupt:
                    print("\n\n👋 Interrupted")
                    break
                except Exception as e:
                    print(f"❌ Error: {e}")
    
    except Exception as e:
        print(f"\n❌ Startup error: {e}")
        sys.exit(1)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="LangChain Browser Agent - Intelligent Web Automation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Launch new browser and run a task
  python run.py --task "Go to google.com and take a screenshot"
  
  # Connect to existing Chrome
  python run.py --mode connect --task "Get the current page title"
  
  # Interactive mode
  python run.py --interactive
  
  # Use custom model
  python run.py --model qwen-max --task "Search for AI news"
        """
    )
    
    # 模式参数
    parser.add_argument(
        "--mode", "-m",
        choices=["launch", "connect"],
        default="launch",
        help="Browser mode (default: launch)"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run in headless mode"
    )
    
    parser.add_argument(
        "--cdp-url",
        type=str,
        help="CDP URL for connect mode (e.g., http://localhost:9222)"
    )
    
    # Agent 参数
    parser.add_argument(
        "--model",
        type=str,
        default="qwen-plus",
        help="Model name (default: qwen-plus)"
    )
    
    parser.add_argument(
        "--temperature", "-t",
        type=float,
        default=0.1,
        help="Temperature (default: 0.1)"
    )
    
    # 任务参数
    parser.add_argument(
        "--task",
        type=str,
        help="Task to execute"
    )
    
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Run in interactive mode"
    )
    
    # 信息参数
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="LangChain Browser Agent v1.0.0"
    )
    
    args = parser.parse_args()
    
    # 验证参数
    if not args.interactive and not args.task:
        parser.error("Either --task or --interactive is required")
    
    # 运行
    try:
        if args.interactive:
            asyncio.run(run_interactive(args))
        else:
            asyncio.run(run_task(args))
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()