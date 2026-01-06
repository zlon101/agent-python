"""
云效任务数据可视化模块 - 通用架构版本

核心组件:
- Visualizer: 通用可视化工具类,提供各种图表生成方法

使用方法:
    # 生成所有图表
    task_viz.generate_all_charts()
    
    # 或生成单个图表
    task_viz.generate_project_chart()
"""

from .visualizer import Visualizer

__version__ = '2.0.0'
__all__ = ['Visualizer']
