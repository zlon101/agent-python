# main.py (适配 LangChain v1.2.0+ / 2025 Edition)

import os
import json
from dotenv import load_dotenv
from pydantic import SecretStr
# --- 1. Imports ---
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import messages_to_dict # 官方提供的转换工具
# 注意：这里直接使用你 debug 出来的 create_agent
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage

# 导入 Puppeteer 工具
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from puppeteer.puppeteer_tools import get_puppeteer_tools

load_dotenv()

@tool
def add(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city."""
    return f"The weather in {city} is sunny and 25°C."

# 获取 Puppeteer 工具
puppeteer_tools = get_puppeteer_tools()

# 合并所有工具
tools = [add, get_weather] + puppeteer_tools
llm = ChatOpenAI(
    api_key=SecretStr(os.getenv("ALIBABA_API_KEY") or ""),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    # 模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models)
    # qwen-plus
    model="deepseek-r1",
)

# 它内部自动处理了 Prompt 模板和 Tool Calling 的循环
agent_runner = create_agent(
    model=llm,
    tools=tools,
    # 这里的 system_prompt 替代了以前复杂的 ChatPromptTemplate
    system_prompt="You are a helpful assistant. You must use tools to answer questions.",
)

def main():
    # input_text = "4 + 8 等于多少?"
    input_text = "帮我浏览一下 https://segmentfault.com/ ，输出主要内容，并将页面截图保存在本地。"

    print(f"正在处理请求: {input_text}")

    result = agent_runner.invoke({"messages": [HumanMessage(content=input_text)]})

    # 步骤 1: 将 Message 对象列表转换为普通的 List/Dict 结构
    # 类似于: const rawData = messages.map(m => m.toJSON());
    messages_dict = messages_to_dict(result["messages"])

    # 步骤 2: 序列化为 JSON 字符串
    # ensure_ascii=False: 允许输出中文等非 ASCII 字符，而不是 \uXXXX
    # indent=2: 美化输出，类似 JS 的 space 参数
    json_str = json.dumps(messages_dict, indent=2, ensure_ascii=False)
    print("\n--- Final Result ---\n")
    print(json_str)

    # 步骤 3: 保存 JSON 字符串到项目根目录的文件中
    with open("result.json", "w", encoding="utf-8") as f:
        f.write(json_str)

    print("\n--- Result saved to result.json ---\n")


if __name__ == "__main__":
    main()