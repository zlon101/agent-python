# Universal Web Scraper - 通用网页数据抓取器

## 🎯 功能概述

通用网页数据抓取器是一个强大、灵活的数据采集工具，完全满足你提出的需求：

✅ **支持自定义字段和CSS选择器**  
✅ **支持分页抓取（按钮/URL参数）**  
✅ **可配置页码范围和延迟时间**  
✅ **输出标准JSON格式**  
✅ **与LangChain Agent无缝集成**

---

## 📋 需求实现

根据你的需求：

### 输入参数
- ✅ 网址（url）
- ✅ 需要解析的DOM内容（字段名+CSS选择器）
- ✅ 页码范围（可选）
- ✅ 下一页按钮选择器（可选）
- ✅ 切换页面延迟时间

### 输出格式
- ✅ JSON格式保存到本地文件

### 核心功能
1. ✅ 用户指定URL和CSS选择器
2. ✅ 解析页面DOM，获取指定信息
3. ✅ 支持分页采集
4. ✅ 可配置延迟时间和页数

---

## 🚀 快速使用

### 你的示例需求

**输入**：
```
打开 https://segmentfault.com/ 页面，
获取 .list-group.list-group-flush 对应的列表数据，

采集的信息和对应的选择器如下：
标题：h3 a.text-body
投票数量：.num-card .font-size-16
阅读数量：.num-card.text-secondary .font-size-16

下一页按钮选择器是 a.page-link[rel='next']，
页面至少停留5秒
```

**实现代码**：

```python
import asyncio
from browser import BrowserManager
from puppeteer import UniversalScraper, create_scraper_config

async def main():
    async with BrowserManager(mode="launch") as bm:
        page = await bm.get_or_create_page()
        
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
        
        scraper = UniversalScraper(page, config)
        data = await scraper.scrape()
        
        # 保存为你需要的格式
        import json
        with open("output.json", 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

asyncio.run(main())
```

**输出**（output.json）：
```json
[
  {
    "标题": "xxx",
    "投票数量": "3",
    "阅读数量": "10"
  },
  {
    "标题": "yyy",
    "投票数量": "5",
    "阅读数量": "20"
  }
]
```

---

## 📁 文件结构

```
lib/puppeteer/universal_scraper/
├── __init__.py           # 模块导出
├── scraper.py            # 核心抓取器
├── tools.py              # LangChain工具集成
└── example.py            # 完整示例（6个场景）

examples/
└── universal_scraper_agent.py  # Agent集成示例

docs/
└── universal_scraper_guide.md  # 详细使用文档

test_universal_scraper.py        # 快速测试脚本
```

---

## 🧪 测试验证

### 方法1：运行测试脚本

```bash
python test_universal_scraper.py
# 选择 1 (基础抓取)
```

### 方法2：运行示例代码

```bash
python lib/puppeteer/universal_scraper/example.py
# 选择 6 (完整用户场景)
```

### 方法3：使用Agent

```bash
python examples/universal_scraper_agent.py
# 选择 1 (SegmentFault任务)
```

---

## 🔧 核心功能

### 1. 灵活的字段配置

```python
fields = {
    "标题": "h3 a.text-body",
    "投票数": ".vote-count",
    "阅读数": ".view-count"
}
```

### 2. 多种分页方式

```python
# 按钮分页
next_button_selector = "button.next"

# URL参数分页
page_range = (1, 10)

# 页码链接
next_button_selector = "a.page-link[rel='next']"
```

### 3. 智能延迟控制

```python
delay = 5.0  # 每页等待5秒
```

### 4. 页数限制

```python
max_pages = 10  # 最多抓取10页
page_range = (3, 8)  # 只抓取第3-8页
```

### 5. 提取属性值

```python
FieldConfig(name="链接", selector="a", attribute="href")
FieldConfig(name="图片", selector="img", attribute="src")
```

---

## 🎨 使用场景

| 场景 | 配置 |
|------|------|
| 单页抓取 | 只设置`url`和`fields` |
| 按钮分页 | 添加`next_button_selector` |
| URL分页 | 设置`page_range` |
| 提取链接 | 使用`attribute="href"` |
| 测试选择器 | 使用`preview_scrape`工具 |

---

## 📚 文档

详细文档：`docs/universal_scraper_guide.md`

包含内容：
- 📖 完整参数说明
- 💡 最佳实践
- 🐛 常见问题解答
- 🔧 调试技巧
- 📝 更多示例

---

## 🛠️ 与Agent集成

### 可用工具

| 工具 | 功能 |
|------|------|
| `scrape_web_data` | 基础通用抓取 |
| `scrape_web_data_advanced` | 高级抓取（支持页码范围） |
| `preview_scrape` | 预览结果（测试选择器） |

### Agent使用示例

```python
from custom_agent import create_custom_agent
from puppeteer import get_browser_tools, get_universal_scraping_tools

# 获取所有工具
all_tools = get_browser_tools(browser) + get_universal_scraping_tools(browser)

# 创建Agent
agent = create_custom_agent(tools=all_tools)

# 执行任务
task = """
抓取 SegmentFault 首页文章：
- 容器: .list-group-item
- 字段: {"标题": "h3 a", "投票数": ".vote"}
- 抓取2页，停留5秒
"""
result = await agent.ainvoke({"messages": [HumanMessage(task)]})
```

---

## ✨ 特性亮点

1. **零依赖额外配置** - 基于现有项目架构
2. **完全类型安全** - 使用dataclass和类型注解
3. **异常处理完善** - 优雅处理各种错误情况
4. **输出格式灵活** - 支持完整/简化JSON格式
5. **Agent友好** - 无缝集成LangChain
6. **文档齐全** - 示例代码+详细文档

---

## 🔍 与其他工具对比

| 特性 | Universal Scraper | Table Scraper | Puppeteer Tools |
|------|-------------------|---------------|-----------------|
| 自定义字段 | ✅ | ❌ | ❌ |
| 标准表格 | ✅ | ✅ | ❌ |
| 非表格结构 | ✅ | ❌ | ⚠️ |
| 分页支持 | ✅ | ✅ | ❌ |
| 页码控制 | ✅ | ⚠️ | ❌ |
| 提取属性 | ✅ | ❌ | ❌ |
| Agent集成 | ✅ | ✅ | ✅ |

---

## 🎓 学习路径

1. **新手**：
   - 阅读本README
   - 运行`test_universal_scraper.py`
   - 尝试修改示例参数

2. **进阶**：
   - 查看`example.py`中的6个示例
   - 尝试抓取自己感兴趣的网站
   - 学习高级字段配置

3. **专家**：
   - 阅读`docs/universal_scraper_guide.md`
   - 集成到Agent工作流
   - 自定义扩展功能

---

## 📞 支持

- 📖 详细文档：`docs/universal_scraper_guide.md`
- 💡 示例代码：`lib/puppeteer/universal_scraper/example.py`
- 🧪 测试脚本：`test_universal_scraper.py`
- 🤖 Agent示例：`examples/universal_scraper_agent.py`

---

## 🎉 总结

你的需求已经**完全实现**！

✅ **入参**：url、字段配置、分页选择器、延迟时间、页数  
✅ **功能**：DOM解析、数据提取、分页采集  
✅ **输出**：标准JSON格式

立即开始使用：
```bash
python test_universal_scraper.py
```
