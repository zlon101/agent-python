"""
浏览器步骤执行器
支持按步骤自动化操作浏览器
"""

import asyncio
import json
from typing import List, Dict, Optional, Any, Literal
from dataclasses import dataclass, asdict
from playwright.async_api import Page
from enum import Enum


class StepType(str, Enum):
    """步骤类型"""
    NAVIGATE = "navigate"           # 打开URL
    CLICK = "click"                 # 点击元素
    INPUT = "input"                 # 输入文本
    SELECT = "select"               # 选择下拉框
    WAIT = "wait"                   # 等待
    EXTRACT = "extract"             # 提取数据
    PRESS_KEY = "press_key"         # 按键
    SCROLL = "scroll"               # 滚动


@dataclass
class StepConfig:
    """步骤配置"""
    type: StepType                   # 步骤类型
    selector: Optional[str] = None   # CSS选择器
    value: Optional[str] = None      # 输入值/URL
    wait_time: float = 1.0           # 等待时间（秒）
    description: str = ""            # 步骤描述
    
    # 数据提取相关
    container_selector: Optional[str] = None  # 容器选择器
    fields: Optional[Dict[str, str]] = None   # 提取字段
    next_button: Optional[str] = None         # 下一页按钮
    max_pages: int = 1                        # 最大页数
    output_file: str = "output.json"          # 输出文件


