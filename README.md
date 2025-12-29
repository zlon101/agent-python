# LangChain Agent 项目

这是一个基于 LangChain 框架的 Python 项目，演示了如何使用代理（Agent）模式与大语言模型进行交互，并通过工具调用（Tool Calling）功能执行特定任务。

## 项目概述

本项目使用 LangChain v1.2.0+ 版本，通过阿里云的 DashScope 兼容模式 API 接入大语言模型服务。项目核心功能是创建一个智能代理，能够理解用户请求并选择合适的工具来完成任务，如数学计算和天气查询。

## 主要特性

- **工具调用 (Tool Calling)**: 代理可以调用预定义的工具函数来完成特定任务
- **数学计算**: 提供 `add` 工具用于两个整数相加
- **天气查询**: 提供 `get_weather` 工具返回指定城市的天气信息
- **环境变量管理**: 使用 `.env` 文件安全地存储 API 密钥等敏感信息

## 文件结构

```
openai/
├── .env                    # 环境变量配置文件
├── .python-version         # Python 版本指定
├── .venv                   # Python 虚拟环境
├── .vscode                 # VS Code 编辑器配置
├── debug.py                # 调试脚本
├── src/
│   └── main.py             # 主程序入口
└── README.md              # 项目说明文档
```

## 核心组件

### `src/main.py`

这是项目的核心文件，主要包含以下部分：

1. **工具定义**: 使用 `@tool` 装饰器定义可被代理调用的函数
2. **LLM 初始化**: 配置 ChatOpenAI 实例，连接到阿里云 DashScope 服务
3. **代理创建**: 使用 `create_agent` 函数创建智能代理，自动处理提示模板和工具调用循环
4. **执行逻辑**: 定义 `main()` 函数来处理用户输入并输出结果

### `debug.py`

调试脚本，包含一些辅助函数用于开发和调试。

### `.env`

环境变量文件，存储了访问不同 API 所需的密钥和端点地址：

- `OPENAI_API_KEY`: OpenAI API 密钥
- `ALIBABA_API_KEY`: 阿里巴巴 API 密钥
- `ALIBABA_API_URL_OVERSEAS`: 海外 API 端点
- `ALIBABA_API_URL`: 国内 API 端点

## 运行项目

1. 确保已安装 Python 3.8 或更高版本
2. 创建并激活虚拟环境：
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # 或 .venv\Scripts\activate  # Windows
   ```
3. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```
4. 在 `.env` 文件中配置您的 API 密钥
5. 运行主程序：
   ```bash
   python src/main.py
   ```

## 技术栈

- Python 3.8+
- LangChain 1.2.0
- langchain-core 1.2.3
- langchain-openai 1.1.6
- OpenAI Python SDK 2.13.0
- python-dotenv 1.2.1
- Pydantic 2.12.5
- DashScope (阿里云)

## 使用示例

当运行程序时，代理会处理如下类型的请求：

- "4 + 8 等于多少?" → 调用 `add` 工具返回计算结果
- "新加坡的天气如何？" → 调用 `get_weather` 工具返回天气信息

## 注意事项

- 请勿将 `.env` 文件提交到版本控制系统，以保护您的 API 密钥安全
- 当前配置使用 `deepseek-r1` 模型，您可以在 `main.py` 中根据需要更改模型名称
- 程序输出结果以 JSON 格式打印，便于后续处理和分析