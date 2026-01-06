"""
通用可视化工具使用示例
展示如何使用 Visualizer 类处理任意数据
"""
from visualizer import Visualizer
import numpy as np


def example_basic_charts():
    """
    基础图表示例
    
    该函数演示了如何使用 Visualizer 类生成三种基本图表：
    1. 柱状图：用于展示2024年上半年的月度销售额。
    2. 折线图：用于显示月平均气温的变化趋势。
    3. 饼图：用于表示移动操作系统的市场份额。
    
    生成的图表将保存在 `output_基础` 目录下。
    """
    print("=" * 60)
    print("示例 1: 基础图表")
    print("=" * 60)
    
    viz = Visualizer(output_dir="output_基础")
    
    # 1. 柱状图示例
    sales_data = {
        '一月': 12000,
        '二月': 15000,
        '三月': 18000,
        '四月': 14000,
        '五月': 20000,
        '六月': 22000,
    }
    
    viz.bar_chart(
        data=sales_data,
        title='2024年上半年销售额统计',
        xlabel='月份',
        ylabel='销售额(元)',
        filename='example_sales_bar.png'
    )
    
    # 2. 折线图示例
    temperature_data = {
        '1月': -2,
        '2月': 0,
        '3月': 8,
        '4月': 15,
        '5月': 22,
        '6月': 28,
    }
    
    viz.line_chart(
        data=temperature_data,
        title='月平均气温变化',
        xlabel='月份',
        ylabel='温度(°C)',
        filename='example_temperature_line.png'
    )
    
    # 3. 饼图示例
    market_share = {
        'iOS': 28.5,
        'Android': 71.2,
        '其他': 0.3,
    }
    
    viz.pie_chart(
        data=market_share,
        title='移动操作系统市场份额',
        filename='example_market_pie.png'
    )
    
    print("\n✓ 基础图表示例完成!")


def example_advanced_charts():
    """
    高级图表示例
    
    该函数展示了如何生成更复杂的高级图表：
    1. 堆积柱状图：用于比较各城市不同产品的销售分布。
    2. 横向柱状图：用于展示员工的绩效排名，并只显示前8名。
    3. 热力图：用于可视化各部门在不同季度的任务完成率。
    
    生成的图表将保存在 `output_高级` 目录下。
    """
    print("\n" + "=" * 60)
    print("示例 2: 高级图表")
    print("=" * 60)
    
    viz = Visualizer(output_dir="output_高级")
    
    # 1. 堆积柱状图示例
    product_sales = {
        '北京': {'产品A': 1200, '产品B': 800, '产品C': 600},
        '上海': {'产品A': 1500, '产品B': 1000, '产品C': 500},
        '广州': {'产品A': 900, '产品B': 700, '产品C': 400},
        '深圳': {'产品A': 1100, '产品B': 900, '产品C': 550},
    }
    
    viz.stacked_bar_chart(
        data=product_sales,
        title='各城市产品销售分布',
        xlabel='城市',
        ylabel='销售额(万元)',
        filename='example_product_stacked.png'
    )
    
    # 2. 横向柱状图示例
    employee_performance = {
        '张三': 95,
        '李四': 88,
        '王五': 92,
        '赵六': 85,
        '钱七': 90,
        '孙八': 87,
        '周九': 93,
        '吴十': 89,
    }
    
    viz.horizontal_bar_chart(
        data=employee_performance,
        title='员工绩效排名',
        xlabel='得分',
        filename='example_performance_horizontal.png',
        top_n=8
    )
    
    # 3. 热力图示例
    # 假设这是各部门各季度的完成率数据
    heatmap_data = [
        [85, 92, 88, 95],  # 研发部
        [90, 88, 93, 91],  # 销售部
        [78, 82, 85, 88],  # 市场部
        [95, 96, 94, 97],  # 运营部
        [88, 85, 89, 90],  # 人事部
    ]
    
    departments = ['研发部', '销售部', '市场部', '运营部', '人事部']
    quarters = ['Q1', 'Q2', 'Q3', 'Q4']
    
    viz.heatmap(
        data=heatmap_data,
        row_labels=departments,
        col_labels=quarters,
        title='各部门季度完成率热力图',
        filename='example_department_heatmap.png'
    )
    
    print("\n✓ 高级图表示例完成!")


