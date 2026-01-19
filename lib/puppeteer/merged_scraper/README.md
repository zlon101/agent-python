# 列表页与详情页合并抓取器

## 📋 功能概述

合并抓取器用于解决一个常见的爬虫场景：**从列表页获取概览信息，然后访问每个详情页获取完整数据**。

### 核心特性

✅ **严格顺序执行**：List Item A → Detail A → List Item B → Detail B  
✅ **数据不错配**：每条记录携带唯一标识（list_page + item_index）  
✅ **原子合并**：列表数据和详情数据在同一次迭代中合并  
✅ **错误隔离**：单个详情页失败不影响其他项  
✅ **状态追踪**：完整记录每条数据的抓取状态  

## 🎯 使用场景

```
场景示例：抓取文章网站

列表页：
├─ 文章标题
├─ 文章摘要
├─ 发布时间
└─ 详情链接 → 点击进入详情页

详情页：
├─ 完整内容
├─ 作者信息
├─ 标签
└─ 评论数
```

## 🚀 快速开始

### 基础示例

```python
from browser import BrowserManager
from puppeteer.universal_scraper import create_scraper_config
from puppeteer.merged_scraper import MergedScraper, create_merged_scraper_config

async def main():
    async with BrowserManager(mode="launch") as bm:
        page = await bm.get_or_create_page()
        
        # 1. 配置列表页抓取
        list_config = create_scraper_config(
            url="https://example.com/list",
            fields={
                "标题": "h3 a",
                "摘要": ".summary",
                "详情链接": "h3 a"  # 用于提取详情页URL
            },
            container_selector=".list-item",
            next_button_selector=".next-page",
            max_pages=2
        )
        
        # 2. 配置详情页抓取
        merged_config = create_merged_scraper_config(
            list_config=list_config,
            detail_fields={
                "完整内容": ".article-content",
                "作者": ".author",
                "发布时间": ".publish-time"
            },
            detail_container_selector=".article-content",
            detail_url_field="详情链接",  # 对应列表字段名
            detail_url_attribute="href",
            continue_on_error=True
        )
        
        # 3. 执行抓取
        scraper = MergedScraper(page, merged_config)
        data = await scraper.scrape()
        
        # 4. 保存数据
        scraper.save_to_json("merged_data.json")
```

### 输出数据格式

```json
{
  "metadata": {
    "total_items": 20,
    "statistics": {
      "total_list_items": 20,
      "successful_details": 18,
      "failed_details": 2,
      "skipped_details": 0
    }
  },
  "data": [
    {
      "list_data": {
        "标题": "文章标题",
        "摘要": "文章摘要",
        "详情链接": "https://example.com/article/123"
      },
      "detail_data": {
        "完整内容": "文章完整内容...",
        "作者": "张三",
        "发布时间": "2025-01-19"
      },
      "metadata": {
        "list_page": 1,
        "item_index": 0,
        "detail_url": "https://example.com/article/123",
        "scrape_status": "success",
        "error_message": null,
        "scraped_at": "2025-01-19T10:30:00"
      }
    }
  ]
}
```

## 🔧 配置说明

### MergedScraperConfig 参数

| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `list_config` | `ScraperConfig` | 列表页抓取配置 | 必填 |
| `detail_fields` | `List[FieldConfig]` | 详情页字段配置 | 必填 |
| `detail_container_selector` | `str` | 详情页容器选择器 | 必填 |
| `detail_url_field` | `str` | 列表中的URL字段名 | 必填 |
| `detail_url_attribute` | `str` | URL属性名 | `"href"` |
| `navigation_mode` | `NavigationMode` | 导航模式 | `GO_BACK` |
| `back_wait_time` | `float` | 返回列表页等待时间 | `2.0` |
| `detail_page_wait_time` | `float` | 详情页加载等待时间 | `2.0` |
| `max_detail_retries` | `int` | 详情页最大重试次数 | `2` |
| `continue_on_error` | `bool` | 失败后是否继续 | `True` |

## 🎨 高级用法

### 1. 在已打开的页面上抓取

```python
async with BrowserManager(mode="connect") as bm:
    # 连接到已打开的页面
    page = await bm.get_or_create_page(target_url="example.com")
    
    scraper = MergedScraper(page, merged_config)
    
    # 从当前页面开始抓取（不重新导航）
    data = await scraper.scrape_from_current_page()
```

### 2. 处理相对URL

```python
# 列表配置中提取详情链接时，自动处理相对URL
list_config = create_scraper_config(
    url="https://example.com/list",
    fields={
        "详情链接": "h3 a"  # 即使是相对路径也会自动补全
    },
    # ...
)
```

### 3. 错误处理和重试

```python
merged_config = create_merged_scraper_config(
    # ...
    max_detail_retries=3,  # 详情页失败后重试3次
    continue_on_error=True,  # 某个详情页失败后继续抓取其他项
    skip_invalid_urls=True  # 跳过无效的URL
)
```

### 4. 提取多个值

```python
from puppeteer.universal_scraper import FieldConfig

detail_fields = [
    FieldConfig(name="标签", selector=".tag", multiple=True),  # 提取所有标签
    FieldConfig(name="图片", selector="img", attribute="src", multiple=True)
]
```

## 📊 核心原理

### 防止数据错配的机制

```
核心思路：顺序执行 + 唯一标识 + 原子合并

For each 列表页(page_num):
    For each 列表项(index):
        1. 提取列表数据 → list_data
        2. 提取详情URL → detail_url
        3. 访问详情页 → detail_data
        4. 原子合并 → merged_item = {
             "list_data": list_data,
             "detail_data": detail_data,
             "metadata": {
                 "list_page": page_num,
                 "item_index": index,
                 "detail_url": detail_url
             }
           }
        5. 返回列表页
    翻到下一页
```

### 关键设计

1. **唯一标识追踪**
   - `list_page`: 列表页码
   - `item_index`: 项在当前页的索引
   - `detail_url`: 详情页URL

2. **严格顺序执行**
   - ❌ 不使用并发：`asyncio.gather()`会导致顺序错乱
   - ✅ 使用顺序循环：确保数据一一对应

3. **错误隔离**
   - 单个详情页失败不影响其他项
   - 记录详细的错误信息到metadata

## 🧪 测试

### 运行测试

```bash
# 测试基础功能
python lib/puppeteer/merged_scraper/example.py

# 测试已打开的页面
python examples/02.scrape_list_with_detail.py
```

### 测试准备

```bash
# 启动Chrome（用于连接模式）
chrome.exe --remote-debugging-port=9222

# 打开目标列表页
# 然后运行测试脚本
```

## 📝 完整示例

查看 `lib/puppeteer/merged_scraper/example.py` 中的完整示例：

- 示例1：基础使用
- 示例2：在已打开的页面上抓取
- 示例3：错误处理
- 示例4：高级配置

## ⚠️ 注意事项

1. **页面导航**
   - 目前支持 `GO_BACK` 模式（使用浏览器返回）
   - `NEW_TAB` 模式（新标签页）暂未实现

2. **等待时间**
   - 根据网站响应速度调整 `back_wait_time` 和 `detail_page_wait_time`
   - 网速慢时建议增加等待时间

3. **URL处理**
   - 相对URL会自动补全为完整URL
   - 无效URL会被跳过（如果 `skip_invalid_urls=True`）

4. **内存使用**
   - 大量数据时建议启用 `save_partial_results=True`
   - 定期保存部分结果避免数据丢失

## 🔗 相关文档

- [UniversalScraper 文档](../universal_scraper/README.md)
- [BrowserManager 文档](../../browser/README.md)
- [项目主 README](../../../README.md)
