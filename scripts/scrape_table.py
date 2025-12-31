#!/usr/bin/env python3
"""
一键抓取表格 - 简化命令行工具
快速抓取分页表格数据，无需编写代码
"""

import asyncio
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from browser import BrowserManager
from puppeteer import TableScraper


async def quick_scrape(args):
    """快速抓取表格"""
    
    print("\n" + "="*60)
    print("🚀 一键抓取表格")
    print("="*60 + "\n")
    
    print(f"📋 配置:")
    print(f"   URL: {args.url}")
    print(f"   表格选择器: {args.table}")
    print(f"   分页类型: {args.pagination_type}")
    print(f"   最大页数: {args.max_pages}")
    print(f"   输出文件: {args.output}\n")
    
    try:
        async with BrowserManager(mode=args.mode) as bm:
            page = await bm.get_or_create_page()
            scraper = TableScraper(page)
            
            # 1. 导航到页面
            print(f"🌐 访问: {args.url}")
            await page.goto(args.url)
            await page.wait_for_load_state("networkidle")
            print("   ✓ 页面加载完成\n")
            
            # 2. 根据分页类型抓取
            if args.pagination_type == "button":
                print(f"📄 使用按钮分页抓取...")
                if not args.next_button:
                    print("❌ 错误: 按钮分页需要 --next-button 参数")
                    return
                
                await scraper.scrape_with_button_pagination(
                    table_selector=args.table,
                    next_button_selector=args.next_button,
                    max_pages=args.max_pages,
                    wait_time=args.wait
                )
            
            elif args.pagination_type == "url":
                print(f"📄 使用 URL 参数分页抓取...")
                await scraper.scrape_with_url_params(
                    base_url=args.url,
                    table_selector=args.table,
                    page_param=args.page_param,
                    start_page=1,
                    max_pages=args.max_pages,
                    wait_time=args.wait
                )
            
            elif args.pagination_type == "none":
                print(f"📄 提取单页表格...")
                data = await scraper.extract_table(table_selector=args.table)
                scraper.all_data.append(data)
            
            else:
                print(f"❌ 不支持的分页类型: {args.pagination_type}")
                return
            
            # 3. 保存数据
            print()
            if args.output.endswith('.json'):
                scraper.save_to_json(args.output)
            else:
                scraper.save_to_csv(args.output)
            
            # 4. 显示摘要
            merged = scraper.merge_all_data()
            print(f"\n✅ 抓取完成!")
            print(f"   总页数: {merged['total_pages']}")
            print(f"   总行数: {merged['total_rows']}")
            print(f"   列数: {len(merged['headers'])}")
            print(f"   文件: {args.output}")
    
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="一键抓取分页表格数据",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:

  # 抓取单页表格
  python scrape_table.py https://example.com/data --table "table.data" -o output.csv

  # 抓取按钮分页表格（前5页）
  python scrape_table.py https://example.com/products \\
      --table "table#products" \\
      --pagination button \\
      --next-button "button.next" \\
      --max-pages 5 \\
      -o products.csv

  # 抓取 URL 参数分页表格
  python scrape_table.py "https://example.com/search?q=python" \\
      --table "table.results" \\
      --pagination url \\
      --page-param page \\
      --max-pages 10 \\
      -o results.json

  # 使用已打开的 Chrome
  python scrape_table.py https://example.com/data \\
      --mode connect \\
      --table "table" \\
      -o data.csv
        """
    )
    
    # 必需参数
    parser.add_argument(
        "url",
        help="目标页面 URL"
    )
    
    # 表格配置
    parser.add_argument(
        "--table", "-t",
        default="table",
        help="表格 CSS 选择器 (默认: 'table')"
    )
    
    parser.add_argument(
        "--output", "-o",
        default="output.csv",
        help="输出文件名 (支持 .csv 和 .json)"
    )
    
    # 分页配置
    parser.add_argument(
        "--pagination", "-p",
        choices=["none", "button", "url"],
        default="none",
        help="分页类型 (none=单页, button=按钮, url=URL参数)"
    )
    
    parser.add_argument(
        "--next-button",
        help="下一页按钮选择器 (pagination=button 时需要)"
    )
    
    parser.add_argument(
        "--page-param",
        default="page",
        help="URL 页码参数名 (pagination=url 时使用)"
    )
    
    parser.add_argument(
        "--max-pages",
        type=int,
        default=10,
        help="最大抓取页数 (默认: 10)"
    )
    
    parser.add_argument(
        "--wait",
        type=float,
        default=2.0,
        help="每页等待时间(秒) (默认: 2.0)"
    )
    
    # 浏览器配置
    parser.add_argument(
        "--mode",
        choices=["launch", "connect"],
        default="launch",
        help="浏览器模式 (默认: launch)"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="无头模式运行"
    )
    
    # 辅助功能
    parser.add_argument(
        "--version", "-v",
        action="version",
        version="Quick Scrape v1.0.0"
    )
    
    args = parser.parse_args()
    
    # 保存为实例变量
    args.pagination_type = args.pagination
    
    # 运行
    try:
        asyncio.run(quick_scrape(args))
    except KeyboardInterrupt:
        print("\n\n👋 用户中断")


if __name__ == "__main__":
    main()