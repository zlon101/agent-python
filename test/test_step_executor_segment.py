"""
用户需求实现 - SegmentFault 搜索并抓取
按照用户指定的步骤自动化操作浏览器
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from browser import BrowserManager
from puppeteer import (
    BrowserStepExecutor,
    create_navigate_step,
    create_input_step,
    create_press_key_step,
    create_click_step,
    create_extract_step
)


async def user_requirement():
    """
    用户需求：
    1. 打开 https://segmentfault.com/
    2. 在搜索框中输入 "langchain" 并回车
    3. 点击文章标签
    4. 提取页面数据（2页）
    5. 保存为 segmentfault_result.json
    """
    
    print("\n" + "="*60)
    print("🎯 执行用户需求：SegmentFault 搜索 + 数据抓取")
    print("="*60 + "\n")
    
    async with BrowserManager(mode="connect", headless=False) as bm:
        page = await bm.get_or_create_page(target_url="https://segmentfault.com/")
        
        # 创建步骤执行器
        executor = BrowserStepExecutor(page)
        
        # 定义步骤（完全按照用户需求）
        steps = [
            # # 步骤 1: 打开 SegmentFault
            # create_navigate_step(
            #     url="https://segmentfault.com/",
            #     wait_time=2.0,
            #     description="打开 SegmentFault 首页"
            # ),
            
            # # 步骤 2: 在搜索框输入 "langchain" 并回车
            # create_input_step(
            #     selector="#react-aria-3 input.form-control",
            #     value="langchain",
            #     wait_time=1.0,
            #     description="在搜索框输入 'langchain'"
            # ),
            
            # create_press_key_step(
            #     key="Enter",
            #     wait_time=2.0,
            #     description="按回车键搜索"
            # ),
            
            # 步骤 3: 点击文章标签
            # create_click_step(
            #     selector="a[data-rr-ui-event-key='search?q=langchain&type=article']",
            #     wait_time=2.0,
            #     description="点击'文章'标签"
            # ),
            
            # 步骤 4-5: 提取数据
            create_extract_step(
                container_selector=".row div.list-group li",
                fields={
                    "标题": "h5",
                    "时间": ".mb-0.font-size-14"
                },
                next_button=".d-none .page-item:last-child .page-link",
                max_pages=1,
                wait_time=3.0,
                output_file="segmentfault_result.json",
                description="提取文章列表（抓取2页，每页停留3秒）"
            )
        ]
        
        # 执行步骤
        result = await executor.execute_steps(steps)
        
        # 显示结果
        print("\n" + "="*60)
        print("📊 执行结果")
        print("="*60 + "\n")
        
        if result["success"]:
            print("✅ 所有步骤执行成功！")
            
            if result["extracted_data"]:
                data_count = len(result["extracted_data"])
                print(f"\n📈 数据统计:")
                print(f"   总条数: {data_count}")
                print(f"   文件: segmentfault_result.json")
                
                # 显示前3条数据
                print(f"\n📄 数据预览（前3条）:")
                for i, item in enumerate(result["extracted_data"][:3], 1):
                    print(f"\n{i}.")
                    print(f"   标题: {item.get('标题', 'N/A')}")
                    print(f"   时间: {item.get('时间', 'N/A')}")
                
                # 保存执行日志
                executor.save_log("execution_log.json")
                print(f"\n💾 执行日志已保存: execution_log.json")
            else:
                print("\n⚠️ 未提取到数据")
        else:
            print("❌ 执行过程中出现错误:")
            for error in result["errors"]:
                print(f"   - {error}")
        
        print("\n" + "="*60)


if __name__ == "__main__":
    print("\n🤖 浏览器自动化 - 用户需求执行")
    print("按 Ctrl+C 可随时中断\n")
    
    try:
        asyncio.run(user_requirement())
    except KeyboardInterrupt:
        print("\n\n⚠️ 用户中断执行")
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()
