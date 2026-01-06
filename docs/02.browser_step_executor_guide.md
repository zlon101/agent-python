### 浏览器步骤执行器使用文档

## 📖 概述

浏览器步骤执行器允许你通过定义步骤序列来自动化操作浏览器，支持：
- ✅ 打开 URL
- ✅ 点击按钮
- ✅ 输入文本
- ✅ 选择下拉框
- ✅ 按键操作
- ✅ 等待
- ✅ 提取数据
- ✅ 滚动页面

---

## 🚀 快速开始

### 基础示例

```python
import asyncio
from browser import BrowserManager
from puppeteer import (
    BrowserStepExecutor,
    create_navigate_step,
    create_input_step,
    create_press_key_step,
    create_extract_step
)

async def main():
    async with BrowserManager(mode="launch") as bm:
        page = await bm.get_or_create_page()
        
        # 创建执行器
        executor = BrowserStepExecutor(page)
        
        # 定义步骤
        steps = [
            create_navigate_step(url="https://example.com"),
            create_input_step(selector="#search", value="keyword"),
            create_press_key_step(key="Enter"),
            create_extract_step(
                container_selector=".result",
                fields={"标题": "h2"}
            )
        ]
        
        # 执行
        result = await executor.execute_steps(steps)

asyncio.run(main())
```

---

## 📝 步骤类型

### 1. 导航步骤 (NAVIGATE)

打开指定 URL。

```python
step = create_navigate_step(
    url="https://segmentfault.com/",
    wait_time=2.0,
    description="打开首页"
)
```

---

### 2. 点击步骤 (CLICK)

点击页面元素。

```python
step = create_click_step(
    selector="button.submit",
    wait_time=1.0,
    description="点击提交按钮"
)
```

---

### 3. 输入步骤 (INPUT)

在输入框中输入文本。

```python
step = create_input_step(
    selector="#search-input",
    value="langchain",
    wait_time=1.0,
    description="输入搜索关键词"
)
```

---

### 4. 选择步骤 (SELECT)

选择下拉框选项。

```python
step = create_select_step(
    selector="#category",
    value="technology",
    wait_time=1.0,
    description="选择分类"
)
```

---

### 5. 按键步骤 (PRESS_KEY)

按下键盘按键。

```python
step = create_press_key_step(
    key="Enter",  # 或 "Tab", "Escape" 等
    wait_time=1.0,
    description="按回车键"
)
```

---

### 6. 等待步骤 (WAIT)

等待指定时间。

```python
step = create_wait_step(
    wait_time=5.0,
    description="等待页面加载"
)
```

---

### 7. 提取数据步骤 (EXTRACT)

提取页面数据。

```python
step = create_extract_step(
    container_selector=".list-item",
    fields={
        "标题": "h3",
        "时间": ".date"
    },
    next_button=".next-page",  # 可选：分页
    max_pages=2,
    wait_time=3.0,
    output_file="data.json",
    description="提取列表数据"
)
```

---

## 🎯 完整示例：用户需求

### 需求描述

```markdown
按照以下步骤操作浏览器：
1. 打开 https://segmentfault.com/
2. 在搜索框中输入 "langchain" 并回车
3. 点击"文章"标签
4. 提取数据（抓取2页）
5. 保存为 segmentfault_result.json
```

### 实现代码

```python
import asyncio
from browser import BrowserManager
from puppeteer import (
    BrowserStepExecutor,
    create_navigate_step,
    create_input_step,
    create_press_key_step,
    create_click_step,
    create_extract_step
)

async def segmentfault_search():
    async with BrowserManager(mode="launch", headless=False) as bm:
        page = await bm.get_or_create_page()
        executor = BrowserStepExecutor(page)
        
        steps = [
            # 步骤 1: 打开网站
            create_navigate_step(
                url="https://segmentfault.com/",
                wait_time=2.0,
                description="打开 SegmentFault"
            ),
            
            # 步骤 2: 输入搜索词并回车
            create_input_step(
                selector="#react-aria-3 input.form-control",
                value="langchain",
                wait_time=1.0,
                description="输入搜索关键词"
            ),
            
            create_press_key_step(
                key="Enter",
                wait_time=2.0,
                description="按回车搜索"
            ),
            
            # 步骤 3: 点击文章标签
            create_click_step(
                selector="a[data-rr-ui-event-key='search?q=langchain&type=article']",
                wait_time=2.0,
                description="点击文章标签"
            ),
            
            # 步骤 4-5: 提取并保存数据
            create_extract_step(
                container_selector=".row div.list-group li",
                fields={
                    "标题": "h5",
                    "时间": ".mb-0.font-size-14"
                },
                next_button=".d-none .page-item:last-child .page-link",
                max_pages=2,
                wait_time=3.0,
                output_file="segmentfault_result.json",
                description="提取文章列表"
            )
        ]
        
        # 执行步骤
        result = await executor.execute_steps(steps)
        
        # 保存执行日志
        executor.save_log("execution_log.json")
        
        # 输出结果
        if result["success"]:
            print(f"\n✅ 成功提取 {len(result['extracted_data'])} 条数据")
            print(f"数据已保存到: segmentfault_result.json")

asyncio.run(segmentfault_search())
```

