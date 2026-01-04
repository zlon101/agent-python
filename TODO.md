# Task
success ! 当前项目基础上新增功能，根据用户指定的步骤，操作浏览器。操作的类型有：打开某个url、点击按钮、选择select、输入框搜索、抓取页面数据

# Example

## input
按照以下步骤操作浏览器：
1. 打开 https://segmentfault.com/
2. 在 `#react-aria-3 input.form-control` 中输入 "langchain" 并回车
3. 点击 `a[data-rr-ui-event-key='search?q=langchain&type=article']`
5. 提取页面中的数据
  - 容器选择器：.row div.list-group li
  - 需要提取的字段：
    * 标题: h5
    * 时间: .mb-0.font-size-14
  - 下一页按钮: .d-none .page-item:last-child .page-link
  - 抓取2页，每页停留3秒
  - 保存为 segmentfault_result.json


## output
```json
[
  {
    "标题": "adgsdf",
    "时间": "2025-11-07",
  },
  {
    "标题": "asdg4",
    "时间": "2025-11-09",
  },
]
```


=================

# Task
更新 /Users/admins/work/openai/lib/browser/manager.py 中的 get_or_create_page，让用户可以连接到当前打开的浏览器，查找用户指定的url对应的标签页，在这个标签页上进行操作