def example_dashboard():
    """
    仪表盘示例
    
    该函数演示了如何创建一个包含多种图表的综合仪表盘，用于展示业务数据的概览。
    仪表盘中包含：
    - 区域业绩的柱状图
    - 产品品类占比的饼图
    - 月度营收趋势的折线图
    - 关键业务数据的文本摘要
    
    生成的仪表盘将保存在 `output_仪表盘` 目录下。
    """
    print("\n" + "=" * 60)
    print("示例 3: 综合仪表盘")
    print("=" * 60)

    viz = Visualizer(output_dir="output_仪表盘")

    # 准备数据
    monthly_revenue = {'1月': 120, '2月': 135, '3月': 150, '4月': 142, '5月': 168, '6月': 180}
    category_sales = {'电子产品': 45, '服装': 30, '食品': 15, '其他': 10}
    region_performance = {'华东': 280, '华南': 220, '华北': 250, '西南': 180}
    
    stats_text = """
    业务数据概览
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    总营收: 895 万元
    总订单: 12,458 单
    客户满意度: 4.8/5.0
    环比增长: +12.5%
    """
    
    # 配置仪表盘
    charts_config = [
        (331, 'bar', region_performance, {'title': '区域业绩', 'color': '#3498DB'}),
        (332, 'pie', category_sales, {'title': '品类占比'}),
        (333, 'line', monthly_revenue, {'title': '月度营收', 'color': '#E74C3C'}),
        (313, 'text', stats_text, {'fontsize': 11}),
    ]
    
    viz.multi_chart_dashboard(
        charts_config=charts_config,
        title='业务数据综合仪表盘',
        filename='example_business_dashboard.png'
    )
    
    print("\n✓ 仪表盘示例完成!")


def example_custom_data():
    """
    自定义数据可视化示例
    
    该函数展示了如何处理自定义数据并进行可视化。
    它模拟了一组科学实验的成功率数据，并将其转换为字典格式，
    然后使用柱状图来对比不同实验的成功率。
    
    生成的图表将保存在 `output_自定义` 目录下。
    """
    print("\n" + "=" * 60)
    print("示例 4: 自定义数据处理")
    print("=" * 60)

    viz = Visualizer(output_dir="output_自定义")

    # 模拟一些科学数据
    experiments = ['实验A', '实验B', '实验C', '实验D', '实验E']
    success_rates = [0.85, 0.92, 0.78, 0.88, 0.95]
    
    # 转换为字典
    data = dict(zip(experiments, [rate * 100 for rate in success_rates]))
    
    viz.bar_chart(
        data=data,
        title='实验成功率对比',
        xlabel='实验编号',
        ylabel='成功率(%)',
        filename='example_experiment_success.png',
        color='#2ECC71'
    )
    
    print("\n✓ 自定义数据示例完成!")


def main():
    """
    主程序入口
    
    该函数将按顺序执行所有示例函数，以全面展示 `Visualizer` 类的功能。
    运行此脚本将生成一系列示例图表，并将其保存在不同的输出目录中。
    """
    print("=" * 60)
    print("通用可视化工具使用示例")
    print("=" * 60)
    print()
    print("这些示例展示了如何使用 Visualizer 类处理各种类型的数据")
    print()
    
    # 运行所有示例
    example_basic_charts()
    example_advanced_charts()
    example_dashboard()
    example_custom_data()
    
    print("\n" + "=" * 60)
    print("✓ 所有示例完成!")
    print("✓ 查看 output/ 目录查看生成的图表")
    print("=" * 60)


if __name__ == '__main__':
    main()
