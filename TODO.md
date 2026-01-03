# task

在当前项目功能上，实现一个统计网页数据的通用功能，入参有网址、需要解析的dom内容、页码范围（可选）、下一页按钮选择器（可选）、切换页面的延迟时间，返回json格式的数据内容

# RULE

1. 用户指定一个网页的url，指定需要抓取的内容的css选择器，如果数据有分页，还会指定下一页按钮的css选择器
2. 根据用户提供的信息，解析页面dom结构，获取用户指定的信息，并且已json格式保存到本地文件
3. 可以配置点击下一页的延迟时间，需要采集的页数

# example

## input
打开 https://segmentfault.com/ 页面，获取 `.list-group.list-group-flush` 对应的列表数据，
采集的信息和对应的选择器如下：
"""
标题：h3 a.text-body
投票数量：.num-card .font-size-16
阅读数量：.num-card.text-secondary .font-size-16
"""

下一页按钮选择器是 `a.page-link`，页面至少停留5秒，


## output
```json
[
  {
    "标题": "xxx",
    "投票数量": 3,
    "阅读数量": 10
  },
  {
    "标题": "yyy",
    "投票数量": 5,
    "阅读数量": 20
  }
]
```