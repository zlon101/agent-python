"""
列表页与详情页合并抓取器核心实现
Merged Scraper Core Implementation
"""

import json
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from playwright.async_api import Page, TimeoutError as PlaywrightTimeout

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from puppeteer.universal_scraper import UniversalScraper, FieldConfig
from .config import MergedScraperConfig, NavigationMode


class MergedScraper:
    """
    列表页与详情页合并抓取器
    
    核心特性：
    1. 严格顺序执行：List Item A -> Detail A -> List Item B -> Detail B
    2. 数据不错配：每条记录携带唯一标识（list_page + item_index）
    3. 原子合并：列表数据和详情数据在同一次迭代中合并
    4. 错误隔离：单个详情页失败不影响其他项
    5. 状态追踪：完整记录每条数据的抓取状态
    """
    
    def __init__(self, page: Page, config: MergedScraperConfig):
        """
        初始化合并抓取器
        
        Args:
            page: Playwright页面对象
            config: 合并抓取器配置
        """
        self.page = page
        self.config = config
        self.merged_data: List[Dict[str, Any]] = []
        
        # 创建列表页抓取器
        self.list_scraper = UniversalScraper(page, config.list_config)
        
        # 统计信息
        self.stats = {
            "total_list_items": 0,
            "successful_details": 0,
            "failed_details": 0,
            "skipped_details": 0,
            "start_time": None,
            "end_time": None
        }
    
    async def _extract_detail_url(self, list_item: Dict[str, Any]) -> Optional[str]:
        """
        从列表项中提取详情页URL
        
        Args:
            list_item: 列表项数据
            
        Returns:
            详情页URL，如果提取失败返回None
        """
        url_value = list_item.get(self.config.detail_url_field)
        
        if not url_value:
            return None
        
        # 如果是字符串，直接返回
        if isinstance(url_value, str):
            # 检查是否是有效URL
            if url_value.startswith('http://') or url_value.startswith('https://'):
                return url_value
            # 相对URL，需要补全
            elif url_value.startswith('/'):
                base_url = self.page.url
                from urllib.parse import urljoin
                return urljoin(base_url, url_value)
            else:
                return None
        
        return None
    
    async def _scrape_detail_page(self, detail_url: str) -> Optional[Dict[str, Any]]:
        """
        抓取单个详情页数据
        
        Args:
            detail_url: 详情页URL
            
        Returns:
            详情页数据字典，失败返回None
        """
        try:
            # 导航到详情页
            await self.page.goto(detail_url, wait_until="domcontentloaded", timeout=30000)
            
            # 等待详情页容器加载
            await self.page.wait_for_selector(
                self.config.detail_container_selector,
                timeout=15000
            )
            
            # 额外等待时间
            await asyncio.sleep(self.config.detail_page_wait_time)
            
            # 提取详情页字段
            detail_data = {}
            for field in self.config.detail_fields:
                try:
                    value = await self._extract_detail_field(field)
                    detail_data[field.name] = value
                except Exception as e:
                    print(f"      ⚠️ 提取详情字段失败 [{field.name}]: {e}")
                    detail_data[field.name] = None
            
            return detail_data
            
        except PlaywrightTimeout as e:
            print(f"      ❌ 详情页加载超时: {str(e)[:100]}")
            return None
        except Exception as e:
            print(f"      ❌ 详情页抓取失败: {str(e)[:100]}")
            return None
    
    async def _extract_detail_field(self, field: FieldConfig) -> Any:
        """
        提取详情页单个字段的值
        
        Args:
            field: 字段配置
            
        Returns:
            字段值
        """
        locator = self.page.locator(field.selector)
        
        # 检查元素是否存在
        count = await locator.count()
        if count == 0:
            return None
        
        # 提取多个值
        if field.multiple:
            elements = await locator.all()
            values = []
            for elem in elements:
                if field.attribute:
                    val = await elem.get_attribute(field.attribute)
                else:
                    val = await elem.text_content()
                values.append(val.strip() if val else None)
            return values
        
        # 提取单个值
        if field.attribute:
            value = await locator.first.get_attribute(field.attribute)
        else:
            value = await locator.first.text_content()
        
        return value.strip() if value else None
    
    async def _navigate_back_to_list(self):
        """返回列表页"""
        if self.config.navigation_mode == NavigationMode.GO_BACK:
            # 使用浏览器返回
            await self.page.go_back(wait_until="domcontentloaded", timeout=15000)
            
            # 等待列表页稳定
            await asyncio.sleep(self.config.back_wait_time)
            
            # 验证列表页状态
            if self.config.verify_list_page_state:
                await self._verify_list_page_state()
        else:
            # 使用新标签页模式（当前未实现，可扩展）
            raise NotImplementedError("NEW_TAB 模式暂未实现")
    
    async def _verify_list_page_state(self):
        """验证返回列表页后的状态"""
        try:
            # 等待列表容器出现
            await self.page.wait_for_selector(
                self.config.list_config.container_selector,
                timeout=10000
            )
            
            # 等待网络空闲
            await self.page.wait_for_load_state("networkidle", timeout=10000)
            
        except Exception as e:
            print(f"      ⚠️ 列表页状态验证失败: {e}")
    
    async def scrape_list_item_with_detail(
        self,
        list_item: Dict[str, Any],
        item_index: int,
        page_num: int
    ) -> Dict[str, Any]:
        """
        抓取单个列表项及其详情页数据（核心方法）
        
        这是防止数据错配的关键：
        1. 在单个函数调用中完成列表+详情的数据获取
        2. 使用唯一标识（page_num + item_index）追踪
        3. 原子性合并数据
        
        Args:
            list_item: 列表项数据
            item_index: 项在当前列表页的索引
            page_num: 列表页码
            
        Returns:
            合并后的数据记录
        """
        print(f"   📝 处理第 {item_index + 1} 项...")
        
        # 初始化合并记录
        merged_item = {
            "list_data": list_item.copy(),  # 列表页数据
            "detail_data": {},  # 详情页数据（待填充）
            "metadata": {
                "list_page": page_num,
                "item_index": item_index,
                "detail_url": None,
                "scrape_status": "pending",
                "error_message": None,
                "scraped_at": datetime.now().isoformat()
            }
        }
        
        # 提取详情页URL
        detail_url = await self._extract_detail_url(list_item)
        merged_item["metadata"]["detail_url"] = detail_url
        
        if not detail_url:
            print(f"      ⚠️ 未找到详情页URL")
            merged_item["metadata"]["scrape_status"] = "skipped"
            merged_item["metadata"]["error_message"] = "详情页URL为空"
            self.stats["skipped_details"] += 1
            
            if self.config.skip_invalid_urls:
                return merged_item
        
        # 抓取详情页（带重试）
        detail_data = None
        retry_count = 0
        
        while retry_count <= self.config.max_detail_retries and detail_data is None:
            if retry_count > 0:
                print(f"      🔄 重试第 {retry_count} 次...")
            
            try:
                detail_data = await self._scrape_detail_page(detail_url)
                
                if detail_data:
                    print(f"      ✓ 详情页抓取成功")
                    merged_item["detail_data"] = detail_data
                    merged_item["metadata"]["scrape_status"] = "success"
                    self.stats["successful_details"] += 1
                else:
                    retry_count += 1
                    if retry_count <= self.config.max_detail_retries:
                        await asyncio.sleep(1)  # 重试前等待
                    
            except Exception as e:
                print(f"      ❌ 详情页抓取异常: {str(e)[:100]}")
                merged_item["metadata"]["error_message"] = str(e)
                retry_count += 1
                if retry_count <= self.config.max_detail_retries:
                    await asyncio.sleep(1)
        
        # 如果最终失败
        if not detail_data:
            merged_item["metadata"]["scrape_status"] = "failed"
            self.stats["failed_details"] += 1
            
            if not self.config.continue_on_error:
                raise Exception(f"详情页抓取失败且 continue_on_error=False")
        
        # 返回列表页
        try:
            await self._navigate_back_to_list()
        except Exception as e:
            print(f"      ⚠️ 返回列表页失败: {e}")
            merged_item["metadata"]["navigation_error"] = str(e)
        
        return merged_item
    
    async def scrape_current_list_page_with_details(
        self,
        page_num: int
    ) -> List[Dict[str, Any]]:
        """
        抓取当前列表页的所有项及其详情
        
        Args:
            page_num: 当前页码
            
        Returns:
            当前页所有合并后的数据
        """
        print(f"\n📄 抓取列表页第 {page_num} 页...")
        
        # 抓取列表页数据
        list_items = await self.list_scraper.scrape_current_page()
        
        if not list_items:
            print(f"   ⚠️ 列表页无数据")
            return []
        
        print(f"   找到 {len(list_items)} 个列表项")
        self.stats["total_list_items"] += len(list_items)
        
        page_merged_data = []
        
        # 顺序处理每个列表项
        for index, list_item in enumerate(list_items):
            merged_item = await self.scrape_list_item_with_detail(
                list_item=list_item,
                item_index=index,
                page_num=page_num
            )
            page_merged_data.append(merged_item)
            
            # 部分保存（可选）
            if self.config.save_partial_results and len(page_merged_data) % 5 == 0:
                self._save_partial_results()
        
        return page_merged_data
    
    async def scrape_with_pagination(self) -> List[Dict[str, Any]]:
        """
        执行分页抓取（列表页+详情页）
        
        核心流程：
        For each 列表页:
            For each 列表项:
                抓取详情页
                合并数据
                返回列表页
            翻到下一页
        
        Returns:
            所有合并后的数据
        """
        self.stats["start_time"] = datetime.now().isoformat()
        current_page = 1
        
        while True:
            # 检查是否达到最大页数
            if self.config.list_config.max_pages > 0 and \
               current_page > self.config.list_config.max_pages:
                print(f"\n✅ 达到最大页数: {self.config.list_config.max_pages}")
                break
            
            # 抓取当前列表页及其详情
            try:
                page_data = await self.scrape_current_list_page_with_details(current_page)
                self.merged_data.extend(page_data)
                
            except Exception as e:
                print(f"\n❌ 列表页 {current_page} 抓取失败: {e}")
                if not self.config.continue_on_error:
                    break
            
            # 检查是否有下一页
            if not self.config.list_config.next_button_selector:
                print("\n✅ 无分页配置，抓取完成")
                break
            
            # 查找下一页按钮
            next_button = self.page.locator(self.config.list_config.next_button_selector)
            
            try:
                count = await next_button.count()
                if count == 0:
                    print("\n✅ 未找到下一页按钮")
                    break
                
                is_visible = await next_button.first.is_visible()
                is_enabled = await next_button.first.is_enabled()
                
                if not is_visible or not is_enabled:
                    print("\n✅ 下一页按钮不可用")
                    break
                
                # 点击下一页
                print(f"\n🔄 翻到第 {current_page + 1} 页...")
                await next_button.first.click()
                
                # 等待页面加载
                await asyncio.sleep(self.config.list_config.delay)
                await self.page.wait_for_load_state("networkidle", timeout=15000)
                
                current_page += 1
                
            except Exception as e:
                print(f"\n✅ 分页结束: {str(e)[:100]}")
                break
        
        self.stats["end_time"] = datetime.now().isoformat()
        return self.merged_data
    
    async def scrape_from_current_page(self) -> List[Dict[str, Any]]:
        """
        从当前页面开始抓取（不导航到list_config.url）
        适用于已经打开列表页的场景
        
        Returns:
            所有合并后的数据
        """
        print(f"\n{'='*60}")
        print(f"🚀 开始合并抓取")
        print(f"{'='*60}")
        print(f"📍 当前页面: {self.page.url}")
        print(f"📋 列表容器: {self.config.list_config.container_selector}")
        print(f"📋 详情容器: {self.config.detail_container_selector}")
        
        # 等待列表页稳定
        await asyncio.sleep(self.config.list_config.delay)
        
        # 执行分页抓取
        data = await self.scrape_with_pagination()
        
        # 打印统计信息
        self._print_stats()
        
        return data
    
    async def scrape(self) -> List[Dict[str, Any]]:
        """
        执行抓取（从list_config.url开始）
        
        Returns:
            所有合并后的数据
        """
        # 导航到列表页
        print(f"\n🌐 访问列表页: {self.config.list_config.url}")
        await self.page.goto(self.config.list_config.url)
        await asyncio.sleep(self.config.list_config.delay)
        
        return await self.scrape_from_current_page()
    
    def _save_partial_results(self):
        """保存部分结果（内部使用）"""
        try:
            filename = "partial_merged_data.json"
            self._save_to_file(filename)
            print(f"      💾 部分结果已保存")
        except Exception as e:
            print(f"      ⚠️ 部分结果保存失败: {e}")
    
    def _save_to_file(self, filename: str):
        """保存数据到文件（内部使用）"""
        output = {
            "metadata": {
                "total_items": len(self.merged_data),
                "statistics": self.stats,
                "config": {
                    "list_url": self.config.list_config.url,
                    "list_fields": [f.name for f in self.config.list_config.fields],
                    "detail_fields": [f.name for f in self.config.detail_fields],
                    "detail_url_field": self.config.detail_url_field
                }
            },
            "data": self.merged_data
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
    
    def save_to_json(self, filename: str = "merged_data.json") -> str:
        """
        保存合并后的数据到JSON文件
        
        Args:
            filename: 文件名
            
        Returns:
            保存结果信息
        """
        if not self.merged_data:
            return "❌ 无数据可保存"
        
        self._save_to_file(filename)
        
        print(f"\n{'='*60}")
        print(f"💾 数据已保存到: {filename}")
        print(f"{'='*60}")
        print(f"📊 总条目: {len(self.merged_data)}")
        print(f"✅ 成功: {self.stats['successful_details']}")
        print(f"❌ 失败: {self.stats['failed_details']}")
        print(f"⏭️  跳过: {self.stats['skipped_details']}")
        
        return filename
    
    def _print_stats(self):
        """打印统计信息"""
        print(f"\n{'='*60}")
        print(f"📊 抓取统计")
        print(f"{'='*60}")
        print(f"📋 列表项总数: {self.stats['total_list_items']}")
        print(f"✅ 详情页成功: {self.stats['successful_details']}")
        print(f"❌ 详情页失败: {self.stats['failed_details']}")
        print(f"⏭️  详情页跳过: {self.stats['skipped_details']}")
        
        if self.stats['total_list_items'] > 0:
            success_rate = (self.stats['successful_details'] / 
                          self.stats['total_list_items'] * 100)
            print(f"📈 成功率: {success_rate:.1f}%")
        
        print(f"{'='*60}")
    
    def get_data(self) -> List[Dict[str, Any]]:
        """获取抓取的数据"""
        return self.merged_data
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        return self.stats.copy()
