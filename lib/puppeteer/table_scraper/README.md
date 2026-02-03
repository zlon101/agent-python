# 📊 分页表格抓取完整指南

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install beautifulsoup4
```

### 2. 将新文件添加到项目

```
agent-python/
├── lib/
│   ├── table_scraper.py        # 表格提取核心
│   ├── table_tools.py          # Agent 工具
│   ├── scrape_table_example.py # 使用示例
│   └── agent_scrape_table.py   # Agent 自动抓取
```

---

## 🎯 三种使用方式

### 方式 1: 直接使用 TableScraper（手动）

适合：**已知表格结构和分页方式**

```python
from table_scraper import TableScraper
from browser import BrowserManager

async with BrowserManager(mode="connect") as bm:
    page = await bm.get_or_create_page()
    scraper = TableScraper(page)
    
    # 访问页面
    await page.goto("https://example.com/data")
    
    # 抓取分页表格
    await scraper.scrape_with_button_pagination(
        table_selector="table.data",
        next_button_selector="button.next",
        max_pages=10
    )
    
    # 保存数据
    scraper.save_to_csv("output.csv")
```

### 方式 2: 运行示例脚本（半自动）

适合：**学习和测试不同场景**

```bash
python lib/scrape_table_example.py
```

选择预定义的示例：
1. 按钮分页
2. 页码分页
3. URL 参数分页
4. GitHub Trending 实战
5. 等等...

### 方式 3: Agent 自动抓取（全自动）

适合：**让 AI 自主识别和抓取**

```bash
python lib/agent_scrape_table.py
```

只需描述任务，Agent 会：
- ✅ 自动导航到页面
- ✅ 分析表格结构
- ✅ 选择合适的抓取方法
- ✅ 保存数据

---

## 📝 常见场景示例

### 场景 1: 电商产品列表（按钮分页）

**特征：**
- 标准 HTML 表格
- "下一页"按钮
- 每页显示固定数量

**代码：**

```python
await scraper.scrape_with_button_pagination(
    table_selector="table#products",
    next_button_selector="button[aria-label='Next']",
    max_pages=5,
    wait_time=2.0
)
```

**实际网站示例：**
- 淘宝商品列表
- 京东搜索结果
- 亚马逊产品页

---

### 场景 2: 论坛帖子列表（页码分页）

**特征：**
- 底部有页码 1, 2, 3, ...
- 可以直接跳转到指定页
- 通常有"首页"、"尾页"按钮

**代码：**

```python
await scraper.scrape_with_page_numbers(
    table_selector="table.threads",
    page_number_selector="a.page-{page}",  # {page} 自动替换
    max_pages=20
)
```

**实际网站示例：**
- V2EX 主题列表
- Stack Overflow 问题列表
- Reddit 论坛

---

### 场景 3: API 结果展示（URL 参数分页）

**特征：**
- URL 包含页码参数：`?page=1`
- 每个页面独立访问
- 适合爬取搜索结果

**代码：**

```python
await scraper.scrape_with_url_params(
    base_url="https://api.example.com/search?q=python",
    table_selector="table.results",
    page_param="page",
    start_page=1,
    max_pages=10
)
```

**实际网站示例：**
- GitHub 搜索结果
- Google Scholar
- 招聘网站职位列表

---

### 场景 4: 非标准表格（自定义选择器）

**特征：**
- 不是 `<table>` 标签
- 使用 `<div>` 或其他元素模拟表格
- 需要自定义选择器

**代码：**

```python
data = await scraper.extract_table(
    table_selector="div.data-grid",
    headers_selector="div.header > span",
    rows_selector="div.row",
    cells_selector="div.cell"
)
```

**实际网站示例：**
- 现代单页应用 (SPA)
- React/Vue 构建的表格
- 响应式设计的表格

---

## 🔍 如何识别分页类型？

### 步骤 1: 打开浏览器开发者工具

1. 按 `F12` 打开开发者工具
2. 点击"元素"选项卡
3. 找到分页控件

### 步骤 2: 识别分页机制

#### ✅ 按钮分页

**特征：**
```html
<button class="next-page">下一页</button>
<button id="btnNext">Next →</button>
```

**选择器：**
```python
next_button_selector="button.next-page"
# 或
next_button_selector="button#btnNext"
```

---

#### ✅ 页码分页

**特征：**
```html
<a class="page-link" data-page="1">1</a>
<a class="page-link" data-page="2">2</a>
<a class="page-link" data-page="3">3</a>
```

**选择器：**
```python
page_number_selector="a.page-link[data-page='{page}']"
```

---

#### ✅ URL 参数分页

**特征：**
```
https://example.com/list?page=1
https://example.com/list?page=2
```

**检查方法：**
- 点击页码，观察 URL 是否变化
- 如果变化，记录参数名（如 `page`、`p`、`pageNum` 等）

**使用：**
```python
await scraper.scrape_with_url_params(
    base_url="https://example.com/list",
    page_param="page"  # 参数名
)
```

---

## 🛠️ 常见问题解决

### Q1: 表格加载很慢怎么办？

**A:** 增加等待时间

```python
await scraper.scrape_with_button_pagination(
    ...
    wait_time=5.0  # 增加到 5 秒
)
```

或等待特定元素：

```python
await page.wait_for_selector("table tbody tr", timeout=10000)
```

---

### Q2: 表格是动态加载的（AJAX）

**A:** 等待网络请求完成

```python
# 等待网络空闲
await page.wait_for_load_state("networkidle")

