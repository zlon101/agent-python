"""
合并抓取器配置
Configuration for Merged Scraper
"""

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from puppeteer.universal_scraper import ScraperConfig, FieldConfig


class NavigationMode(Enum):
    """页面导航模式"""
    GO_BACK = "go_back"  # 使用浏览器返回按钮
    NEW_TAB = "new_tab"  # 使用新标签页


@dataclass
class MergedScraperConfig:
    """
    列表页与详情页合并抓取配置
    
    核心思路：
    1. 使用list_config配置列表页抓取
    2. 从列表数据中提取详情页URL
    3. 访问详情页并抓取detail_fields配置的字段
    4. 将列表数据和详情数据合并保存
    """
    
    # ========== 列表页配置 ==========
    list_config: ScraperConfig  # 列表页抓取配置（复用UniversalScraper配置）
    
    # ========== 详情页配置 ==========
    detail_fields: List[FieldConfig]  # 详情页要抓取的字段
    detail_container_selector: str  # 详情页容器选择器（用于等待页面加载）
    detail_url_field: str  # 列表数据中哪个字段是详情页URL
    detail_url_attribute: str = "href"  # 详情URL的属性（默认href）
    
    # ========== 导航配置 ==========
    navigation_mode: NavigationMode = NavigationMode.GO_BACK  # 导航模式
    back_wait_time: float = 2.0  # 返回列表页后的等待时间（秒）
    detail_page_wait_time: float = 2.0  # 详情页加载等待时间（秒）
    
    # ========== 容错配置 ==========
    max_detail_retries: int = 2  # 详情页抓取最大重试次数
    continue_on_error: bool = True  # 详情页失败时是否继续抓取
    skip_invalid_urls: bool = True  # 是否跳过无效的详情页URL
    
    # ========== 高级配置 ==========
    verify_list_page_state: bool = True  # 返回列表页后是否验证页面状态
    save_partial_results: bool = True  # 是否在抓取过程中保存部分结果
    
    def __post_init__(self):
        """配置验证"""
        if not self.list_config:
            raise ValueError("list_config 不能为空")
        
        if not self.detail_fields:
            raise ValueError("detail_fields 不能为空")
        
        if not self.detail_container_selector:
            raise ValueError("detail_container_selector 不能为空")
        
        if not self.detail_url_field:
            raise ValueError("detail_url_field 不能为空")
        
        # 验证detail_url_field是否在list_config的fields中
        list_field_names = [field.name for field in self.list_config.fields]
        if self.detail_url_field not in list_field_names:
            raise ValueError(
                f"detail_url_field '{self.detail_url_field}' "
                f"必须是list_config.fields中的一个字段"
            )


def create_merged_scraper_config(
    list_config: ScraperConfig,
    detail_fields: dict,  # {"字段名": "CSS选择器"}
    detail_container_selector: str,
    detail_url_field: str,
    detail_url_attribute: str = "href",
    navigation_mode: str = "go_back",
    back_wait_time: float = 2.0,
    detail_page_wait_time: float = 2.0,
    max_detail_retries: int = 2,
    continue_on_error: bool = True
) -> MergedScraperConfig:
    """
    创建合并抓取器配置（便捷函数）
    
    Args:
        list_config: 列表页抓取配置
        detail_fields: 详情页字段配置字典 {"字段名": "CSS选择器"}
        detail_container_selector: 详情页容器选择器
        detail_url_field: 列表数据中哪个字段是详情页URL
        detail_url_attribute: 详情URL的属性
        navigation_mode: 导航模式 "go_back" 或 "new_tab"
        back_wait_time: 返回列表页后的等待时间
        detail_page_wait_time: 详情页加载等待时间
        max_detail_retries: 详情页抓取最大重试次数
        continue_on_error: 详情页失败时是否继续
        
    Returns:
        MergedScraperConfig对象
    """
    # 转换detail_fields为FieldConfig列表
    detail_field_configs = [
        FieldConfig(name=name, selector=selector)
        for name, selector in detail_fields.items()
    ]
    
    # 转换导航模式
    nav_mode = NavigationMode.GO_BACK if navigation_mode == "go_back" else NavigationMode.NEW_TAB
    
    return MergedScraperConfig(
        list_config=list_config,
        detail_fields=detail_field_configs,
        detail_container_selector=detail_container_selector,
        detail_url_field=detail_url_field,
        detail_url_attribute=detail_url_attribute,
        navigation_mode=nav_mode,
        back_wait_time=back_wait_time,
        detail_page_wait_time=detail_page_wait_time,
        max_detail_retries=max_detail_retries,
        continue_on_error=continue_on_error
    )
