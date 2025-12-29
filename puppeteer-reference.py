import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent, AgentExecutor
from langchain_community.agent_toolkits import PlaywrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_sync_playwright_browser

# --- Setup ---
load_dotenv()

# 1. 初始化 Browser (Sync 模式)
# 前端习惯 async/await，但在 Python 脚本简单场景下，Sync 模式更少心智负担
# create_sync_playwright_browser 会自动启动一个 headless=True 的浏览器实例
sync_browser = create_sync_playwright_browser()

# 2. 加载工具集 (The Toolkit)
# 这相当于引入了一个 "UI Automation Hook" 库
# 它会自动提供以下工具给 Agent:
# - click_element: 点击
# - navigate_browser: 跳转 URL
# - extract_text: 获取 innerText
# - extract_content: 获取 HTML
# - current_page: 获取当前 URL
toolkit = PlaywrightBrowserToolkit.from_browser(sync_browser=sync_browser)
tools = toolkit.get_tools()

# 打印一下看看 LLM 能用到哪些工具
# 类似 console.log(Object.keys(tools))
print("--- Available Tools ---")
for tool in tools:
    print(f"- {tool.name}: {tool.description}")

# 3. 初始化 LLM
# 建议使用 gpt-4o 或 gpt-3.5-turbo-16k，因为网页内容(HTML)通常很长，需要大 Context Window
llm = ChatOpenAI(model="gpt-4o", temperature=0)

# 4. 创建 Agent
# 这是一个专门设计的 Prompt，教 Agent 如何做一个 "Web Surfer"
system_prompt = """
You are an autonomous browser agent. 
Your goal is to browse the web and perform tasks given by the user.
You have tools to navigate, click elements, and extract text.

IMPORTANT: 
- When you navigate to a page, ALWAYS use 'extract_text' or 'extract_content' to read the page content before deciding what to do next.
- If you need to click something, you must infer the CSS selector from the page content.
"""

agent_runner = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)

agent_executor = AgentExecutor(
    agent=agent_runner, 
    tools=tools, 
    verbose=True # 开启日志，看 Agent 怎么“操作”浏览器
)

# --- Execution ---
def main():
    try:
        print("\n--- Mission Start ---")
        # 任务：去 Python 官网，找到 Downloads 按钮，告诉我最新的 Python 版本是多少
        task = "Go to https://www.python.org/. Find the 'Downloads' section and tell me what the latest Python version is for download."
        
        result = agent_executor.invoke({"messages": [("user", task)]})
        
        print("\n--- Final Answer ---")
        print(result["output"])
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 类似 browser.close()
        # 这一步很重要，否则后台会有僵尸进程
        # 但 LangChain 的这个 wrapper 有时很难优雅关闭，实际工程中通常配合 Context Manager 使用
        print("Closing browser...")

if __name__ == "__main__":
    main()