class BrowserStepExecutor:
    """浏览器步骤执行器"""
    
    def __init__(self, page: Page):
        """
        初始化执行器
        
        Args:
            page: Playwright页面对象
        """
        self.page = page
        self.execution_log: List[Dict[str, Any]] = []
    
    async def execute_steps(self, steps: List[StepConfig]) -> Dict[str, Any]:
        """
        执行步骤序列
        
        Args:
            steps: 步骤配置列表
            
        Returns:
            执行结果
        """
        print("\n" + "="*60)
        print("🚀 开始执行浏览器自动化步骤")
        print("="*60 + "\n")
        
        results = {
            "success": True,
            "steps_executed": 0,
            "extracted_data": None,
            "errors": []
        }
        
        for i, step in enumerate(steps, 1):
            try:
                print(f"📍 步骤 {i}/{len(steps)}: {step.type.value}")
                if step.description:
                    print(f"   描述: {step.description}")
                
                result = await self._execute_single_step(step)
                
                # 记录执行日志
                self.execution_log.append({
                    "step_number": i,
                    "type": step.type.value,
                    "description": step.description,
                    "success": result.get("success", True),
                    "result": result
                })
                
                results["steps_executed"] += 1
                
                # 如果是提取步骤，保存数据
                if step.type == StepType.EXTRACT and result.get("data"):
                    results["extracted_data"] = result["data"]
                
                print(f"   ✅ 完成\n")
                
            except Exception as e:
                error_msg = f"步骤 {i} 执行失败: {str(e)}"
                print(f"   ❌ {error_msg}\n")
                results["errors"].append(error_msg)
                results["success"] = False
                
                # 可选：是否继续执行
                # break
        
        print("="*60)
        print(f"✅ 执行完成: {results['steps_executed']}/{len(steps)} 步骤成功")
        print("="*60 + "\n")
        
        return results
    
    async def _execute_single_step(self, step: StepConfig) -> Dict[str, Any]:
        """执行单个步骤"""
        
        if step.type == StepType.NAVIGATE:
            return await self._step_navigate(step)
        
        elif step.type == StepType.CLICK:
            return await self._step_click(step)
        
        elif step.type == StepType.INPUT:
            return await self._step_input(step)
        
        elif step.type == StepType.SELECT:
            return await self._step_select(step)
        
        elif step.type == StepType.WAIT:
            return await self._step_wait(step)
        
        elif step.type == StepType.EXTRACT:
            return await self._step_extract(step)
        
        elif step.type == StepType.PRESS_KEY:
            return await self._step_press_key(step)
        
        elif step.type == StepType.SCROLL:
            return await self._step_scroll(step)
        
        else:
            raise ValueError(f"未知的步骤类型: {step.type}")
    
    async def _step_navigate(self, step: StepConfig) -> Dict[str, Any]:
        """导航到URL"""
        url = step.value
        if not url:
            raise ValueError("导航步骤需要提供URL")
        
        print(f"   🌐 访问: {url}")
        await self.page.goto(url)
        await asyncio.sleep(step.wait_time)
        
        return {"success": True, "url": url}
    
    async def _step_click(self, step: StepConfig) -> Dict[str, Any]:
        """点击元素"""
        if not step.selector:
            raise ValueError("点击步骤需要提供选择器")
        
        print(f"   🖱️  点击: {step.selector}")
        
        # 等待元素可见
        await self.page.wait_for_selector(step.selector, timeout=10000)
        
        # 点击
        await self.page.click(step.selector)
        await asyncio.sleep(step.wait_time)
        
        return {"success": True, "selector": step.selector}
    
    async def _step_input(self, step: StepConfig) -> Dict[str, Any]:
        """输入文本"""
        if not step.selector:
            raise ValueError("输入步骤需要提供选择器")
        if not step.value:
            raise ValueError("输入步骤需要提供文本")
        
        print(f"   ⌨️  输入到 {step.selector}: {step.value}")
        
        # 等待元素
        await self.page.wait_for_selector(step.selector, timeout=10000)
        
        # 清空并输入
        await self.page.fill(step.selector, step.value)
        await asyncio.sleep(step.wait_time)
        
        return {"success": True, "selector": step.selector, "value": step.value}
    
    async def _step_select(self, step: StepConfig) -> Dict[str, Any]:
        """选择下拉框选项"""
        if not step.selector:
            raise ValueError("选择步骤需要提供选择器")
        if not step.value:
            raise ValueError("选择步骤需要提供选项值")
        
        print(f"   📋 选择 {step.selector}: {step.value}")
        
        # 等待元素
        await self.page.wait_for_selector(step.selector, timeout=10000)
        
        # 选择选项
        await self.page.select_option(step.selector, step.value)
        await asyncio.sleep(step.wait_time)
        
        return {"success": True, "selector": step.selector, "value": step.value}
    
    async def _step_wait(self, step: StepConfig) -> Dict[str, Any]:
        """等待"""
        wait_time = step.wait_time
        print(f"   ⏱️  等待 {wait_time} 秒")
        
        await asyncio.sleep(wait_time)
        
        return {"success": True, "wait_time": wait_time}
    
    async def _step_press_key(self, step: StepConfig) -> Dict[str, Any]:
        """按键"""
        if not step.value:
            raise ValueError("按键步骤需要提供按键名称")
        
        key = step.value
        print(f"   ⌨️  按键: {key}")
        
        await self.page.keyboard.press(key)
        await asyncio.sleep(step.wait_time)
        
        return {"success": True, "key": key}
    
    async def _step_scroll(self, step: StepConfig) -> Dict[str, Any]:
        """滚动页面"""
        print(f"   📜 滚动页面")
        
        if step.value:
            # 滚动到指定元素
            await self.page.locator(step.value).scroll_into_view_if_needed()
        else:
            # 滚动到底部
            await self.page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        
        await asyncio.sleep(step.wait_time)
        
        return {"success": True}
    
    async def _step_extract(self, step: StepConfig) -> Dict[str, Any]:
        """提取数据"""
        print(f"   📊 提取数据")
        
        if not step.container_selector or not step.fields:
            raise ValueError("提取步骤需要提供容器选择器和字段配置")
        
        # 导入抓取器
        from ..universal_scraper import UniversalScraper, create_scraper_config
        
        # 创建配置
        config = create_scraper_config(
            url=self.page.url,
            fields=step.fields,
            container_selector=step.container_selector,
            next_button_selector=step.next_button,
            delay=step.wait_time,
            max_pages=step.max_pages
        )
        
        # 执行抓取
        scraper = UniversalScraper(self.page, config)
        
        if step.next_button and step.max_pages > 1:
            # 分页抓取
            data = await scraper.scrape_with_pagination()
        else:
            # 单页抓取
            data = await scraper.scrape_current_page()
        
        print(f"   ✓ 提取了 {len(data)} 条数据")
        
        # 保存数据
        output_file = step.output_file or "output.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"   ✓ 保存到: {output_file}")
        
        return {"success": True, "data": data, "output_file": output_file}
    
    def get_execution_log(self) -> List[Dict[str, Any]]:
        """获取执行日志"""
        return self.execution_log
    
    def save_log(self, filename: str = "execution_log.json"):
        """保存执行日志"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.execution_log, f, ensure_ascii=False, indent=2)
        print(f"💾 执行日志已保存到: {filename}")


# 便捷函数

def create_navigate_step(url: str, wait_time: float = 1.0, description: str = "") -> StepConfig:
    """创建导航步骤"""
    return StepConfig(
        type=StepType.NAVIGATE,
        value=url,
        wait_time=wait_time,
        description=description or f"打开 {url}"
    )


def create_click_step(selector: str, wait_time: float = 1.0, description: str = "") -> StepConfig:
    """创建点击步骤"""
    return StepConfig(
        type=StepType.CLICK,
        selector=selector,
        wait_time=wait_time,
        description=description or f"点击 {selector}"
    )


def create_input_step(selector: str, value: str, wait_time: float = 1.0, description: str = "") -> StepConfig:
    """创建输入步骤"""
    return StepConfig(
        type=StepType.INPUT,
        selector=selector,
        value=value,
        wait_time=wait_time,
        description=description or f"在 {selector} 输入 {value}"
    )


def create_select_step(selector: str, value: str, wait_time: float = 1.0, 
                      description: str = "") -> StepConfig:
    """创建选择步骤"""
    return StepConfig(
        type=StepType.SELECT,
        selector=selector,
        value=value,
        wait_time=wait_time,
        description=description or f"选择 {selector}: {value}"
    )


def create_extract_step(
    container_selector: str,
    fields: Dict[str, str],
    next_button: Optional[str] = None,
    max_pages: int = 1,
    wait_time: float = 3.0,
    output_file: str = "output.json",
    description: str = ""
) -> StepConfig:
    """创建提取步骤"""
    return StepConfig(
        type=StepType.EXTRACT,
        container_selector=container_selector,
        fields=fields,
        next_button=next_button,
        max_pages=max_pages,
        wait_time=wait_time,
        output_file=output_file,
        description=description or "提取页面数据"
    )


def create_press_key_step(key: str, wait_time: float = 1.0, description: str = "") -> StepConfig:
    """创建按键步骤"""
    return StepConfig(
        type=StepType.PRESS_KEY,
        value=key,
        wait_time=wait_time,
        description=description or f"按键: {key}"
    )


def create_wait_step(wait_time: float, description: str = "") -> StepConfig:
    """创建等待步骤"""
    return StepConfig(
        type=StepType.WAIT,
        wait_time=wait_time,
        description=description or f"等待 {wait_time} 秒"
    )
