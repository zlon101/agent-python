import os
import json
import asyncio
from dotenv import load_dotenv
from pydantic import SecretStr

# --- LangChain Imports ---
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage, messages_to_dict
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit

# 【修改1】引入 Playwright 原生异步 API
from playwright.async_api import async_playwright 

load_dotenv()

# 全局变量用于 Tool 访问浏览器实例
browser_app = None

# --- Custom Tools ---

@tool
def add(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b

@tool
async def take_screenshot(filename: str = "screenshot.png") -> str:
    """
    Take a screenshot of the current page and save it to a file.
    Useful when the user asks to capture the screen or see the page.
    """
    global browser_app
    if not browser_app:
        return "Browser not initialized"
        
    try:
        # 获取当前活跃的页面
        # browser -> contexts -> pages
        if not browser_app.contexts:
            return "No open browser context found"
            
        page = browser_app.contexts[0].pages[0]
        
        # 异步截图
        await page.screenshot(path=filename)
        return f"Screenshot saved to {filename}"
    except Exception as e:
        return f"Failed to take screenshot: {e}"

# --- Main Logic ---

async def main():
    global browser_app
    print("\n--- Mission Start (Native Async Mode) ---")

    # 【修改2】使用 Playwright 原生 Context Manager 启动
    # 这完全避免了 "loop already running" 错误
    async with async_playwright() as p:
        # 启动浏览器 (类似 await puppeteer.launch)
        browser_app = await p.chromium.launch(headless=False)
        
        # 初始化 LangChain Toolkit
        # 注意：这里我们传入 native browser 实例，LangChain 能完美识别
        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser_app)
        playwright_tools = toolkit.get_tools()
        
        # 组合工具
        tools = [add, take_screenshot] + playwright_tools

        print(f"--- Loaded {len(tools)} Tools ---")

        # 定义 Prompt
        system_prompt = """
        You are an autonomous browser agent. 
        Your goal is to browse the web and perform tasks given by the user.

        RULES:
        1. You have tools to navigate, click elements, extract text, and TAKE SCREENSHOTS.
        2. ALWAYS use 'extract_text' to read the page content immediately after navigating.
        3. If you need to click something, look at the extracted HTML/Text to infer the correct selector.
        4. If you achieve the goal, just answer the user's question directly.
        """

        # 初始化 LLM
        llm = ChatOpenAI(
            api_key=SecretStr(os.getenv("ALIBABA_API_KEY") or ""),
            base_url=os.getenv("ALIBABA_API_URL"),
            model="qwen-plus", 
            temperature=0.1,
        )

        # 创建 Agent
        agent_runner = create_agent(
            model=llm,
            tools=tools,
            system_prompt=system_prompt
        )

        try:
            task = "Go to https://segmentfault.com/. Extract the main content title, and then take a screenshot of the home page named 'sf_home.png'."
            
            # 执行任务 (Async invoke)
            print("🤖 Agent is thinking...")
            result = await agent_runner.ainvoke({"messages": [HumanMessage(content=task)]})
            
            print("\n--- Final Answer ---\n")
            if "messages" in result:
                print(result["messages"][-1].content)

            # 保存日志
            messages_dict = messages_to_dict(result["messages"])
            json_str = json.dumps(messages_dict, indent=2, ensure_ascii=False)
            with open("log.json", "w", encoding="utf-8") as f:
                f.write(json_str)
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        
        # 【修改3】无需手动 close
        # async with 块结束时，playwright 会自动关闭浏览器，就像 garbage collection
        print("Closing browser context...")

if __name__ == "__main__":
    asyncio.run(main())