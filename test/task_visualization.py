"""
云效任务数据可视化 - 业务层
使用通用可视化工具生成具体的业务图表
"""

import sys
from pathlib import Path
import json
from collections import defaultdict
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
from visualization import Visualizer

# 数据文件路径
DATA_FILE = '/Users/admins/work/openai/test_云效任务类型人天统计.json'

# 任务类型映射
TASK_TYPE_MAPPING = {
    'A': "需求评审",
    'B': "技术方案",
    'C': "技术开发",
    'D': "联调冒烟",
    'E': "测试执行",
    'F': "代码CR",
    'G': "跟测",
    'I': "跟测",
}

"""
数据处理器
负责从原始数据中提取和聚合可视化所需的数据
"""
class DataProcessor:
    def __init__(self, data_file=None):
        """
        初始化数据处理器
        
        Args:
            data_file: 数据文件路径
        """
        self.data_file = data_file or DATA_FILE
        self.raw_data = None
        self.load_data()
    
    def load_data(self):
        """加载数据"""
        with open(self.data_file, 'r', encoding='utf-8') as f:
            self.raw_data = json.load(f)
        return self.raw_data
    
    @staticmethod
    def parse_workdays(workdays):
        """解析人天数据"""
        if workdays is None or workdays == '':
            return 0
        try:
            return float(workdays)
        except:
            return 0
    
    @staticmethod
    def extract_task_type(title):
        """提取任务类型"""
        if not title:
            return "其他"
        
        for key, value in TASK_TYPE_MAPPING.items():
            if title.startswith(f'{key}.') or title.startswith(f'{key}、'):
                return value
        return "其他"
    
    def get_project_workdays(self):
        """
        获取各项目人天统计
        
        Returns:
            dict: {项目名: 人天数}
        """
        project_workdays = defaultdict(float)
        
        for item in self.raw_data['data']:
            project = item.get('项目', '未知项目')
            workdays = self.parse_workdays(item.get('人天'))
            project_workdays[project] += workdays
        
        return dict(project_workdays)
    
    def get_monthly_workdays(self):
        """
        获取月度人天统计
        
        Returns:
            dict: {月份: 人天数}
        """
        monthly_workdays = defaultdict(float)
        
        for item in self.raw_data['data']:
            start_time = item.get('开始时间', '')
            if not start_time or start_time == '--':
                continue
            
            try:
                date = datetime.strptime(start_time, '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                workdays = self.parse_workdays(item.get('人天'))
                monthly_workdays[month_key] += workdays
            except:
                continue
        
        return dict(monthly_workdays)
    
    def get_task_type_workdays(self):
        """
        获取任务类型人天统计
        
        Returns:
            dict: {任务类型: 人天数}
        """
        task_type_workdays = defaultdict(float)
        
        for item in self.raw_data['data']:
            title = item.get('标题', '')
            task_type = self.extract_task_type(title)
            workdays = self.parse_workdays(item.get('人天'))
            task_type_workdays[task_type] += workdays
        
        # 过滤掉0值
        return {k: v for k, v in task_type_workdays.items() if v > 0}
    
    def get_project_task_distribution(self):
        """
        获取项目×任务类型分布数据
        
        Returns:
            dict: {项目: {任务类型: 人天数}}
        """
        project_task_data = defaultdict(lambda: defaultdict(float))
        
        for item in self.raw_data['data']:
            project = item.get('项目', '未知项目')
            task_type = self.extract_task_type(item.get('标题', ''))
            workdays = self.parse_workdays(item.get('人天'))
            project_task_data[project][task_type] += workdays
        
        return {k: dict(v) for k, v in project_task_data.items()}
    
    def get_top_tasks(self, top_n=15):
        """
        获取人天最多的任务
        
        Args:
            top_n: 返回前N个任务
            
        Returns:
            list: [(任务标题, 人天数), ...]
        """
        task_workdays = []
        
        for item in self.raw_data['data']:
            title = item.get('标题', '')
            workdays = self.parse_workdays(item.get('人天'))
            if workdays > 0:
                task_workdays.append((title, workdays))
        
        task_workdays.sort(key=lambda x: x[1], reverse=True)
        return task_workdays[:top_n]
    
    def get_month_task_matrix(self):
        """
        获取月份×任务类型矩阵数据
        
        Returns:
            tuple: (matrix, row_labels, col_labels)
                - matrix: 二维数组
                - row_labels: 任务类型列表
                - col_labels: 月份列表
        """
        month_task_data = defaultdict(lambda: defaultdict(float))
        
        for item in self.raw_data['data']:
            start_time = item.get('开始时间', '')
            if not start_time or start_time == '--':
                continue
            
            try:
                date = datetime.strptime(start_time, '%Y-%m-%d')
                month_key = date.strftime('%Y-%m')
                task_type = self.extract_task_type(item.get('标题', ''))
                workdays = self.parse_workdays(item.get('人天'))
                month_task_data[month_key][task_type] += workdays
            except:
                continue
        
        # 准备数据
        months = sorted(month_task_data.keys())
        task_types = sorted(set(
            task for tasks in month_task_data.values() for task in tasks.keys()
        ))
        
        # 构建矩阵
        matrix = []
        for task_type in task_types:
            row = [month_task_data[month][task_type] for month in months]
            matrix.append(row)
        
        return matrix, task_types, months
    
    def get_statistics(self):
        """
        获取统计信息
        
        Returns:
            dict: 包含各种统计数据的字典
        """
        total_workdays = sum(
            self.parse_workdays(item.get('人天')) for item in self.raw_data['data']
        )
        total_tasks = len([
            item for item in self.raw_data['data'] 
            if self.parse_workdays(item.get('人天')) > 0
        ])
        avg_workdays = total_workdays / total_tasks if total_tasks > 0 else 0
        
        project_count = len(self.get_project_workdays())
        task_type_count = len(self.get_task_type_workdays())
        
        return {
            'total_items': self.raw_data['metadata']['total_items'],
            'total_tasks': total_tasks,
            'total_workdays': total_workdays,
            'avg_workdays': avg_workdays,
            'project_count': project_count,
            'task_type_count': task_type_count,
        }
    
    def get_dashboard_data(self):
        """
        获取仪表盘所需的所有数据
        
        Returns:
            dict: 包含所有图表数据
        """
        return {
            'project_workdays': self.get_project_workdays(),
            'monthly_workdays': self.get_monthly_workdays(),
            'task_type_workdays': self.get_task_type_workdays(),
            'statistics': self.get_statistics(),
        }


class TaskVisualization:
    """任务数据可视化业务类"""
    
    def __init__(self, data_file=None, output_dir=None):
        """
        初始化
        
        Args:
            data_file: 数据文件路径
            output_dir: 输出目录
        """
        self.processor = DataProcessor(data_file)
        self.visualizer = Visualizer(output_dir)
    
    def generate_project_chart(self):
        """生成项目人天统计图"""
        data = self.processor.get_project_workdays()
        return self.visualizer.bar_chart(
            data=data,
            title='各项目人天统计',
            xlabel='项目',
            ylabel='人天',
            filename='项目人天统计_柱状图.png'
        )
    
    def generate_monthly_trend_chart(self):
        """生成月度趋势图"""
        data = self.processor.get_monthly_workdays()
        return self.visualizer.line_chart(
            data=data,
            title='月度人天趋势',
            xlabel='月份',
            ylabel='人天',
            filename='月度人天趋势_折线图.png'
        )
    
    def generate_task_type_chart(self):
        """生成任务类型占比图"""
        data = self.processor.get_task_type_workdays()
        return self.visualizer.pie_chart(
            data=data,
            title='任务类型人天占比',
            filename='任务类型占比_饼图.png'
        )
    
    def generate_project_task_distribution(self):
        """生成项目任务分布堆积图"""
        data = self.processor.get_project_task_distribution()
        return self.visualizer.stacked_bar_chart(
            data=data,
            title='各项目任务类型分布',
            xlabel='项目',
            ylabel='人天',
            filename='项目任务分布_堆积柱状图.png'
        )
    
    def generate_top_tasks_chart(self, top_n=15):
        """生成任务排名图"""
        data = dict(self.processor.get_top_tasks(top_n))
        return self.visualizer.horizontal_bar_chart(
            data=data,
            title=f'Top {top_n} 任务人天排名',
            xlabel='人天',
            filename='任务人天排名_横向柱状图.png',
            top_n=top_n
        )
    
    def generate_heatmap(self):
        """生成月份×任务类型热力图"""
        matrix, row_labels, col_labels = self.processor.get_month_task_matrix()
        return self.visualizer.heatmap(
            data=matrix,
            row_labels=row_labels,
            col_labels=col_labels,
            title='月份×任务类型 人天热力图',
            filename='月份任务类型_热力图.png'
        )
    
    def generate_dashboard(self):
        """生成综合仪表盘"""
        dashboard_data = self.processor.get_dashboard_data()
        stats = dashboard_data['statistics']
        
        # 准备统计文本
        stats_text = f"""
    数据统计概览
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    总任务数: {stats['total_items']} 个
    有效任务数: {stats['total_tasks']} 个
    总人天: {stats['total_workdays']:.1f} 天
    平均每任务人天: {stats['avg_workdays']:.2f} 天
    项目数: {stats['project_count']} 个
    任务类型数: {stats['task_type_count']} 种
    """
        
        # 配置图表
        charts_config = [
            # 项目人天柱状图 (第1行,占两列)
            (331, 'bar', dashboard_data['project_workdays'], 
             {'title': '各项目人天统计', 'color': '#3498DB'}),
            
            # 任务类型饼图 (第2行左)
            (332, 'pie', dashboard_data['task_type_workdays'],
             {'title': '任务类型占比'}),
            
            # 月度趋势折线图 (第2行右)
            (333, 'line', dashboard_data['monthly_workdays'],
             {'title': '月度人天趋势', 'color': '#E74C3C'}),
            
            # 统计信息文本 (第3行,占两列)
            (313, 'text', stats_text, {'fontsize': 11}),
        ]
        
        return self.visualizer.multi_chart_dashboard(
            charts_config=charts_config,
            title='云效任务统计综合仪表盘',
            filename='综合统计仪表盘.png'
        )
    
    def generate_basic_charts(self):
        """生成基础图表(柱状图、折线图、饼图)"""
        print("=" * 60)
        print("开始生成基础图表...")
        print("=" * 60)
        print()
        
        self.generate_project_chart()
        self.generate_monthly_trend_chart()
        self.generate_task_type_chart()
        
        print()
        print("=" * 60)
        print("✓ 基础图表生成完成!")
        print("=" * 60)
    
    def generate_advanced_charts(self):
        """生成高级图表(堆积图、热力图等)"""
        print("=" * 60)
        print("开始生成高级图表...")
        print("=" * 60)
        print()
        
        self.generate_project_task_distribution()
        self.generate_top_tasks_chart(15)
        self.generate_heatmap()
        self.generate_dashboard()
        
        print()
        print("=" * 60)
        print("✓ 高级图表生成完成!")
        print("=" * 60)
    
    def generate_all_charts(self):
        """生成所有图表"""
        print("=" * 60)
        print("云效任务数据可视化")
        print("=" * 60)
        print()
        
        self.generate_basic_charts()
        print()
        self.generate_advanced_charts()
        
        print()
        print("=" * 60)
        print("✓ 所有图表生成完成!")
        print(f"✓ 输出目录: {self.visualizer.output_dir}")
        print("=" * 60)


def main():
    """主程序"""
    task_viz = TaskVisualization(output_dir='output_云效')
    
    while True:
        print("\n请选择操作:")
        print("1. 生成基础图表")
        print("2. 生成高级图表")
        print("3. 生成所有图表")
        print("4. 生成单个图表")
        print("0. 退出")
        print()
        
        choice = input("请输入选项 (0-4): ").strip()
        print()
        
        if choice == '1':
            task_viz.generate_basic_charts()
        elif choice == '2':
            task_viz.generate_advanced_charts()
        elif choice == '3':
            task_viz.generate_all_charts()
        elif choice == '4':
            print("单个图表选项:")
            print("1. 项目人天统计")
            print("2. 月度趋势")
            print("3. 任务类型占比")
            print("4. 项目任务分布")
            print("5. Top任务排名")
            print("6. 热力图")
            print("7. 综合仪表盘")
            
            sub_choice = input("请选择 (1-7): ").strip()
            
            if sub_choice == '1':
                task_viz.generate_project_chart()
            elif sub_choice == '2':
                task_viz.generate_monthly_trend_chart()
            elif sub_choice == '3':
                task_viz.generate_task_type_chart()
            elif sub_choice == '4':
                task_viz.generate_project_task_distribution()
            elif sub_choice == '5':
                task_viz.generate_top_tasks_chart()
            elif sub_choice == '6':
                task_viz.generate_heatmap()
            elif sub_choice == '7':
                task_viz.generate_dashboard()
            else:
                print("⚠️ 无效选项")
        elif choice == '0':
            print("已退出程序")
            break
        else:
            print("⚠️ 无效选项,请重新输入")


if __name__ == '__main__':
    main()
