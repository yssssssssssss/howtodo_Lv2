# 没有考虑brand
# 这里的热力图不是基于25宫格分类,而是基于商品数量
# 还是保留了5x5网格分类,生成了线框图和分类图片
# 将结果统计为了一个新的excel表,包含'x', 'y', 'box_no', 'x1', 'y1', 'x2', 'y2'



import pandas as pd
import os
import shutil
from tqdm import tqdm
import concurrent.futures
import itertools
import datetime
from matplotlib.patches import Rectangle
import matplotlib.pyplot as plt

# 全局参数
x_list = ['9736', '9735', '12004']
y_list = ['txt', 'price']
path = 'Lv2期结论'
z = '男士春夏下装_from_0501'

# 用于收集每个 x 和 y 分类的结果
all_results = []

# 1. 归一化坐标
def normalize_coordinates(row):
    width, height = 800, 800
    row['left_norm'] = max(0, min(row['img_x1'] / width, 1))
    row['top_norm'] = max(0, min(row['img_y1'] / height, 1))
    row['right_norm'] = max(0, min(row['img_x2'] / width, 1))
    row['bottom_norm'] = max(0, min(row['img_y2'] / height, 1))
    return row

# 2. 判断重叠和分类
def check_overlap(rect, grid_cell):
    return not (rect[2] < grid_cell[0] or rect[0] > grid_cell[2] or
                rect[3] < grid_cell[1] or rect[1] > grid_cell[3])

def classify_image(group):
    overlaps = [0] * 25
    for _, row in group.iterrows():
        rect = (row['left_norm'], row['top_norm'], row['right_norm'], row['bottom_norm'])
        for i in range(5):
            for j in range(5):
                grid_cell = (i / 5, j / 5, (i + 1) / 5, (j + 1) / 5)
                if check_overlap(rect, grid_cell):
                    overlaps[i * 5 + j] = 1
    return ''.join(map(str, overlaps))

# 3. 绘制线框图
def draw_rectangles(group, save_path):
    fig, ax = plt.subplots(figsize=(6.16, 6.16), dpi=100)

    # 绘制矩形框
    for _, row in group.iterrows():
        rect = Rectangle((row['left_norm'], 1 - row['bottom_norm']),
                         row['right_norm'] - row['left_norm'],
                         row['bottom_norm'] - row['top_norm'],
                         fill=False, edgecolor='r')
        ax.add_patch(rect)

    # 绘制5x5网格
    for i in range(5):
        for j in range(5):
            grid_rect = Rectangle((j / 5, 1 - (i + 1) / 5), 1 / 5, 1 / 5, fill=False, edgecolor='b')
            ax.add_patch(grid_rect)

    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')

    # 保存线框图
    fig.savefig(save_path, bbox_inches='tight', pad_inches=0)
    plt.close(fig)

# 4. 处理单个图像并分类
def process_image(name, group, x, y):
    # 检查源图片是否存在，避免处理不存在的文件
    source = os.path.join(f'D://code//data//{path}//{z}//{x}//grounding_output//{y}', name)
    if not os.path.exists(source):
        # print(f"File not found: {source}")
        return None

    # 分类图像
    classification = classify_image(group)
    
    # 处理这个图片的所有框
    results = []
    for _, row in group.iterrows():
        results.append((
            x,                  # x
            y,                  # y
            row['box_no'],      # box_no
            row['x1'],          # x1
            row['y1'],          # y1
            row['x2'],          # x2
            row['y2'],          # y2
            name,               # Image Name
            classification,     # Classification
            row['uv'],         # uv
            row['click_uv']    # click_uv
        ))

    # 复制图片到分类文件夹
    destination_dir = os.path.join(f'D://code//data//{path}//{z}//{x}//grounding_output//{y}//50%_img_classified_images', classification)
    os.makedirs(destination_dir, exist_ok=True)
    destination = os.path.join(destination_dir, name)
    shutil.copy(source, destination)

    # 绘制并保存线框图
    visualization_dir = f'D://code//data//{path}//{z}//{x}//grounding_output//{y}//50%_img_visualizations'
    os.makedirs(visualization_dir, exist_ok=True)
    draw_rectangles(group, os.path.join(visualization_dir, f"{name}_visualization.png"))

    return results

# 主处理函数
def main(x, y):
    print(f"Processing for x: {x}, y: {y}")
    df = pd.read_excel(f'D://code//data//{path}//{z}//merged_info_ctr-1.xlsx')
    
    # 添加验证代码
    required_columns = ['box_no', 'uv', 'click_uv']
    for col in required_columns:
        if col not in df.columns:
            raise ValueError(f"'{col}' 列在Excel文件中不存在")
    
    df['Image Name'] = df['Image Name'].astype(str) + '.jpg'

    # 计算 x2 和 y2
    df['x1'] = df['img_x1']
    df['y1'] = df['img_y1']
    df['x2'] = df['img_x2']
    df['y2'] = df['img_y2']

    # 删除重复 'ctr' 列
    if 'ctr' in df.columns and df.columns.duplicated().any():
        df = df.loc[:, ~df.columns.duplicated()]

    # 按 'ctr' 列排序并取前50%
    df = df.sort_values(by='ctr', ascending=False)
    rows_to_keep = int(len(df) * 0.5)
    df = df.head(rows_to_keep)
    df = df.apply(normalize_coordinates, axis=1)

    # 添加这行：按 'Image Name' 分组
    grouped = df.groupby('Image Name')

    # 按 'Image Name' 分组并处理
    # 修改结果收集方式
    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(process_image, name, group, x, y) for name, group in grouped]

        for future in tqdm(concurrent.futures.as_completed(futures), total=len(futures)):
            results = future.result()
            if results is not None:
                for result in results:
                    all_results.append(result)

# 处理所有 x 和 y 组合
for x, y in itertools.product(x_list, y_list):
    main(x, y)

# 保存总表
output_df = pd.DataFrame(all_results, columns=[
    'x', 'y', 'box_no', 'x1', 'y1', 'x2', 'y2', 
    'Image Name', 'Classification', 'uv', 'click_uv'
])
output_file = f'D://code//data//{path}//{z}//all_classification_results.xlsx'
output_df.to_excel(output_file, index=False)

# 打印当前时间
current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
print(f"All processing completed at: {formatted_time}")


