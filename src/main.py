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

# 【引入 Playwright 原生异步 API
from playwright.async_api import async_playwright
from puppeteer.puppeteer_tools import get_browser_tools
from agent_tools import add

load_dotenv()

def create_agent_runner(tools):
    # 初始化 LLM
    llm = ChatOpenAI(
        api_key=SecretStr(os.getenv("ALIBABA_API_KEY") or ""),
        base_url=os.getenv("ALIBABA_API_URL"),
        model="qwen-plus",
        temperature=0.1,
    )

    # 4. 定义 System Prompt
    system_prompt = """
    You are an autonomous browser agent. 
    Your goal is to browse the web and perform tasks given by the user.

    RULES:
    1. You have tools to navigate, click elements, extract text, and TAKE SCREENSHOTS.
    2. ALWAYS use 'extract_text' or 'extract_content' to read the page content immediately after navigating.
    3. If you need to click something, look at the extracted HTML/Text to infer the correct selector.
    4. If you achieve the goal, just answer the user's question directly.
    """

    # 创建 Agent
    agent_runner = create_agent(model=llm, tools=tools, system_prompt=system_prompt)
    return agent_runner


async def main():
    async with async_playwright() as p:
        # 1. 启动浏览器
        browser = await p.chromium.launch(headless=False)

        # 2. 获取工具
        browser_tools = get_browser_tools(browser)
        tools = [add] + browser_tools
        print(f"--- Loaded {len(tools)} Tools ---")

        agent_runner = create_agent_runner(tools)

        try:
            task = "Go to https://segmentfault.com/. Extract the main content title, and then take a screenshot of the home page named 'sf_home.png'."

            # 执行任务 (Async invoke)
            print("🤖 Agent is thinking...")
            result = await agent_runner.ainvoke(
                {"messages": [HumanMessage(content=task)]}
            )
            last_message = result["messages"][-1]
            print("\n--- Final Answer ---\n")
            print(last_message.content)

            # 保存日志
            messages_dict = messages_to_dict(result["messages"])
            json_str = json.dumps(messages_dict, indent=2, ensure_ascii=False)
            with open("log.json", "w", encoding="utf-8") as f:
                f.write(json_str)

        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback

            traceback.print_exc()

        # 无需手动 close
        # async with 块结束时，playwright 会自动关闭浏览器，就像 garbage collection
        print("Closing browser context...")


if __name__ == "__main__":
    asyncio.run(main())
