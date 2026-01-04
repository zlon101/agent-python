# 浏览器管理器新功能 - 连接到指定 URL 标签页

## 🎯 功能概述

更新后的 `BrowserManager` 支持：
- ✅ 查找并连接到已打开的指定 URL 标签页
- ✅ 支持部分匹配和精确匹配
- ✅ 列出所有打开的标签页信息
- ✅ 在已打开的标签页上直接操作（无需重新导航）

---

## 🆕 新增方法

### 1. `get_or_create_page(target_url=None)`

获取或创建页面，支持查找指定 URL 的标签页。

**参数**：
- `target_url` (可选): 目标 URL
  - 如果提供，会查找匹配此 URL 的已打开标签页
  - 支持部分匹配（URL 包含关系）
  - 如果找不到，按原逻辑返回或创建页面

**示例**：

```python
from browser import BrowserManager

async with BrowserManager(mode="connect") as bm:
    # 原始用法：获取最后一个活跃页面
    page = await bm.get_or_create_page()
    
    # 新用法：查找并连接到 SegmentFault 页面
    page = await bm.get_or_create_page(target_url="segmentfault.com")
    
    # 直接在这个页面上操作，无需重新导航
    print(await page.title())
```

---

### 2. `find_page_by_url(target_url, exact_match=False)`

在所有打开的标签页中查找匹配指定 URL 的页面。

**参数**：
- `target_url`: 目标 URL
- `exact_match`: 是否精确匹配
  - `False`（默认）: 部分匹配（页面 URL 包含 target_url）
  - `True`: 精确匹配（页面 URL 完全等于 target_url）

**返回**：
- 找到的 `Page` 对象，如果没找到返回 `None`

**示例**：

```python
# 部分匹配
page = await bm.find_page_by_url("github.com")
if page:
    print(f"找到: {page.url}")

# 精确匹配
page = await bm.find_page_by_url(
    "https://github.com/trending",
    exact_match=True
)
```

---

### 3. `list_all_pages()`

列出所有打开的页面信息。

**返回**：
- 包含所有页面信息的列表

**示例**：

```python
pages_info = await bm.list_all_pages()

for info in pages_info:
    print(f"标题: {info['title']}")
    print(f"URL: {info['url']}")
    print(f"Context: {info['context_index']}")
    print(f"已关闭: {info['is_closed']}")
```

---

## 🚀 使用场景

### 场景 1: 在已打开的页面上直接抓取

**需求**：用户已经在浏览器中打开了 SegmentFault，想直接在这个页面上抓取数据，而不是重新导航。

**解决方案**：

```python
from browser import BrowserManager
from puppeteer import UniversalScraper, create_scraper_config

async def scrape_existing_tab():
    async with BrowserManager(mode="connect") as bm:
        # 连接到已打开的 SegmentFault 页面
        page = await bm.get_or_create_page(target_url="segmentfault.com")
        
        # 配置抓取器（使用当前页面的 URL）
        config = create_scraper_config(
            url=page.url,  # 使用当前 URL
            fields={
                "标题": "h3 a.text-body",
                "投票数": ".num-card .font-size-16"
            },
            container_selector=".list-group-item",
            delay=2.0
        )
        
        scraper = UniversalScraper(page, config)
        
        # 直接抓取当前页面，无需导航
        data = await scraper.scrape_current_page()
        
        print(f"✅ 成功抓取 {len(data)} 条数据")
```

---

### 场景 2: 批量操作多个标签页

**需求**：用户打开了多个网页，想依次在每个页面上执行操作。

**解决方案**：

```python
async def process_all_tabs():
    async with BrowserManager(mode="connect") as bm:
        # 获取所有打开的页面
        pages_info = await bm.list_all_pages()
        
        print(f"找到 {len(pages_info)} 个标签页")
        
        for info in pages_info:
            url = info['url']
            
            # 连接到这个页面
            page = await bm.find_page_by_url(url, exact_match=True)
            
            if page:
                # 在这个页面上执行操作
                await page.bring_to_front()  # 切换到前台
                title = await page.title()
                print(f"处理: {title}")
                
                # 执行你的操作...
                # await page.screenshot(path=f"{title}.png")
```

---

### 场景 3: 查找特定网站的多个标签页

**需求**：查找所有 GitHub 相关的标签页。

**解决方案**：

```python
async def find_github_tabs():
    async with BrowserManager(mode="connect") as bm:
        github_pages = []
        
        # 遍历所有页面
        for context in bm.browser.contexts:
            for page in context.pages:
                if "github.com" in page.url.lower():
                    github_pages.append(page)
        
        print(f"找到 {len(github_pages)} 个 GitHub 标签页:")
        for page in github_pages:
            print(f"  - {await page.title()}")
            print(f"    {page.url}")
```

---

### 场景 4: 智能抓取器（自动查找或创建页面）

**需求**：如果页面已打开就直接用，没打开就自动打开。

**解决方案**：

```python
async def smart_scraper(target_url: str):
    async with BrowserManager(mode="connect") as bm:
        # 尝试查找已打开的页面
        page = await bm.get_or_create_page(target_url=target_url)
        
        # 检查是否需要导航
        if target_url not in page.url:
            print(f"页面不匹配，导航到: {target_url}")
            await page.goto(target_url)
        else:
            print(f"使用已打开的页面: {page.url}")
        
        # 继续抓取...
```

---

## 📝 完整示例

### 示例 1: 基础用法