### 输出结果

```json
[
  {
    "标题": "LangChain 入门教程",
    "时间": "2025-11-07"
  },
  {
    "标题": "使用 LangChain 构建 AI 应用",
    "时间": "2025-11-09"
  }
]
```

---

## 🔧 高级用法

### 1. 动态生成步骤

```python
async def search_multiple_keywords(keywords: list):
    async with BrowserManager(mode="launch") as bm:
        page = await bm.get_or_create_page()
        executor = BrowserStepExecutor(page)
        
        for keyword in keywords:
            steps = [
                create_navigate_step(url="https://example.com"),
                create_input_step(selector="#search", value=keyword),
                create_press_key_step(key="Enter"),
                create_extract_step(
                    container_selector=".result",
                    fields={"标题": "h2"},
                    output_file=f"{keyword}_result.json"
                )
            ]
            
            await executor.execute_steps(steps)
```

---

### 2. 错误处理

```python
result = await executor.execute_steps(steps)

if result["success"]:
    print("✅ 所有步骤执行成功")
else:
    print("❌ 执行失败:")
    for error in result["errors"]:
        print(f"   - {error}")
```

---

### 3. 查看执行日志

```python
# 执行步骤后
executor.save_log("execution_log.json")

# 或获取日志
log = executor.get_execution_log()
for entry in log:
    print(f"步骤 {entry['step_number']}: {entry['type']}")
    print(f"  成功: {entry['success']}")
```

---

## 📊 步骤配置详解

### StepConfig 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `type` | StepType | ✅ | 步骤类型 |
| `selector` | str | ❌ | CSS选择器 |
| `value` | str | ❌ | 输入值/URL |
| `wait_time` | float | ❌ | 等待时间（秒），默认1.0 |
| `description` | str | ❌ | 步骤描述 |
| `container_selector` | str | ❌ | 容器选择器（提取时用） |
| `fields` | dict | ❌ | 提取字段配置 |
| `next_button` | str | ❌ | 下一页按钮选择器 |
| `max_pages` | int | ❌ | 最大页数，默认1 |
| `output_file` | str | ❌ | 输出文件，默认output.json |

---

## 🧪 测试

### 运行示例

```bash
# 运行示例脚本
python examples/browser_step_executor.py

# 选择示例：
#   1. SegmentFault 搜索 + 抓取
#   2. 简单导航
#   3. 表单交互
#   4. 动态生成步骤
#   5. 自定义工作流
```

---

## 💡 最佳实践

### 1. 合理设置等待时间

```python
# 快速操作
wait_time=1.0

# 需要加载的页面
wait_time=2.0-3.0

# 慢速网站或复杂操作
wait_time=5.0
```

---

### 2. 使用描述信息

```python
step = create_navigate_step(
    url="https://example.com",
    description="打开首页"  # 便于调试和日志查看
)
```

---

### 3. 分步验证

```python
# 先测试单个步骤
steps = [
    create_navigate_step(url="https://example.com"),
]
await executor.execute_steps(steps)

# 确认无误后添加更多步骤
```

---

## ⚠️ 注意事项

1. **选择器准确性**：确保CSS选择器正确
2. **等待时间**：给予足够的页面加载时间
3. **动态内容**：对于AJAX加载的内容，增加等待时间
4. **错误处理**：检查执行结果中的错误信息

---

## 📚 相关文档

- 通用抓取器: `/Users/admins/work/openai/docs/universal_scraper_guide.md`
- 浏览器管理器: `/Users/admins/work/openai/docs/browser_manager_new_features.md`
- 示例代码: `/Users/admins/work/openai/examples/browser_step_executor.py`

---

## 🎯 总结

浏览器步骤执行器让你可以：
1. ✅ 按步骤自动化操作浏览器
2. ✅ 支持多种操作类型
3. ✅ 灵活组合步骤
4. ✅ 记录执行日志
5. ✅ 简单易用的API

立即开始使用：
```bash
python examples/browser_step_executor.py
```
