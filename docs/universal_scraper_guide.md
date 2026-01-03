# 通用网页数据抓取器使用文档

## 📖 概述

通用网页数据抓取器是一个灵活、强大的数据采集工具，支持：
- ✅ 自定义字段和CSS选择器
- ✅ 分页数据抓取（按钮/URL参数）
- ✅ 灵活的延迟配置
- ✅ 页码范围控制
- ✅ JSON格式输出
- ✅ 与LangChain Agent集成

---

## 🚀 快速开始

### 方法1：直接使用抓取器

```python
import asyncio
from browser import BrowserManager
from puppeteer import UniversalScraper, create_scraper_config

async def main():
    async with BrowserManager(mode="launch") as bm:
        page = await bm.get_or_create_page()
        
        # 创建配置
        config = create_scraper_config(
            url="https://segmentfault.com/",
            fields={
                "标题": "h3 a.text-body",
                "投票数": ".num-card .font-size-16"
            },
            container_selector=".list-group-item",
            next_button_selector="a.page-link[rel='next']",
            delay=5.0,
            max_pages=2
        )
        
        # 执行抓取
        scraper = UniversalScraper(page, config)
        data = await scraper.scrape()
        
        # 保存数据
        scraper.save_to_json("output.json")

asyncio.run(main())
```

### 方法2：通过Agent使用

```python
from custom_agent import create_custom_agent
from puppeteer import get_browser_tools, get_universal_scraping_tools

# 获取工具
browser_tools = get_browser_tools(browser)
scraping_tools = get_universal_scraping_tools(browser)
all_tools = browser_tools + scraping_tools

# 创建Agent
agent = create_custom_agent(tools=all_tools)

# 执行任务
task = """
抓取 SegmentFault 首页文章：
- 字段: {"标题": "h3 a", "投票数": ".vote-count"}
- 容器: .list-group-item
- 抓取2页，停留5秒
"""
result = await agent.ainvoke({"messages": [HumanMessage(task)]})
```

---

## 🔧 配置参数详解

### ScraperConfig 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `url` | str | ✅ | 目标网址 |
| `fields` | List[FieldConfig] | ✅ | 字段配置列表 |
| `container_selector` | str | ✅ | 数据项容器的CSS选择器 |
| `next_button_selector` | str | ❌ | 下一页按钮选择器（分页用） |
| `page_range` | tuple | ❌ | 页码范围 (start, end) |
| `delay` | float | ❌ | 页面等待时间（秒），默认3.0 |
| `max_pages` | int | ❌ | 最大抓取页数，0表示无限制 |

### FieldConfig 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `name` | str | ✅ | 字段名 |
| `selector` | str | ✅ | CSS选择器 |
| `attribute` | str | ❌ | 提取属性（如href、src），默认提取文本 |
| `multiple` | bool | ❌ | 是否提取多个值，默认False |

---

## 📝 使用示例

### 示例1：基础抓取（单页）

```python
config = create_scraper_config(
    url="https://example.com",
    fields={
        "标题": "h2.title",
        "描述": "p.description"
    },
    container_selector=".item",
    delay=3.0
)
```

### 示例2：分页抓取（按钮）

```python
config = create_scraper_config(
    url="https://example.com",
    fields={
        "标题": "h2.title"
    },
    container_selector=".item",
    next_button_selector="button.next",  # 下一页按钮
    delay=5.0,
    max_pages=5  # 最多抓取5页
)
```

### 示例3：页码范围控制

```python
config = create_scraper_config(
    url="https://example.com",
    fields={"标题": "h2"},
    container_selector=".item",
    next_button_selector="a.next",
    page_range=(2, 5),  # 只抓取第2-5页
    delay=4.0
)
```

### 示例4：提取属性值

```python
from puppeteer.universal_scraper import FieldConfig, ScraperConfig

config = ScraperConfig(
    url="https://example.com",
    fields=[
        FieldConfig(name="标题", selector="h2 a"),
        FieldConfig(name="链接", selector="h2 a", attribute="href"),  # 提取href属性
        FieldConfig(name="图片", selector="img", attribute="src")     # 提取src属性
    ],
    container_selector=".item",
    delay=3.0
)
```

### 示例5：提取多个值

```python
config = ScraperConfig(
    url="https://example.com",
    fields=[
        FieldConfig(name="标题", selector="h2"),
        FieldConfig(
            name="标签", 
            selector=".tag", 
            multiple=True  # 提取所有标签
        )
    ],
    container_selector=".item",
    delay=3.0
)
```

---

## 🎯 完整示例：SegmentFault

根据你的需求实现：

```python
import asyncio
from browser import BrowserManager
from puppeteer import UniversalScraper, create_scraper_config

async def scrape_segmentfault():
    """
    抓取 SegmentFault 首页文章列表
    
    需求：
    - URL: https://segmentfault.com/
    - 容器: .list-group.list-group-flush
    - 字段:
      * 标题: h3 a.text-body
      * 投票数量: .num-card .font-size-16
      * 阅读数量: .num-card.text-secondary .font-size-16
    - 下一页: a.page-link[rel='next']
    - 延迟: 5秒
    """
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        page = await bm.get_or_create_page()
        
        # 配置
        config = create_scraper_config(
            url="https://segmentfault.com/",
            fields={
                "标题": "h3 a.text-body",
                "投票数量": ".num-card .font-size-16",
                "阅读数量": ".num-card.text-secondary .font-size-16"
            },
            container_selector=".list-group.list-group-flush > .list-group-item",
            next_button_selector="a.page-link[rel='next']",
            delay=5.0,
            max_pages=2
        )
        
        # 抓取
        scraper = UniversalScraper(page, config)
        data = await scraper.scrape()
        
        # 保存（简化格式，直接保存数据数组）
        import json
        with open("output.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 抓取完成：{len(data)} 条数据")
        return data

# 运行
asyncio.run(scrape_segmentfault())
```

