# main.py (适配 LangChain v1.2.0+ / 2025 Edition)

import os
import json
from dotenv import load_dotenv
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_core.messages import messages_to_dict # 官方提供的转换工具
from langchain_community.tools.playwright.utils import create_sync_playwright_browser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit

load_dotenv()

@tool
def add(a: int, b: int) -> int:
  """Add two integers together."""
  return a + b

# 1. 初始化 Browser (Sync 模式)
# create_sync_playwright_browser 会自动启动一个 headless=True 的浏览器实例
sync_browser = create_sync_playwright_browser(headless=False)

# 2. 创建 Playwright 工具
toolkit = PlayWrightBrowserToolkit.from_browser(sync_browser=sync_browser)
playwright_tools = toolkit.get_tools()
# 这些是浏览器自动化工具
# click_tool = ClickTool(sync_browser=sync_browser)
# navigate_tool = NavigateTool(sync_browser=sync_browser)
# extract_text_tool = ExtractTextTool(sync_browser=sync_browser)
# extract_hyperlinks_tool = ExtractHyperlinksTool(sync_browser=sync_browser)

# 打印一下看看 LLM 能用到哪些工具
# print("--- Available Tools ---")
# for tool in playwright_tools:
#     print(f"- {tool.name}: {tool.description}")

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
  # qwen-plus deepseek-r1 qwen3-coder-plus qwen3-max-preview
  model="qwen3-coder-plus",
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
    # task = '3 加 8 等于多少？'
    result = agent_runner.invoke({"messages": [HumanMessage(content=task)]})
    print("\n--- Final Result ---\n")

    messages_dict = messages_to_dict(result["messages"])
    # ensure_ascii=False: 允许输出中文等非 ASCII 字符，而不是 \uXXXX
    # indent=2: 美化输出，类似 JS 的 space 参数
    json_str = json.dumps(messages_dict, indent=2, ensure_ascii=False)

    with open("log.json", "w", encoding="utf-8") as f:
      f.write(json_str)

    print("\n--- Result saved to log.json ---\n")
  except Exception as e:
    print(f"Error: {e}")
  finally:
    # 关闭浏览器
    if hasattr(sync_browser, 'close'):
      print("Closing browser...")
      sync_browser.close()


if __name__ == "__main__":
  main()