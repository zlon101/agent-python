"""
Agent 配置模块
负责 LLM 和 Agent 的初始化
"""

import os
from typing import List
from pydantic import SecretStr
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.tools import BaseTool


# 默认 System Prompt
DEFAULT_SYSTEM_PROMPT = """
You are an autonomous browser agent. 
Your goal is to browse the web and perform tasks given by the user.

RULES:
1. You have tools to navigate, click elements, extract text, and TAKE SCREENSHOTS.
2. ALWAYS use 'extract_text' or 'extract_content' to read the page content immediately after navigating.
3. If you need to click something, look at the extracted HTML/Text to infer the correct selector.
4. If you achieve the goal, just answer the user's question directly.
5. When taking screenshots, use descriptive filenames that reflect the page content.
"""


def create_llm(
    api_key: str = "",
    base_url: str = "",
    model: str = "qwen-plus",
    temperature: float = 0.1
) -> ChatOpenAI:
    """
    创建 LLM 实例
    
    Args:
        api_key: API 密钥（默认从环境变量获取）
        base_url: API 端点（默认从环境变量获取）
        model: 模型名称
        temperature: 温度参数
        
    Returns:
        ChatOpenAI: LLM 实例
    """
    if not api_key:
        api_key = os.getenv("ALIBABA_API_KEY", "")
    
    if not base_url:
        base_url = os.getenv("ALIBABA_API_URL", "")
    
    if not api_key:
        raise ValueError("API key is required. Set ALIBABA_API_KEY environment variable.")
    
    if not base_url:
        raise ValueError("Base URL is required. Set ALIBABA_API_URL environment variable.")
    
    return ChatOpenAI(
        api_key=SecretStr(api_key),
        base_url=base_url,
        model=model,
        temperature=temperature,
    )


def create_custom_agent(
    tools: List[BaseTool],
    api_key: str = "",
    base_url: str = "",
    model: str = "qwen-plus",
    temperature: float = 0.1,
    system_prompt: str = DEFAULT_SYSTEM_PROMPT
):
    """
    创建浏览器 Agent
    Args:
        tools: 工具列表
        api_key: API 密钥
        base_url: API 端点
        model: 模型名称
        temperature: 温度参数
        system_prompt: 系统提示词
        
    Returns:
        Agent: 配置好的 Agent 实例
    """
    # 创建 LLM
    llm = create_llm(
        api_key=api_key,
        base_url=base_url,
        model=model,
        temperature=temperature
    )
    
    # 创建 Agent
    agent = create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt
    )
    
    print(f"✅ Agent created with {len(tools)} tools")
    print(f"   Model: {model}")
    print(f"   Temperature: {temperature}")
    
    return agent


def get_agent_config() -> dict:
    """
    获取 Agent 配置信息（从环境变量）
    Returns:
        dict: 配置字典
    """
    return {
        "api_key": os.getenv("ALIBABA_API_KEY", ""),
        "base_url": os.getenv("ALIBABA_API_URL", ""),
        "model": os.getenv("AGENT_MODEL", "qwen-plus"),
        "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.1"))
    }