**输出格式**（output.json）：

```json
[
  {
    "标题": "如何优化前端性能",
    "投票数量": "5",
    "阅读数量": "120"
  },
  {
    "标题": "Python异步编程实战",
    "投票数量": "8",
    "阅读数量": "256"
  }
]
```

---

## 🛠️ Agent工具使用

### 可用工具

| 工具名 | 功能 | 使用场景 |
|--------|------|----------|
| `scrape_web_data` | 通用抓取 | 大部分场景 |
| `scrape_web_data_advanced` | 高级抓取 | 需要页码范围控制 |
| `preview_scrape` | 预览结果 | 测试选择器 |

### 工具参数

#### scrape_web_data

```python
{
    "url": "https://example.com",
    "fields": '{"标题": "h2", "描述": "p"}',  # JSON字符串
    "container_selector": ".item",
    "next_button_selector": "button.next",  # 可选
    "delay": 5.0,
    "max_pages": 3,
    "filename": "output.json"
}
```

#### scrape_web_data_advanced

```python
{
    "url": "https://example.com",
    "fields_json": '{"标题": "h2"}',
    "container_selector": ".item",
    "next_button_selector": "a.next",
    "page_range_start": 2,  # 起始页
    "page_range_end": 5,    # 结束页
    "delay": 4.0,
    "filename": "output.json"
}
```

#### preview_scrape

```python
{
    "url": "https://example.com",
    "fields": '{"标题": "h2"}',
    "container_selector": ".item",
    "limit": 3  # 预览3条
}
```

---

## 🧪 测试验证

### 快速测试

```bash
# 测试基础功能
python test_universal_scraper.py
# 选择 1 (基础抓取)

# 测试分页功能
python test_universal_scraper.py
# 选择 2 (分页抓取)
```

### 使用示例脚本

```bash
# 直接使用抓取器
python lib/puppeteer/universal_scraper/example.py
# 选择 6 (完整用户场景)

# Agent集成
python examples/universal_scraper_agent.py
# 选择 1 (SegmentFault)
```

---

## ❓ 常见问题

### Q1: 如何找到正确的CSS选择器？

**方法1：浏览器开发者工具**
1. 右键点击目标元素 → 检查
2. 在Elements面板中找到元素
3. 右键 → Copy → Copy selector

**方法2：使用preview_scrape测试**
```python
# 先用预览工具测试
result = await preview_scrape(
    url="https://example.com",
    fields='{"标题": "h2.title"}',
    container_selector=".item",
    limit=3
)
print(result)
```

### Q2: 分页按钮不工作怎么办？

**检查项：**
1. 选择器是否准确？
2. 按钮是否在页面加载后才出现？
3. 延迟时间是否足够？

**调试方法：**
```python
# 增加延迟时间
config.delay = 8.0

# 使用更精确的选择器
next_button_selector = "a.page-link[rel='next']"  # 带属性
```

### Q3: 提取的数据为空？

**可能原因：**
1. 容器选择器不正确
2. 字段选择器不正确
3. 页面需要登录
4. 数据动态加载

**解决方法：**
```python
# 1. 增加等待时间
config.delay = 5.0

# 2. 使用preview_scrape测试
# 3. 检查页面HTML结构
```

### Q4: 如何抓取需要登录的页面？

```python
# 先手动登录，然后使用connect模式
async with BrowserManager(mode="connect") as bm:
    # 使用已登录的浏览器
    page = await bm.get_or_create_page()
    # ... 继续抓取
```

---

## 💡 最佳实践

### 1. 合理设置延迟时间

```python
# 快速网站
config.delay = 2.0

# 普通网站
config.delay = 3.0 - 5.0

# 慢速网站或需要重度渲染
config.delay = 5.0 - 10.0
```

### 2. 使用精确的选择器

```python
# ❌ 不好：太宽泛
".title"

# ✅ 好：更精确
"h3.article-title > a"

# ✅ 最好：包含属性
"a.page-link[rel='next']"
```

### 3. 先预览再全量抓取

```python
# 第一步：预览测试
preview_result = await preview_scrape(...)

# 第二步：确认无误后全量抓取
full_data = await scrape_web_data(...)
```

### 4. 分批抓取大量数据

```python
# 不要一次性抓取太多页
# ❌ 不好
max_pages = 100

# ✅ 好：分批抓取
for batch in range(0, 100, 10):
    config.page_range = (batch+1, batch+10)
    data = await scraper.scrape()
    # 保存每批数据
```

---

## 📚 API参考

完整API文档请参考代码注释：
- `lib/puppeteer/universal_scraper/scraper.py`
- `lib/puppeteer/universal_scraper/tools.py`

---

## 🔗 相关链接

- 项目README: `/README.md`
- 浏览器管理: `/lib/browser/`
- Puppeteer工具: `/lib/puppeteer/`
- 示例代码: `/examples/`

---

## 📞 支持

遇到问题？
1. 查看示例代码：`lib/puppeteer/universal_scraper/example.py`
2. 运行测试脚本：`test_universal_scraper.py`
3. 检查配置参数是否正确
