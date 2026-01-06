"""
可视化配置文件
"""

# 图表样式配置
CHART_CONFIG = {
    # 图表尺寸
    'figsize': {
        'bar': (12, 6),
        'line': (14, 6),
        'pie': (10, 8),
        'stacked_bar': (14, 7),
        'horizontal_bar': (12, 10),
        'heatmap': (16, 8),
        'dashboard': (16, 10),
    },
    
    # 颜色方案
    'colors': {
        'primary': ['#E74C3C', '#3498DB', '#2ECC71', '#F39C12', '#9B59B6', 
                    '#1ABC9C', '#E67E22', '#95A5A6'],
        'bar': '#4A90E2',
        'line': '#E74C3C',
    },
    
    # 字体大小
    'fontsize': {
        'title': 14,
        'label': 12,
        'tick': 9,
        'legend': 10,
    },
    
    # DPI设置
    'dpi': 300,
}

