"""
测试浏览器步骤执行器
验证基本功能是否正常
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))


async def test_import():
    """测试导入"""
    print("\n" + "="*60)
    print("🧪 测试 1: 导入模块")
    print("="*60 + "\n")
    
    try:
        from puppeteer import (
            BrowserStepExecutor,
            StepType,
            StepConfig,
            create_navigate_step,
            create_input_step,
            create_click_step,
            create_extract_step,
            create_press_key_step,
            create_wait_step
        )
        print("✅ 所有模块导入成功")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_step_creation():
    """测试步骤创建"""
    print("\n" + "="*60)
    print("🧪 测试 2: 创建步骤配置")
    print("="*60 + "\n")
    
    try:
        from puppeteer import (
            create_navigate_step,
            create_input_step,
            create_extract_step
        )
        
        # 创建各种步骤
        nav_step = create_navigate_step(url="https://example.com")
        input_step = create_input_step(selector="#search", value="test")
        extract_step = create_extract_step(
            container_selector=".item",
            fields={"标题": "h2"}
        )
        
        print(f"✅ 导航步骤: {nav_step.type.value}")
        print(f"✅ 输入步骤: {input_step.type.value}")
        print(f"✅ 提取步骤: {extract_step.type.value}")
        
        return True
    except Exception as e:
        print(f"❌ 创建步骤失败: {e}")
        return False


async def test_executor_basic():
    """测试基础执行器功能"""
    print("\n" + "="*60)
    print("🧪 测试 3: 执行器基础功能")
    print("="*60 + "\n")
    
    try:
        from browser import BrowserManager
        from puppeteer import (
            BrowserStepExecutor,
            create_navigate_step,
            create_wait_step
        )
        
        async with BrowserManager(mode="launch", headless=False) as bm:
            page = await bm.get_or_create_page()
            
            # 创建执行器
            executor = BrowserStepExecutor(page)
            print("✅ 执行器创建成功")
            
            # 简单步骤
            steps = [
                create_navigate_step(
                    url="https://example.com",
                    wait_time=2.0,
                    description="访问 Example.com"
                ),
                create_wait_step(
                    wait_time=2.0,
                    description="等待2秒"
                )
            ]
            
            # 执行
            print("\n开始执行步骤...\n")
            result = await executor.execute_steps(steps)
            
            print(f"\n执行结果:")
            print(f"  成功: {result['success']}")
            print(f"  执行步骤数: {result['steps_executed']}")
            print(f"  错误数: {len(result['errors'])}")
            
            if result['success']:
                print("\n✅ 基础功能测试通过")
                return True
            else:
                print("\n❌ 执行失败")
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_full_workflow():
    """测试完整工作流（包括数据提取）"""
    print("\n" + "="*60)
    print("🧪 测试 4: 完整工作流（导航 + 提取）")
    print("="*60 + "\n")
    
    try:
        from browser import BrowserManager
        from puppeteer import (
            BrowserStepExecutor,
            create_navigate_step,
            create_extract_step
        )
        
        async with BrowserManager(mode="launch", headless=False) as bm:
            page = await bm.get_or_create_page()
            executor = BrowserStepExecutor(page)
            
            steps = [
                create_navigate_step(
                    url="https://github.com/trending",
                    wait_time=3.0,
                    description="访问 GitHub Trending"
                ),
                
                create_extract_step(
                    container_selector="article.Box-row",
                    fields={
                        "项目名": "h2 a",
                        "描述": "p.col-9"
                    },
                    max_pages=1,
                    wait_time=2.0,
                    output_file="test_github_trending.json",
                    description="提取热门项目"
                )
            ]
            
            result = await executor.execute_steps(steps)
            
            if result['success'] and result['extracted_data']:
                data_count = len(result['extracted_data'])
                print(f"\n✅ 完整工作流测试通过")
                print(f"   提取了 {data_count} 条数据")
                
                if data_count > 0:
                    print(f"\n示例数据:")
                    print(f"   {result['extracted_data'][0]}")
                
                return True
            else:
                print("\n❌ 工作流执行失败")
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🧪 浏览器步骤执行器 - 功能测试")
    print("="*60)
    
    tests = [
        ("导入模块", test_import),
        ("创建步骤", test_step_creation),
        ("基础执行", test_executor_basic),
        ("完整工作流", test_full_workflow)
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ 测试 '{name}' 异常: {e}")
            results.append((name, False))
    
    # 汇总
    print("\n" + "="*60)
    print("📊 测试汇总")
    print("="*60 + "\n")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！")
    else:
        print("\n⚠️ 部分测试失败，请检查")


async def quick_test():
    """快速测试（只测试导入和创建）"""
    print("\n" + "="*60)
    print("⚡ 快速测试")
    print("="*60)
    
    success = await test_import()
    if success:
        success = await test_step_creation()
    
    if success:
        print("\n✅ 快速测试通过！")
        print("运行完整测试: python test_step_executor.py --full")
    else:
        print("\n❌ 快速测试失败")


async def main():
    """主函数"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--full":
        await run_all_tests()
    else:
        await quick_test()


if __name__ == "__main__":
    asyncio.run(main())
