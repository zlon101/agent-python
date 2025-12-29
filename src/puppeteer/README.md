# Puppeteer 工具模块

此模块为 LangChain Agent 提供浏览器自动化功能，使 Agent 能够执行网页浏览、截图和信息提取等任务。

## 功能

- **网页浏览**: `browse_web_page(url, query)` - 访问网页并查询特定信息
- **网页截图**: `take_screenshot(url, full_page)` - 对指定网页进行截图
- **链接提取**: `extract_links(url)` - 从网页中提取所有链接

## 依赖

- Playwright: 用于浏览器自动化
- Python-dotenv: 用于环境变量管理

## 安装

```bash
pip install playwright
playwright install chromium
```

## 使用

这些工具已经集成到主 Agent 中，可以直接通过自然语言指令使用，例如：
- "访问 https://www.example.com 并告诉我主要内容"
- "对 https://www.example.com 进行截图"
- "从 https://www.example.com 提取所有链接"