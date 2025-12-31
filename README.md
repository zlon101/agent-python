# 🤖 LangChain Browser Agent

一个模块化的浏览器自动化 Agent，基于 LangChain 和 Playwright 构建。

## ✨ 特性

- 🎯 **智能代理**: 基于 LLM 的自主决策和任务执行
- 🌐 **浏览器控制**: 完整的网页导航、点击、提取和截图能力
- 🔌 **灵活连接**: 支持启动新浏览器或连接现有 Chrome
- 🧩 **模块化架构**: 清晰的代码组织，易于扩展和维护
- 🔧 **可配置**: 通过环境变量或代码轻松配置

## 📁 项目结构

```
openai/
├── lib/
│   ├── main.py                 # 主入口
│   ├── agent_config.py         # Agent 配置
│   ├── agent_tools.py          # 自定义工具
│   ├── examples.py             # 使用示例
│   └── browser/                # 浏览器管理模块
│       ├── __init__.py
│       ├── manager.py          # 浏览器管理器
│       └── detector.py         # CDP 检测器
├── puppeteer/
│   ├── __init__.py
│   └── puppeteer_tools.py      # Playwright 工具包装
├── .env                        # 环境变量配置
├── requirements.txt            # 依赖包
└── README.md                   # 本文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器
playwright install chromium
```

> 类似于将依赖写入 package.json
pip freeze > requirements.txt

### 2. 配置环境变量

复制 `.env.example` 到 `.env` 并填写配置：

```bash
cp .env.example .env
```

关键配置：
- `ALIBABA_API_KEY`: 阿里云 API 密钥
- `ALIBABA_API_URL`: API 端点
- `BROWSER_MODE`: 浏览器模式 (`launch` 或 `connect`)

### 3. 运行

#### example

```shell
# 1. 测试启动新浏览器
python run.py --mode launch --task "Go to google.com"

# 2. 测试连接已有 Chrome（需先启动 Chrome）
chrome.exe --remote-debugging-port=9222
python run.py --mode connect --task "Get page info"

# 3. 测试交互模式
python run.py --interactive

# 4. 运行示例
python lib/examples.py
```

#### 方式 1: 启动新浏览器

```bash
# 设置环境变量
export BROWSER_MODE=launch

# 运行
python lib/main.py
```

#### 方式 2: 连接已有 Chrome

```bash
# 1. 启动 Chrome（开启远程调试）
chrome.exe --remote-debugging-port=9222 --user-data-dir="C:\chrome-debug"

# 2. 设置环境变量
export BROWSER_MODE=connect

# 3. 运行
python lib/main.py
```

## 📚 核心模块说明

### BrowserManager

浏览器生命周期管理器，支持两种模式：

```python
from browser import BrowserManager

# 模式 1: 启动新浏览器
async with BrowserManager(mode="launch", headless=False) as bm:
    browser = bm.get_browser()
    # ... 使用浏览器

# 模式 2: 连接已有 Chrome
async with BrowserManager(mode="connect") as bm:
    browser = bm.get_browser()
    # ... 使用浏览器
```

**特性:**
- ✅ 自动 CDP 端口检测
- ✅ 上下文管理器支持
- ✅ 优雅的资源清理
- ✅ 详细的状态信息

### Agent Config

简化 Agent 创建和配置：

```python
from agent_config import create_custom_agent

agent = create_custom_agent(
    tools=tools,
    model="qwen-plus",
    temperature=0.1
)
```

### CDP Detector

自动检测可用的 Chrome 调试端口：

```python
from browser.detector import find_chrome_cdp_url, get_chrome_pages

# 查找 Chrome
cdp_url = await find_chrome_cdp_url()

# 获取所有打开的页面
pages = await get_chrome_pages(cdp_url)
```

## 🎮 使用模式

### 单次执行模式（默认）

```bash
export RUN_MODE=single
python lib/main.py
```

执行一个预定义任务后退出。

### 交互模式

```bash
export RUN_MODE=interactive
python lib/main.py
```

持续接收用户输入，适合调试和实验。

## 💡 使用示例

查看 `examples.py` 了解更多用法：

```bash
python lib/examples.py
```

包含示例：
1. 启动新浏览器
2. 连接已有 Chrome
3. 自定义 CDP URL
4. 多任务执行
5. 获取浏览器信息
6. 错误处理
7. 使用自定义工具

## 🔧 高级配置

### 自定义工具

```python
from langchain_core.tools import tool

@tool
def my_custom_tool(input: str) -> str:
    """Tool description"""
    return f"Processed: {input}"

# 添加到工具列表
tools = browser_tools + [my_custom_tool]
agent = create_custom_agent(tools=tools)
```

### 自定义 System Prompt

```python
custom_prompt = """
You are a specialized web scraper.
Focus on extracting structured data.
"""

agent = create_custom_agent(
    tools=tools,
    system_prompt=custom_prompt
)
```

### 远程 Chrome 连接

```python
# 连接到局域网内的 Chrome
async with BrowserManager(
    mode="connect",
    cdp_url="http://192.168.1.100:9222"
) as bm:
    # ...
```

## 📝 环境变量参考

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `BROWSER_MODE` | 浏览器模式 | `connect` |
| `HEADLESS` | 无头模式 | `false` |
| `CDP_URL` | CDP 地址 | `None`（自动检测） |
| `AGENT_MODEL` | 模型名称 | `qwen-plus` |
| `AGENT_TEMPERATURE` | 温度参数 | `0.1` |
| `RUN_MODE` | 运行模式 | `single` |

## 🐛 常见问题

### Q: 连接 Chrome 失败？

**A:** 确保：
1. Chrome 已启动并开启远程调试
2. 端口正确（默认 9222）
3. 没有防火墙阻止连接

### Q: "Target closed" 错误？

**A:** 页面可能已关闭，确保在操作前页面存在。

### Q: 如何保留登录状态？

**A:** 使用 `connect` 模式连接到你正常使用的 Chrome（需要先关闭所有 Chrome 窗口）。

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系

如有问题，请提交 Issue。