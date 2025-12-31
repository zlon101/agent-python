"""
分页表格数据提取工具
支持多种分页方式和表格格式
"""

import json
import csv
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
from playwright.async_api import Page, Locator
from bs4 import BeautifulSoup
import asyncio


@dataclass
class TableData:
    """表格数据结构"""
    headers: List[str]
    rows: List[List[str]]
    page_number: int
    total_rows: int


@dataclass
class PaginationConfig:
    """分页配置"""
    # 分页类型: "button" | "number" | "infinite_scroll" | "url_param"
    type: str
    
    # 下一页按钮选择器（type="button"）
    next_button_selector: Optional[str] = None
    
    # 页码选择器（type="number"）
    page_number_selector: Optional[str] = None
    
    # URL 参数名（type="url_param"）
    url_param_name: Optional[str] = None
    
    # 最大页数（0 表示无限制）
    max_pages: int = 0
    
    # 等待时间（秒）
    wait_time: float = 2.0


class TableScraper:
    """表格数据提取器"""
    
    def __init__(self, page: Page):
        """
        初始化表格提取器
        
        Args:
            page: Playwright 页面对象
        """
        self.page = page
        self.all_data: List[TableData] = []
    
    async def extract_table(
        self,
        table_selector: str = "table",
        headers_selector: str = "thead th",
        rows_selector: str = "tbody tr",
        cells_selector: str = "td"
    ) -> TableData:
        """
        提取当前页表格数据
        
        Args:
            table_selector: 表格选择器
            headers_selector: 表头选择器
            rows_selector: 行选择器
            cells_selector: 单元格选择器
            
        Returns:
            TableData: 表格数据对象
        """
        # 等待表格加载
        await self.page.wait_for_selector(table_selector, timeout=10000)
        
        # 提取表头
        headers = await self.page.locator(headers_selector).all_text_contents()
        headers = [h.strip() for h in headers if h.strip()]
        
        # 提取行数据
        rows = []
        row_elements = await self.page.locator(rows_selector).all()
        
        for row_element in row_elements:
            cells = await row_element.locator(cells_selector).all_text_contents()
            cells = [c.strip() for c in cells]
            if cells:  # 跳过空行
                rows.append(cells)
        
        return TableData(
            headers=headers,
            rows=rows,
            page_number=len(self.all_data) + 1,
            total_rows=len(rows)
        )
    
    async def scrape_with_button_pagination(
        self,
        table_selector: str,
        next_button_selector: str,
        max_pages: int = 0,
        wait_time: float = 2.0
    ) -> List[TableData]:
        """
        使用"下一页"按钮分页抓取
        
        Args:
            table_selector: 表格选择器
            next_button_selector: 下一页按钮选择器
            max_pages: 最大页数（0 表示无限制）
            wait_time: 每页等待时间
            
        Returns:
            List[TableData]: 所有页面的数据
        """
        page_count = 0
        
        while True:
            # 检查是否达到最大页数
            if max_pages > 0 and page_count >= max_pages:
                print(f"✅ 达到最大页数限制: {max_pages}")
                break
            
            # 提取当前页数据
            print(f"📄 提取第 {page_count + 1} 页...")
            data = await self.extract_table(table_selector)
            self.all_data.append(data)
            page_count += 1
            
            print(f"   ✓ 提取 {data.total_rows} 行数据")
            
            # 检查是否有下一页按钮
            next_button = self.page.locator(next_button_selector)
            
            try:
                # 检查按钮是否存在且可点击
                is_visible = await next_button.is_visible()
                is_enabled = await next_button.is_enabled()
                
                if not is_visible or not is_enabled:
                    print("✅ 已到达最后一页（按钮不可用）")
                    break
                
                # 点击下一页
                await next_button.click()
                
                # 等待页面加载
                await asyncio.sleep(wait_time)
                
                # 等待表格更新（可选：检查表格变化）
                await self.page.wait_for_load_state("networkidle")
                
            except Exception as e:
                print(f"✅ 已到达最后一页: {str(e)}")
                break
        
        return self.all_data
    
    async def scrape_with_page_numbers(
        self,
        table_selector: str,
        page_number_selector: str,
        max_pages: int = 0,
        wait_time: float = 2.0
    ) -> List[TableData]:
        """
        使用页码分页抓取（1, 2, 3, ...）
        
        Args:
            table_selector: 表格选择器
            page_number_selector: 页码链接选择器模板（例如：'a.page-{page}'）
            max_pages: 最大页数
            wait_time: 每页等待时间
            
        Returns:
            List[TableData]: 所有页面的数据
        """
        page_count = 1
        
        # 提取第一页
        print(f"📄 提取第 {page_count} 页...")
        data = await self.extract_table(table_selector)
        self.all_data.append(data)
        print(f"   ✓ 提取 {data.total_rows} 行数据")
        
        # 循环提取后续页面
        while True:
            page_count += 1
            
            if max_pages > 0 and page_count > max_pages:
                print(f"✅ 达到最大页数限制: {max_pages}")
                break
            
            # 构造页码选择器
            selector = page_number_selector.replace("{page}", str(page_count))
            page_link = self.page.locator(selector)
            
            try:
                is_visible = await page_link.is_visible()
                if not is_visible:
                    print(f"✅ 已到达最后一页（页码 {page_count} 不存在）")
                    break
                
                print(f"📄 提取第 {page_count} 页...")
                
                # 点击页码
                await page_link.click()
                await asyncio.sleep(wait_time)
                await self.page.wait_for_load_state("networkidle")
                
                # 提取数据
                data = await self.extract_table(table_selector)
                self.all_data.append(data)
                print(f"   ✓ 提取 {data.total_rows} 行数据")
                
            except Exception as e:
                print(f"✅ 已到达最后一页: {str(e)}")
                break
        
        return self.all_data
    
    async def scrape_with_url_params(
        self,
        base_url: str,
        table_selector: str,
        page_param: str = "page",
        start_page: int = 1,
        max_pages: int = 0,
        wait_time: float = 2.0
    ) -> List[TableData]:
        """
        使用 URL 参数分页抓取（例如：?page=1, ?page=2）
        
        Args:
            base_url: 基础 URL
            table_selector: 表格选择器
            page_param: 页码参数名
            start_page: 起始页码
            max_pages: 最大页数
            wait_time: 每页等待时间
            
        Returns:
            List[TableData]: 所有页面的数据
        """
        page_count = start_page
        
        while True:
            if max_pages > 0 and (page_count - start_page + 1) > max_pages:
                print(f"✅ 达到最大页数限制: {max_pages}")
                break
            
            # 构造 URL
            separator = "&" if "?" in base_url else "?"
            url = f"{base_url}{separator}{page_param}={page_count}"
            
            print(f"📄 提取第 {page_count} 页...")
            print(f"   URL: {url}")
            
            try:
                # 导航到页面
                await self.page.goto(url)
                await asyncio.sleep(wait_time)
                
                # 检查表格是否存在
                table = self.page.locator(table_selector)
                is_visible = await table.is_visible()
                
                if not is_visible:
                    print(f"✅ 已到达最后一页（表格不存在）")
                    break
                
                # 提取数据
                data = await self.extract_table(table_selector)
                
                # 检查是否有数据
                if data.total_rows == 0:
                    print(f"✅ 已到达最后一页（无数据）")
                    break
                
                self.all_data.append(data)
                print(f"   ✓ 提取 {data.total_rows} 行数据")
                
                page_count += 1
                
            except Exception as e:
                print(f"✅ 已到达最后一页: {str(e)}")
                break
        
        return self.all_data
    
    def merge_all_data(self) -> Dict[str, Any]:
        """
        合并所有页面的数据
        
        Returns:
            dict: 合并后的数据
        """
        if not self.all_data:
            return {"headers": [], "rows": [], "total_pages": 0, "total_rows": 0}
        
        # 使用第一页的表头
        headers = self.all_data[0].headers
        
        # 合并所有行
        all_rows = []
        for page_data in self.all_data:
            all_rows.extend(page_data.rows)
        
        return {
            "headers": headers,
            "rows": all_rows,
            "total_pages": len(self.all_data),
            "total_rows": len(all_rows)
        }
    
    def save_to_csv(self, filename: str = "table_data.csv"):
        """保存为 CSV 文件"""
        merged = self.merge_all_data()
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(merged["headers"])
            writer.writerows(merged["rows"])
        
        print(f"💾 数据已保存到: {filename}")
        print(f"   总页数: {merged['total_pages']}")
        print(f"   总行数: {merged['total_rows']}")
    
    def save_to_json(self, filename: str = "table_data.json"):
        """保存为 JSON 文件"""
        merged = self.merge_all_data()
        
        # 转换为字典列表
        data_list = []
        headers = merged["headers"]
        for row in merged["rows"]:
            row_dict = {headers[i]: row[i] for i in range(len(headers))}
            data_list.append(row_dict)
        
        output = {
            "metadata": {
                "total_pages": merged["total_pages"],
                "total_rows": merged["total_rows"],
                "headers": headers
            },
            "data": data_list
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2)
        
        print(f"💾 数据已保存到: {filename}")
        print(f"   总页数: {merged['total_pages']}")
        print(f"   总行数: {merged['total_rows']}")