# 或等待特定数据出现
await page.wait_for_selector("table tr[data-loaded='true']")
```

---

### Q3: 分页按钮被禁用怎么检测？

**A:** 检查按钮状态

```python
next_button = page.locator("button.next")

# 检查是否禁用
is_disabled = await next_button.is_disabled()
if is_disabled:
    print("已到最后一页")
    break

# 或检查 class
has_disabled_class = await next_button.evaluate(
    "el => el.classList.contains('disabled')"
)
```

---

### Q4: 如何处理验证码或登录？

**A:** 使用 `connect` 模式，在抓取前手动登录

```bash
# 1. 启动 Chrome
chrome.exe --remote-debugging-port=9222

# 2. 手动登录网站

# 3. 运行脚本
python agent_scrape_table.py
```

---

### Q5: 表格结构复杂，有合并单元格

**A:** 使用 BeautifulSoup 自定义解析

```python
from bs4 import BeautifulSoup

# 获取 HTML
html = await page.content()
soup = BeautifulSoup(html, 'html.parser')

# 自定义解析逻辑
table = soup.find('table', class_='complex')
for row in table.find_all('tr'):
    cells = row.find_all(['td', 'th'])
    # 处理 rowspan、colspan
    for cell in cells:
        rowspan = int(cell.get('rowspan', 1))
        colspan = int(cell.get('colspan', 1))
        # 你的逻辑...
```

---

## 📊 数据格式对比

### CSV 格式（推荐用于表格数据）

**优点：**
- ✅ Excel 可直接打开
- ✅ 文件小
- ✅ 易于导入数据库

**缺点：**
- ❌ 不支持复杂嵌套
- ❌ 特殊字符可能有问题

**示例：**
```csv
Name,Age,City
Alice,25,Beijing
Bob,30,Shanghai
```

---

### JSON 格式（推荐用于 API 交互）

**优点：**
- ✅ 支持嵌套结构
- ✅ 易于程序处理
- ✅ 保留数据类型

**缺点：**
- ❌ 文件较大
- ❌ 不能直接用 Excel 打开

**示例：**
```json
{
  "metadata": {
    "total_pages": 3,
    "total_rows": 150
  },
  "data": [
    {"Name": "Alice", "Age": 25, "City": "Beijing"},
    {"Name": "Bob", "Age": 30, "City": "Shanghai"}
  ]
}
```

---

## 🎯 实战检查清单

抓取前检查：

- [ ] 确认目标网站允许爬取（查看 robots.txt）
- [ ] 识别表格选择器
- [ ] 确定分页类型
- [ ] 测试单页提取
- [ ] 估算总页数
- [ ] 设置合理的等待时间
- [ ] 准备好保存路径

抓取中注意：

- [ ] 监控控制台输出
- [ ] 检查数据完整性
- [ ] 处理异常（网络错误、超时）
- [ ] 避免过于频繁的请求

抓取后验证：

- [ ] 打开 CSV/JSON 检查数据
- [ ] 验证行数是否正确
- [ ] 检查是否有重复数据
- [ ] 确认特殊字符正常显示

---

## 💡 高级技巧

### 技巧 1: 并发抓取（谨慎使用）

```python
import asyncio

# 同时抓取多个页面
tasks = [
    scraper.scrape_with_url_params(f"https://example.com?page={i}")
    for i in range(1, 11)
]
results = await asyncio.gather(*tasks)
```

⚠️ **注意：** 可能被网站限流或封禁

---

### 技巧 2: 增量更新

```python
# 读取已有数据
existing_data = pd.read_csv("data.csv")
last_id = existing_data['id'].max()

# 只抓取新数据
new_data = scraper.scrape_with_condition(
    lambda row: int(row['id']) > last_id
)
```

---

### 技巧 3: 数据清洗

```python
# 清理提取的数据
for row in data.rows:
    # 去除空格
    row = [cell.strip() for cell in row]
    
    # 转换数据类型
    row[1] = int(row[1])  # 年龄转整数
    
    # 处理空值
    row = [cell if cell else 'N/A' for cell in row]
```

---

## 📚 参考资源

- [Playwright 文档](https://playwright.dev/python/)
- [BeautifulSoup 文档](https://www.crummy.com/software/BeautifulSoup/)
- [CSS 选择器参考](https://www.w3schools.com/cssref/css_selectors.asp)
- [网页爬虫礼仪](https://www.robotstxt.org/)

---

## ⚖️ 法律与道德

**请遵守：**
- ✅ 查看并遵守 robots.txt
- ✅ 尊重网站服务条款
- ✅ 适当限制请求频率
- ✅ 标识爬虫身份（User-Agent）
- ✅ 仅用于个人学习和研究

**禁止：**
- ❌ 爬取受版权保护的内容
- ❌ 对网站造成性能影响
- ❌ 商业用途（未经许可）
- ❌ 规避反爬虫机制
- ❌ 爬取个人隐私数据

---

## 🆘 获取帮助

遇到问题？

1. 查看错误信息
2. 检查选择器是否正确
3. 使用 `analyze_table` 工具
4. 查看浏览器开发者工具
5. 提交 Issue

---

祝你抓取顺利！🎉