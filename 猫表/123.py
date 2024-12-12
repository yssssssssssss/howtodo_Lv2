import pandas as pd
import os
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import datetime


import matplotlib.pyplot as plt
# 设置中文字体为微软雅黑（假设系统中已安装该字体）
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  
# 用来正常显示负号等特殊字符
plt.rcParams['axes.unicode_minus'] = False


# 读取数据表
file_path = f'D://code//data//{path}//{z}//classification_results.xlsx'
df = pd.read_excel(file_path)
df = df.dropna()  # 去除空值

# 设置保存图像的文件夹
output_folder = f'D://code//data//{path}//{z}//url_3'
os.makedirs(output_folder, exist_ok=True)

# 现代时尚的配色方案
modern_colors = [
    '#FF6B6B',  # 珊瑚红
    '#4ECDC4',  # 青绿
    '#45B7D1',  # 天蓝
    '#96CEB4',  # 薄荷绿
    '#FFEEAD',  # 淡黄
]

# 创建一个列表来存储表格数据
table_data = []

# 1. 饼图部分和数据收集
grouped_by_xy = df.groupby(['x', 'y'])

for (x, y), group in grouped_by_xy:
    # 计算每个box_no的统计信息
    box_stats = group.groupby('box_no').agg({
        'Image Name': 'count'  # 使用Image Name列来计数
    }).reset_index()
    
    box_stats = box_stats.rename(columns={'Image Name': 'count'})  # 重命名列
    total_count = box_stats['count'].sum()
    box_stats['count_pct'] = box_stats['count'] / total_count
    
    # 添加到表格数据
    for _, row in box_stats.iterrows():
        table_data.append({
            'x': x,
            'y': y,
            'box_no': row['box_no'],
            'count': row['count'],
            'count_pct': row['count_pct']
        })
    
    # 绘制饼图
    box_no_counts = group['box_no'].value_counts()
    labels = [f'No:{idx}\nCount: {box_no_counts[idx]}' 
            for idx in box_no_counts.index]

    plt.figure(figsize=(8, 8))
    plt.pie(box_no_counts, 
            labels=labels, 
            autopct='%1.1f%%', 
            startangle=140, 
            colors=modern_colors,
            shadow=False,
            textprops={'fontsize': 12})
    plt.title(f'{x}_{y} Box Distribution', pad=20, fontsize=14)
    
    pie_path = os.path.join(output_folder, f'{z}_{y}_box_distribution.png')
    plt.savefig(pie_path, bbox_inches='tight', dpi=100)
    print(f"饼图已生成并保存: {pie_path}")
    plt.close()

# 创建并保存表格
table_df = pd.DataFrame(table_data)
table_df = table_df[['x', 'y', 'box_no', 'count', 'count_pct']]  # 确保列的顺序
table_df.sort_values(['x', 'y', 'box_no'], inplace=True)  # 排序
table_output_path = os.path.join(output_folder, f'{z}_box_distribution_stats.xlsx')
table_df.to_excel(table_output_path, index=False)
print(f"Excel表格已保存: {table_output_path}")

# 2. 热力图部分
grouped_by_xyz = df.groupby(['x', 'y', 'box_no'])

for (x, y, box_no), group in grouped_by_xyz:
    # 获取当前组内所有图片的最大宽度和高度
    max_width = int(group['Image_Width'].max())
    max_height = int(group['Image_Height'].max())
    
    # 创建与图片实际大小相匹配的热力图数据矩阵
    heatmap_data = np.zeros((max_height, max_width))

    for _, row in group.iterrows():
        # 直接使用原始坐标，不需要缩放
        x1 = int(row['x1'])
        y1 = int(row['y1'])
        x2 = int(row['x3'])
        y2 = int(row['y3'])
        
        # 确保坐标在有效范围内
        x1 = max(0, min(x1, max_width - 1))
        x2 = max(0, min(x2, max_width - 1))
        y1 = max(0, min(y1, max_height - 1))
        y2 = max(0, min(y2, max_height - 1))
        
        # 在对应区域增加热度值
        heatmap_data[y1:y2, x1:x2] += 1

    # 根据图片尺寸计算合适的显示尺寸
    display_scale = 8  # 控制显示大小的缩放因子
    figsize_width = max_width / 100 * display_scale
    figsize_height = max_height / 100 * display_scale
    
    # 设置合理的最大显示尺寸
    max_display_size = 20
    if figsize_width > max_display_size or figsize_height > max_display_size:
        scale = max_display_size / max(figsize_width, figsize_height)
        figsize_width *= scale
        figsize_height *= scale

    plt.figure(figsize=(figsize_width, figsize_height))
    
    # 创建标尺刻度
    x_ticks = np.linspace(0, max_width, 10, dtype=int)  # X轴10个刻度
    y_ticks = np.linspace(0, max_height, 10, dtype=int)  # Y轴10个刻度
    
    # 绘制热力图并添加标尺
    sns.heatmap(heatmap_data, 
                cmap='PuBu',
                cbar=True,  # 显示颜色条
                xticklabels=x_ticks,  # 显示X轴刻度
                yticklabels=y_ticks,  # 显示Y轴刻度
                annot=False)  # 不显示具体数值
    
    # 设置标尺标签
    plt.xlabel('Width (pixels)')
    plt.ylabel('Height (pixels)')
    
    # 调整标尺显示
    plt.xticks(np.linspace(0, max_width, 10), x_ticks, rotation=45)
    plt.yticks(np.linspace(0, max_height, 10), y_ticks, rotation=0)
    
    # 添加网格线
    plt.grid(True, linestyle='--', alpha=0.3)
    
    heatmap_path = os.path.join(output_folder, f'{z}_{y}_box_{box_no}_heatmap.png')
    plt.title(f'{z}_{y}_{box_no} Heatmap\nSize: {max_width}x{max_height}', pad=20, fontsize=14)
    
    # 调整布局以确保标尺完全显示
    plt.tight_layout()
    
    plt.savefig(heatmap_path, bbox_inches='tight', dpi=100, pad_inches=0.1)
    print(f"热力图已生成并保存: {heatmap_path}")
    plt.close()

print("所有图表和统计表格已生成并保存。")

# 打印完成时间
current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
print(f"处理完成时间: {formatted_time}")


