"""
通用数据可视化工具类
提供各种图表的通用生成方法
"""
import os
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from config import CHART_CONFIG

# 解决中文显示问题
matplotlib.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'STHeiti']
matplotlib.rcParams['axes.unicode_minus'] = False


class Visualizer:
    """
    通用可视化工具类
    
    该类封装了多种常见的图表生成方法，例如柱状图、折线图、饼图等。
    它使用 Matplotlib 库进行绘图，并提供了灵活的配置选项。
    """
    
    def __init__(self, output_dir, config=None):
        """
        初始化可视化工具
        
        Args:
            output_dir (str): 图表输出目录的路径。
            config (dict, optional): 自定义配置字典，如果未提供，则使用默认配置。 
                                     Defaults to None.
        """
        self.output_dir = output_dir
        self.config = config or CHART_CONFIG
        os.makedirs(self.output_dir, exist_ok=True)
    
    def bar_chart(self, data, title, xlabel, ylabel, filename, 
                  figsize=None, color=None, show_values=True, sort=False):
        """
        生成并保存一个柱状图。
        
        Args:
            data (dict or list): 图表数据，可以是 {标签: 值} 的字典或 [(标签, 值)] 的列表。
            title (str): 图表标题。
            xlabel (str): X轴标签。
            ylabel (str): Y轴标签。
            filename (str): 保存图表的文件名。
            figsize (tuple, optional): 图表尺寸。 Defaults to None.
            color (str, optional): 柱子颜色。 Defaults to None.
            show_values (bool, optional): 是否在柱子上方显示数值。 Defaults to True.
            sort (bool, optional): 是否按值对数据进行排序。 Defaults to False.
            
        Returns:
            str: 生成图表的文件路径。
        """
        # 数据处理
        if isinstance(data, dict):
            items = list(data.items())
        else:
            items = data
        
        if sort:
            items = sorted(items, key=lambda x: x[1], reverse=True)
        
        labels = [str(item[0]) for item in items]
        values = [float(item[1]) for item in items]
        
        # 配置
        figsize = figsize or self.config['figsize']['bar']
        color = color or self.config['colors']['bar']
        
        # 绘图
        plt.figure(figsize=figsize)
        bars = plt.bar(range(len(labels)), values, color=color)
        plt.xlabel(xlabel, fontsize=self.config['fontsize']['label'])
        plt.ylabel(ylabel, fontsize=self.config['fontsize']['label'])
        plt.title(title, fontsize=self.config['fontsize']['title'], fontweight='bold')
        plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3, linestyle='--')
        
        # 添加数值标签
        if show_values:
            for bar, value in zip(bars, values):
                plt.text(bar.get_x() + bar.get_width()/2, value, 
                        f'{value:.1f}', ha='center', va='bottom', fontsize=9)
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.config['dpi'], bbox_inches='tight')
        print(f"✓ 柱状图已生成: {filepath}")
        plt.close()
        
        return filepath
    
    def line_chart(self, data, title, xlabel, ylabel, filename,
                   figsize=None, color=None, fill=True, show_values=True):
        """
        生成并保存一个折线图。
        
        Args:
            data (dict or list): 图表数据。
            title (str): 图表标题。
            xlabel (str): X轴标签。
            ylabel (str): Y轴标签。
            filename (str): 保存图表的文件名。
            figsize (tuple, optional): 图表尺寸。 Defaults to None.
            color (str, optional): 线条颜色。 Defaults to None.
            fill (bool, optional): 是否填充线下方的区域。 Defaults to True.
            show_values (bool, optional): 是否在线条上显示数据点的值。 Defaults to True.
            
        Returns:
            str: 生成图表的文件路径。
        """
        # 数据处理
        if isinstance(data, dict):
            items = sorted(data.items())
        else:
            items = sorted(data)
        
        labels = [str(item[0]) for item in items]
        values = [float(item[1]) for item in items]
        
        # 配置
        figsize = figsize or self.config['figsize']['line']
        color = color or self.config['colors']['line']
        
        # 绘图
        plt.figure(figsize=figsize)
        plt.plot(range(len(labels)), values, marker='o', linewidth=2,
                markersize=6, color=color, label=ylabel)
        
        if fill:
            plt.fill_between(range(len(labels)), values, alpha=0.3, color=color)
        
        plt.xlabel(xlabel, fontsize=self.config['fontsize']['label'])
        plt.ylabel(ylabel, fontsize=self.config['fontsize']['label'])
        plt.title(title, fontsize=self.config['fontsize']['title'], fontweight='bold')
        plt.xticks(range(len(labels)), labels, rotation=45, ha='right')
        plt.grid(True, alpha=0.3, linestyle='--')
        plt.legend(loc='upper left')
        
        # 添加数值标签
        if show_values:
            for x, y in zip(range(len(labels)), values):
                if y > 0:
                    plt.text(x, y, f'{y:.1f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.config['dpi'], bbox_inches='tight')
        print(f"✓ 折线图已生成: {filepath}")
        plt.close()
        
        return filepath
    
    def pie_chart(self, data, title, filename, figsize=None, 
                  colors=None, show_legend=True):
        """
        生成并保存一个饼图。
        
        Args:
            data (dict): 图表数据，格式为 {标签: 值}。
            title (str): 图表标题。
            filename (str): 保存图表的文件名。
            figsize (tuple, optional): 图表尺寸。 Defaults to None.
            colors (list, optional): 颜色列表。 Defaults to None.
            show_legend (bool, optional): 是否显示图例。 Defaults to True.
            
        Returns:
            str: 生成图表的文件路径。
        """
        # 数据处理
        if isinstance(data, dict):
            items = sorted(data.items(), key=lambda x: x[1], reverse=True)
        else:
            items = sorted(data, key=lambda x: x[1], reverse=True)
        
        # 过滤掉0值
        items = [(k, v) for k, v in items if v > 0]
        
        labels = [str(item[0]) for item in items]
        sizes = [float(item[1]) for item in items]
        
        # 配置
        figsize = figsize or self.config['figsize']['pie']
        colors = colors or self.config['colors']['primary']
        
        # 绘图
        plt.figure(figsize=figsize)
        wedges, texts, autotexts = plt.pie(
            sizes, labels=labels, autopct='%1.1f%%',
            colors=colors[:len(labels)], startangle=90,
            textprops={'fontsize': 10}
        )
        
        # 美化百分比文字
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(9)
        
        plt.title(title, fontsize=self.config['fontsize']['title'], 
                 fontweight='bold', pad=20)
        
        # 添加图例
        if show_legend:
            legend_labels = [f'{label}: {size:.1f}' for label, size in zip(labels, sizes)]
            plt.legend(legend_labels, loc='center left', bbox_to_anchor=(1, 0, 0.5, 1))
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.config['dpi'], bbox_inches='tight')
        print(f"✓ 饼图已生成: {filepath}")
        plt.close()
        
        return filepath
    
    def stacked_bar_chart(self, data, title, xlabel, ylabel, filename,
                         figsize=None, colors=None):
        """
        生成并保存一个堆积柱状图。
        
        Args:
            data (dict): 图表数据，格式为 {主类别: {子类别: 值}}。
            title (str): 图表标题。
            xlabel (str): X轴标签。
            ylabel (str): Y轴标签。
            filename (str): 保存图表的文件名。
            figsize (tuple, optional): 图表尺寸。 Defaults to None.
            colors (list, optional): 颜色列表。 Defaults to None.
            
        Returns:
            str: 生成图表的文件路径。
        """
        # 准备数据
        categories = list(data.keys())
        subcategories = sorted(set(
            subcat for subdata in data.values() for subcat in subdata.keys()
        ))
        
        # 构建数据矩阵
        data_matrix = []
        for subcat in subcategories:
            row = [data[cat].get(subcat, 0) for cat in categories]
            data_matrix.append(row)
        
        # 配置
        figsize = figsize or self.config['figsize']['stacked_bar']
        colors = colors or self.config['colors']['primary']
        
        # 绘图
        fig, ax = plt.subplots(figsize=figsize)
        x = np.arange(len(categories))
        width = 0.6
        
        bottom = np.zeros(len(categories))
        for i, (subcat, values) in enumerate(zip(subcategories, data_matrix)):
            ax.bar(x, values, width, label=subcat, bottom=bottom,
                  color=colors[i % len(colors)])
            bottom += values
        
        ax.set_xlabel(xlabel, fontsize=self.config['fontsize']['label'])
        ax.set_ylabel(ylabel, fontsize=self.config['fontsize']['label'])
        ax.set_title(title, fontsize=self.config['fontsize']['title'], fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend(loc='upper left', bbox_to_anchor=(1, 1))
        ax.grid(axis='y', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.config['dpi'], bbox_inches='tight')
        print(f"✓ 堆积柱状图已生成: {filepath}")
        plt.close()
        
        return filepath
    
    def horizontal_bar_chart(self, data, title, xlabel, filename,
                            figsize=None, top_n=None, show_values=True):
        """
        生成并保存一个横向柱状图。
        
        Args:
            data (dict): 图表数据，格式为 {标签: 值}。
            title (str): 图表标题。
            xlabel (str): X轴标签。
            filename (str): 保存图表的文件名。
            figsize (tuple, optional): 图表尺寸。 Defaults to None.
            top_n (int, optional): 只显示前N个。 Defaults to None.
            show_values (bool, optional): 是否显示数值标签。 Defaults to True.
            
        Returns:
            str: 生成图表的文件路径。
        """
        # 数据处理
        if isinstance(data, dict):
            items = sorted(data.items(), key=lambda x: x[1], reverse=True)
        else:
            items = sorted(data, key=lambda x: x[1], reverse=True)
        
        if top_n:
            items = items[:top_n]
        
        # 截断过长的标签
        labels = [str(item[0])[:40] + '...' if len(str(item[0])) > 40 
                 else str(item[0]) for item in items]
        values = [float(item[1]) for item in items]
        
        # 配置
        figsize = figsize or self.config['figsize']['horizontal_bar']
        
        # 绘图
        plt.figure(figsize=figsize)
        y_pos = np.arange(len(labels))
        colors = plt.cm.RdYlGn_r(np.linspace(0.3, 0.7, len(labels)))
        bars = plt.barh(y_pos, values, color=colors)
        
        plt.xlabel(xlabel, fontsize=self.config['fontsize']['label'])
        plt.title(title, fontsize=self.config['fontsize']['title'], fontweight='bold')
        plt.yticks(y_pos, labels, fontsize=9)
        plt.grid(axis='x', alpha=0.3, linestyle='--')
        
        # 添加数值标签
        if show_values:
            for bar, value in zip(bars, values):
                plt.text(value, bar.get_y() + bar.get_height()/2, f' {value:.1f}',
                        va='center', fontsize=9, fontweight='bold')
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.config['dpi'], bbox_inches='tight')
        print(f"✓ 横向柱状图已生成: {filepath}")
        plt.close()
        
        return filepath
    
    def heatmap(self, data, row_labels, col_labels, title, filename,
                figsize=None, cmap=None, show_values=True):
        """
        生成并保存一个热力图。
        
        Args:
            data (list or np.ndarray): 二维数组或矩阵。
            row_labels (list): 行标签列表。
            col_labels (list): 列标签列表。
            title (str): 图表标题。
            filename (str): 保存图表的文件名。
            figsize (tuple, optional): 图表尺寸。 Defaults to None.
            cmap (str or Colormap, optional): 颜色映射。 Defaults to None.
            show_values (bool, optional): 是否在热力图单元格中显示数值。 Defaults to True.
            
        Returns:
            str: 生成图表的文件路径。
        """
        # 配置
        figsize = figsize or self.config['figsize']['heatmap']
        
        if cmap is None:
            colors_list = ['#ffffff', '#ffffcc', '#ffeda0', '#fed976', '#feb24c',
                          '#fd8d3c', '#fc4e2a', '#e31a1c', '#bd0026']
            cmap = LinearSegmentedColormap.from_list('custom', colors_list, N=100)
        
        # 确保数据是numpy数组
        matrix = np.array(data)
        
        # 绘图
        fig, ax = plt.subplots(figsize=figsize)
        im = ax.imshow(matrix, cmap=cmap, aspect='auto')
        
        # 设置坐标轴
        ax.set_xticks(np.arange(len(col_labels)))
        ax.set_yticks(np.arange(len(row_labels)))
        ax.set_xticklabels(col_labels, rotation=45, ha='right')
        ax.set_yticklabels(row_labels)
        
        # 添加数值标签
        if show_values:
            for i in range(len(row_labels)):
                for j in range(len(col_labels)):
                    if matrix[i, j] > 0:
                        text_color = "white" if matrix[i, j] > matrix.max()/2 else "black"
                        ax.text(j, i, f'{matrix[i, j]:.1f}',
                               ha="center", va="center", color=text_color,
                               fontsize=8, fontweight='bold')
        
        ax.set_title(title, fontsize=self.config['fontsize']['title'],
                    fontweight='bold', pad=20)
        
        # 添加颜色条
        cbar = plt.colorbar(im, ax=ax)
        cbar.set_label('值', rotation=270, labelpad=20)
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.config['dpi'], bbox_inches='tight')
        print(f"✓ 热力图已生成: {filepath}")
        plt.close()
        
        return filepath
    
    def multi_chart_dashboard(self, charts_config, title, filename, figsize=None):
        """
        生成并保存一个多图表仪表盘。
        
        Args:
            charts_config (list): 图表配置列表，每个元素为 
                                  (位置, 类型, 数据, 配置)。
            title (str): 总标题。
            filename (str): 保存文件名。
            figsize (tuple, optional): 图表尺寸。 Defaults to None.
            
        Returns:
            str: 生成图表的文件路径。
        """
        figsize = figsize or self.config['figsize']['dashboard']
        
        fig = plt.figure(figsize=figsize)
        
        # 根据配置绘制每个子图
        for position, chart_type, data, config in charts_config:
            ax = fig.add_subplot(position)
            
            if chart_type == 'bar':
                self._draw_bar_subplot(ax, data, config)
            elif chart_type == 'pie':
                self._draw_pie_subplot(ax, data, config)
            elif chart_type == 'line':
                self._draw_line_subplot(ax, data, config)
            elif chart_type == 'text':
                self._draw_text_subplot(ax, data, config)
        
        fig.suptitle(title, fontsize=16, fontweight='bold', y=0.98)
        
        plt.tight_layout()
        filepath = os.path.join(self.output_dir, filename)
        plt.savefig(filepath, dpi=self.config['dpi'], bbox_inches='tight')
        print(f"✓ 仪表盘已生成: {filepath}")
        plt.close()
        
        return filepath
    
    def _draw_bar_subplot(self, ax, data, config):
        """
        在给定的 `Axes` 对象上绘制一个柱状图子图。

        Args:
            ax (matplotlib.axes.Axes): 用于绘图的 `Axes` 对象。
            data (dict): 图表数据，格式为 {标签: 值}。
            config (dict): 图表配置。
        """
        labels = list(data.keys())
        values = list(data.values())
        ax.bar(range(len(labels)), values, color=config.get('color', '#3498DB'))
        ax.set_title(config.get('title', ''), fontweight='bold')
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
        ax.grid(axis='y', alpha=0.3)
    
    def _draw_pie_subplot(self, ax, data, config):
        """
        在给定的 `Axes` 对象上绘制一个饼图子图。

        Args:
            ax (matplotlib.axes.Axes): 用于绘图的 `Axes` 对象。
            data (dict): 图表数据，格式为 {标签: 值}。
            config (dict): 图表配置。
        """
        labels = list(data.keys())
        sizes = list(data.values())
        colors = config.get('colors', self.config['colors']['primary'])
        ax.pie(sizes, labels=labels, autopct='%1.1f%%', colors=colors, startangle=90)
        ax.set_title(config.get('title', ''), fontweight='bold')
    
    def _draw_line_subplot(self, ax, data, config):
        """
        在给定的 `Axes` 对象上绘制一个折线图子图。

        Args:
            ax (matplotlib.axes.Axes): 用于绘图的 `Axes` 对象。
            data (dict): 图表数据，格式为 {标签: 值}。
            config (dict): 图表配置。
        """
        labels = list(data.keys())
        values = list(data.values())
        color = config.get('color', '#E74C3C')
        ax.plot(range(len(labels)), values, marker='o', color=color, linewidth=2)
        ax.fill_between(range(len(labels)), values, alpha=0.3, color=color)
        ax.set_title(config.get('title', ''), fontweight='bold')
        ax.set_xticks(range(len(labels)))
        ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def _draw_text_subplot(self, ax, text, config):
        """
        在给定的 `Axes` 对象上绘制一个文本子图。

        Args:
            ax (matplotlib.axes.Axes): 用于绘图的 `Axes` 对象。
            text (str): 要显示的文本。
            config (dict): 文本配置。
        """
        ax.axis('off')
        ax.text(0.1, 0.5, text, fontsize=config.get('fontsize', 11),
               verticalalignment='center', fontfamily='monospace',
               bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