```python
import asyncio
from browser import BrowserManager

async def basic_usage():
    # 连接到已打开的 Chrome
    async with BrowserManager(mode="connect") as bm:
        # 列出所有标签页
        pages = await bm.list_all_pages()
        print(f"打开了 {len(pages)} 个标签页")
        
        # 查找 SegmentFault 页面
        page = await bm.find_page_by_url("segmentfault.com")
        
        if page:
            print(f"找到页面: {await page.title()}")
            # 在这个页面上操作...
        else:
            print("未找到页面")

asyncio.run(basic_usage())
```

---

### 示例 2: 与抓取器集成

```python
import asyncio
from browser import BrowserManager
from puppeteer import UniversalScraper, create_scraper_config

async def scrape_with_existing_tab():
    async with BrowserManager(mode="connect") as bm:
        # 方式 1: 直接在 get_or_create_page 中指定 URL
        page = await bm.get_or_create_page(target_url="segmentfault.com")
        
        # 方式 2: 先查找，再使用
        # page = await bm.find_page_by_url("segmentfault.com")
        # if not page:
        #     page = await bm.get_or_create_page()
        #     await page.goto("https://segmentfault.com/")
        
        # 配置抓取器
        config = create_scraper_config(
            url=page.url,  # 使用当前 URL
            fields={
                "标题": "h3 a.text-body",
                "投票数": ".num-card .font-size-16"
            },
            container_selector=".list-group-item",
            delay=2.0
        )
        
        # 创建抓取器
        scraper = UniversalScraper(page, config)
        
        # 直接抓取当前页面（不导航）
        data = await scraper.scrape_current_page()
        
        # 保存数据
        scraper.save_to_json("output.json")
        print(f"✅ 抓取了 {len(data)} 条数据")

asyncio.run(scrape_with_existing_tab())
```

---

### 示例 3: 交互式标签页选择

```python
import asyncio
from browser import BrowserManager

async def interactive_tab_selector():
    async with BrowserManager(mode="connect") as bm:
        # 列出所有标签页
        pages_info = await bm.list_all_pages()
        
        print("\n可用的标签页:")
        for i, info in enumerate(pages_info, 1):
            print(f"{i}. {info['title']}")
            print(f"   {info['url']}\n")
        
        # 用户选择
        choice = int(input("选择标签页 (输入编号): ")) - 1
        
        if 0 <= choice < len(pages_info):
            target_url = pages_info[choice]['url']
            
            # 连接到选中的标签页
            page = await bm.find_page_by_url(target_url, exact_match=True)
            
            if page:
                print(f"\n✅ 已连接到: {await page.title()}")
                await page.bring_to_front()  # 切换到前台
                
                # 在这个页面上执行操作...
        else:
            print("无效选择")

asyncio.run(interactive_tab_selector())
```

---

## 🧪 测试

运行测试脚本：

```bash
# 1. 启动 Chrome（开启远程调试）
chrome.exe --remote-debugging-port=9222

# 2. 在 Chrome 中打开一些网页（如 SegmentFault、GitHub 等）

# 3. 运行测试
python test_browser_manager.py

# 选择测试：
#   1. 查找指定 URL 的页面
#   2. 测试 get_or_create_page 新功能
#   3. 在抓取器中使用
#   4. 交互式页面查找器
```

---

## ⚠️ 注意事项

### 1. 仅在 connect 模式下有效

```python
# ✅ 正确
async with BrowserManager(mode="connect") as bm:
    page = await bm.get_or_create_page(target_url="...")

# ❌ 错误（launch 模式下没有已打开的标签页）
async with BrowserManager(mode="launch") as bm:
    page = await bm.get_or_create_page(target_url="...")
```

### 2. URL 匹配规则

```python
# 部分匹配（默认）
await bm.find_page_by_url("github.com")
# ✅ 匹配: https://github.com/trending
# ✅ 匹配: https://github.com/topics/python
# ✅ 匹配: https://www.github.com/

# 精确匹配
await bm.find_page_by_url("https://github.com/trending", exact_match=True)
# ✅ 匹配: https://github.com/trending
# ❌ 不匹配: https://github.com/trending?since=weekly
```

### 3. 页面可能已关闭

```python
page = await bm.find_page_by_url("example.com")

if page:
    if not page.is_closed():
        # 安全操作
        await page.reload()
    else:
        print("页面已关闭")
```

---

## 💡 最佳实践

### 1. 优雅的回退机制

```python
async def get_target_page(bm, target_url):
    """获取目标页面，如果不存在则创建"""
    page = await bm.get_or_create_page(target_url=target_url)
    
    # 检查 URL 是否匹配
    if target_url not in page.url:
        # 不匹配，需要导航
        await page.goto(target_url)
    
    return page
```

### 2. 批量处理

```python
async def process_multiple_sites(site_urls: list):
    async with BrowserManager(mode="connect") as bm:
        for url in site_urls:
            page = await bm.get_or_create_page(target_url=url)
            # 处理每个页面...
```

### 3. 错误处理

```python
try:
    page = await bm.find_page_by_url("example.com")
    if page and not page.is_closed():
        await page.reload()
except Exception as e:
    print(f"操作失败: {e}")
```

---

## 📚 相关文档

- 浏览器管理器基础: `/Users/admins/work/openai/README.md`
- 通用抓取器: `/Users/admins/work/openai/docs/universal_scraper_guide.md`
- 示例代码: `/Users/admins/work/openai/examples/`

---

## 🎯 总结

更新后的 `BrowserManager` 让你可以：

1. ✅ **直接使用已打开的标签页** - 无需重新导航
2. ✅ **查找特定 URL 的页面** - 支持部分/精确匹配
3. ✅ **列出所有标签页** - 了解浏览器状态
4. ✅ **更高效的数据采集** - 减少页面加载时间

这些功能特别适合：
- 🔄 多标签页批量处理
- 📊 实时数据监控
- 🎯 精确页面操作
- ⚡ 快速原型开发
