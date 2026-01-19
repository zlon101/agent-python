# 列表+详情页合并抓取 - 快速上手

## 🎯 核心功能

从列表页抓取概览信息，然后自动访问每个详情页获取完整数据，最后合并保存。

**关键特性**：列表数据和详情数据严格对应，绝不错配。

## 🚀 30秒上手

```python
from browser import BrowserManager
from puppeteer import create_scraper_config, create_merged_scraper_config, MergedScraper

async with BrowserManager(mode="launch") as bm:
    page = await bm.get_or_create_page()
    
    # 步骤1：配置列表页
    list_config = create_scraper_config(
        url="https://segmentfault.com/",
        fields={
            "标题": "h3 a.text-body",
            "详情链接": "h3 a.text-body"  # ← 这个字段用于跳转详情页
        },
        container_selector=".list-group-item",
        max_pages=2
    )
    
    # 步骤2：配置详情页
    merged_config = create_merged_scraper_config(
        list_config=list_config,
        detail_fields={
            "完整内容": ".article-content",
            "作者": ".user-info .name"
        },
        detail_container_selector=".article-content",
        detail_url_field="详情链接"  # ← 对应上面的字段名
    )
    
    # 步骤3：执行抓取
    scraper = MergedScraper(page, merged_config)
    data = await scraper.scrape()
    scraper.save_to_json("result.json")
```

## 📤 输出格式

```json
{
  "data": [
    {
      "list_data": {
        "标题": "文章标题",
        "详情链接": "https://..."
      },
      "detail_data": {
        "完整内容": "文章内容...",
        "作者": "张三"
      },
      "metadata": {
        "list_page": 1,
        "item_index": 0,
        "scrape_status": "success"
      }
    }
  ]
}
```

## 💡 三种使用场景

### 场景1：从URL开始
```python
scraper = MergedScraper(page, merged_config)
data = await scraper.scrape()  # 自动访问list_config.url
```

### 场景2：已打开的页面
```python
scraper = MergedScraper(page, merged_config)
data = await scraper.scrape_from_current_page()  # 从当前页开始
```

### 场景3：连接已打开的Chrome
```python
async with BrowserManager(mode="connect") as bm:
    page = await bm.get_or_create_page(target_url="example.com")
    scraper = MergedScraper(page, merged_config)
    data = await scraper.scrape_from_current_page()
```

## ⚙️ 常用配置

```python
merged_config = create_merged_scraper_config(
    list_config=list_config,
    detail_fields={"内容": ".article"},
    detail_container_selector=".article",
    detail_url_field="详情链接",
    
    # 可选配置
    detail_url_attribute="href",        # URL属性，默认href
    back_wait_time=2.0,                 # 返回列表页等待时间
    detail_page_wait_time=2.0,          # 详情页加载等待时间
    max_detail_retries=2,               # 详情页失败重试次数
    continue_on_error=True,             # 单个失败是否继续
    skip_invalid_urls=True              # 跳过无效URL
)
```

## 🧪 运行测试

```bash
# 完整示例（4个场景）
python lib/puppeteer/merged_scraper/example.py

# 快速测试
python examples/02.scrape_list_with_detail.py
```

## ❓ 常见问题

### Q1: 如何确保数据不错配？

✅ **自动保证**，核心机制：
- 严格顺序执行（A列表→A详情→B列表→B详情）
- 原子化操作（列表+详情在同一函数中合并）
- 唯一标识追踪（每条记录有准确定位）

### Q2: 详情页抓取失败怎么办？

✅ **自动处理**：
- 失败会自动重试（`max_detail_retries=2`）
- 记录失败状态到`metadata.scrape_status`
- 不影响其他项继续抓取（`continue_on_error=True`）

### Q3: 相对URL怎么处理？

✅ **自动补全**，例如：
- `/article/123` → `https://example.com/article/123`

## 📚 详细文档

- 📖 完整文档：`lib/puppeteer/merged_scraper/README.md`
- 💡 技术方案：`docs/merged_scraper_solution.md`
- ✅ 实现总结：`docs/merged_scraper_implementation_summary.md`

## 🎓 核心API

```python
# 配置函数
create_merged_scraper_config(
    list_config,          # 列表页配置
    detail_fields,        # 详情页字段 {"字段名": "选择器"}
    detail_container_selector,  # 详情页容器
    detail_url_field      # URL字段名
)

# 抓取器类
class MergedScraper:
    def __init__(self, page, config)
    
    async def scrape()                     # 从URL开始
    async def scrape_from_current_page()   # 从当前页开始
    
    def save_to_json(filename)             # 保存JSON
    def get_data()                         # 获取数据
    def get_stats()                        # 获取统计
```

## 🎉 开始使用

复制上面的30秒示例代码，修改URL和字段选择器，立即开始抓取！
