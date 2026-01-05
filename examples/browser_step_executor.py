"""
浏览器步骤执行器示例
演示如何按步骤自动化操作浏览器
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "lib"))
from browser import BrowserManager
from puppeteer import (
    BrowserStepExecutor,
    create_navigate_step,
    create_input_step,
    create_click_step,
    create_extract_step,
    create_press_key_step,
    create_wait_step
)


async def example_segmentfault_search():
    """
    示例：SegmentFault 搜索并抓取
    
    步骤：
    1. 打开 SegmentFault
    2. 输入搜索关键词
    3. 按回车搜索
    4. 点击文章标签
    5. 提取搜索结果
    """
    print("\n" + "="*60)
    print("📌 示例：SegmentFault 搜索 + 数据抓取")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        page = await bm.get_or_create_page()
        
        # 创建步骤执行器
        executor = BrowserStepExecutor(page)
        
        # 定义步骤
        steps = [
            # 步骤 1: 打开网站
            create_navigate_step(
                url="https://segmentfault.com/",
                wait_time=2.0,
                description="打开 SegmentFault 首页"
            ),
            
            # 步骤 2: 输入搜索词
            create_input_step(
                selector="#react-aria-3 input.form-control",
                value="langchain",
                wait_time=1.0,
                description="在搜索框输入 langchain"
            ),
            
            # 步骤 3: 按回车搜索
            create_press_key_step(
                key="Enter",
                wait_time=2.0,
                description="按回车键搜索"
            ),
            
            # 步骤 4: 点击"文章"标签
            create_click_step(
                selector="a[data-rr-ui-event-key='search?q=langchain&type=article']",
                wait_time=2.0,
                description="点击文章标签"
            ),
            
            # 步骤 5: 提取数据
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
                description="提取文章列表（2页）"
            )
        ]
        
        # 执行步骤
        result = await executor.execute_steps(steps)
        
        # 保存执行日志
        executor.save_log("execution_log.json")
        
        # 显示结果
        if result["success"]:
            print("\n✅ 所有步骤执行成功!")
            if result["extracted_data"]:
                print(f"\n📊 提取了 {len(result['extracted_data'])} 条数据")
                print(f"前3条数据预览:")
                for i, item in enumerate(result["extracted_data"][:3], 1):
                    print(f"\n{i}. {item}")
        else:
            print("\n❌ 执行过程中出现错误:")
            for error in result["errors"]:
                print(f"   - {error}")


async def example_simple_navigation():
    """
    简单示例：访问多个页面并截图
    """
    print("\n" + "="*60)
    print("📌 示例：简单导航 + 截图")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        page = await bm.get_or_create_page()
        executor = BrowserStepExecutor(page)
        
        steps = [
            create_navigate_step(
                url="https://github.com/trending",
                wait_time=2.0,
                description="访问 GitHub Trending"
            ),
            
            create_extract_step(
                container_selector="article.Box-row",
                fields={
                    "项目名": "h2 a",
                    "描述": "p.col-9"
                },
                max_pages=1,
                output_file="github_trending.json",
                description="提取热门项目"
            )
        ]
        
        result = await executor.execute_steps(steps)
        
        if result["extracted_data"]:
            print(f"\n✅ 提取了 {len(result['extracted_data'])} 个项目")


async def example_form_interaction():
    """
    示例：表单交互
    """
    print("\n" + "="*60)
    print("📌 示例：表单交互")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        page = await bm.get_or_create_page()
        executor = BrowserStepExecutor(page)
        
        steps = [
            create_navigate_step(
                url="https://example.com/form",
                wait_time=1.0
            ),
            
            create_input_step(
                selector="#username",
                value="testuser",
                description="输入用户名"
            ),
            
            create_input_step(
                selector="#password",
                value="password123",
                description="输入密码"
            ),
            
            create_click_step(
                selector="button[type='submit']",
                wait_time=2.0,
                description="点击提交按钮"
            )
        ]
        
        await executor.execute_steps(steps)


async def example_dynamic_steps():
    """
    示例：动态生成步骤
    """
    print("\n" + "="*60)
    print("📌 示例：动态生成步骤")
    print("="*60 + "\n")
    
    # 用户输入
    search_queries = ["python", "javascript", "rust"]
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        page = await bm.get_or_create_page()
        executor = BrowserStepExecutor(page)
        
        for query in search_queries:
            print(f"\n🔍 搜索: {query}\n")
            
            steps = [
                create_navigate_step(
                    url="https://segmentfault.com/",
                    wait_time=2.0
                ),
                
                create_input_step(
                    selector="#react-aria-3 input.form-control",
                    value=query,
                    description=f"搜索 {query}"
                ),
                
                create_press_key_step(
                    key="Enter",
                    wait_time=2.0
                ),
                
                create_extract_step(
                    container_selector=".row div.list-group li",
                    fields={"标题": "h5"},
                    max_pages=1,
                    output_file=f"{query}_results.json",
                    description=f"提取 {query} 搜索结果"
                )
            ]
            
            await executor.execute_steps(steps)


async def example_custom_workflow():
    """
    自定义工作流示例
    """
    print("\n" + "="*60)
    print("📌 示例：自定义工作流")
    print("="*60 + "\n")
    
    print("请输入你想执行的步骤:")
    print("1. URL to visit")
    print("2. Selector to click (optional)")
    print("3. Data to extract (optional)")
    
    url = input("\n1. URL: ").strip()
    click_selector = input("2. Click selector (留空跳过): ").strip()
    extract_container = input("3. Extract container selector (留空跳过): ").strip()
    
    if not url:
        print("❌ URL 不能为空")
        return
    
    async with BrowserManager(mode="launch", headless=False) as bm:
        page = await bm.get_or_create_page()
        executor = BrowserStepExecutor(page)
        
        steps = [
            create_navigate_step(url=url, wait_time=2.0)
        ]
        
        if click_selector:
            steps.append(
                create_click_step(selector=click_selector, wait_time=2.0)
            )
        
        if extract_container:
            field_selector = input("Field selector (e.g., h2): ").strip()
            if field_selector:
                steps.append(
                    create_extract_step(
                        container_selector=extract_container,
                        fields={"内容": field_selector},
                        max_pages=1,
                        output_file="custom_result.json"
                    )
                )
        
        await executor.execute_steps(steps)


async def main():
    """主菜单"""
    examples = {
        "1": ("SegmentFault 搜索 + 抓取", example_segmentfault_search),
        "2": ("简单导航", example_simple_navigation),
        "3": ("表单交互", example_form_interaction),
        "4": ("动态生成步骤", example_dynamic_steps),
        "5": ("自定义工作流", example_custom_workflow)
    }
    
    print("\n" + "="*60)
    print("🎓 浏览器步骤执行器示例")
    print("="*60)
    print("\n可用示例:")
    for key, (name, _) in examples.items():
        print(f"   {key}. {name}")
    
    choice = input("\n选择示例 (1-5): ").strip()
    
    if choice in examples:
        name, func = examples[choice]
        print(f"\n🚀 运行示例: {name}")
        await func()
    else:
        print("❌ 无效选择")


if __name__ == "__main__":
    asyncio.run(main())
