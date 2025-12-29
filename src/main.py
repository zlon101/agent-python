# main.py (适配 LangChain v1.2.0+ / 2025 Edition)

import os
import json
from dotenv import load_dotenv
from pydantic import SecretStr
# --- 1. Imports ---
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent 
from langchain_core.messages import HumanMessage
from langchain_core.messages import messages_to_dict # 官方提供的转换工具
from langchain_community.agent_toolkits import PlaywrightBrowserToolkit
from langchain_community.tools.playwright.utils import create_sync_playwright_browser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

load_dotenv()

@tool
def add(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b

# 1. 初始化 Browser (Sync 模式)
# create_sync_playwright_browser 会自动启动一个 headless=True 的浏览器实例
sync_browser = create_sync_playwright_browser(headless=False)

# 2. 加载工具集 (The Toolkit)
# 这相当于引入了一个 "UI Automation Hook" 库
# 它会自动提供以下工具给 Agent:
# - click_element: 点击
# - navigate_browser: 跳转 URL
# - extract_text: 获取 innerText
# - extract_content: 获取 HTML
# - current_page: 获取当前 URL
toolkit = PlaywrightBrowserToolkit.from_browser(sync_browser=sync_browser)
playwright_tools = toolkit.get_tools()

# 打印一下看看 LLM 能用到哪些工具
# 类似 console.log(Object.keys(tools))
print("--- Available Tools ---")
for tool in playwright_tools:
    print(f"- {tool.name}: {tool.description}")

# 合并所有工具
tools = [add] + playwright_tools

# 3. 创建 Agent
# 这是一个专门设计的 Prompt，教 Agent 如何做一个 "Web Surfer"

system_prompt = """
You are an autonomous browser agent. 
Your goal is to browse the web and perform tasks given by the user.

RULES:
1. You have tools to navigate, click elements, and extract text.
2. ALWAYS use 'extract_text' or 'extract_content' to read the page content immediately after navigating.
3. If you need to click something, look at the extracted HTML/Text to infer the correct selector.
4. If you achieve the goal, just answer the user's question directly.
"""

prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# 4. 初始化 LLM
llm = ChatOpenAI(
    api_key=SecretStr(os.getenv("ALIBABA_API_KEY") or ""),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models)
    # qwen-plus
    model="deepseek-r1",
)
agent_runner = create_agent(
    model=llm,
    tools=tools,
    system_prompt=system_prompt
)

def main():
    try:
        print("\n--- Mission Start ---")
        # 任务：访问 SegmentFault 网站，获取主要内容，并进行截图
        task = "Go to https://segmentfault.com/. Extract the main content and take a screenshot of the page."
        result = agent_runner.invoke({"messages": [HumanMessage(content=task)]})

        print("\n--- Final Answer ---")
        print(result["output"])

        result_data = {
            "input_task": task,
            "output": result["output"],
            "intermediate_steps": result.get("intermediate_steps", [])
        }
        json_str = json.dumps(result_data, indent=2, ensure_ascii=False)

        # 保存 JSON 字符串到项目根目录的文件中
        with open("result.json", "w", encoding="utf-8") as f:
            f.write(json_str)

        print("\n--- Result saved to result.json ---\n")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        # 关闭浏览器
        print("Closing browser...")
        # 注意：在实际应用中，最好使用 Context Manager 来确保浏览器被正确关闭


if __name__ == "__main__":
    main()