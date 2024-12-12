import os
import pandas as pd

# 存储图片信息的列表
image_info = []



x = '京喜_from_0501'



# 一级文件夹路径
root_folder = f'D://code//data//Lv2期结论//{x}//筛选'

# 遍历一级文件夹下的所有二级文件夹
for sub_folder in os.listdir(root_folder):
    if sub_folder.isdigit():  # 只处理数字命名的二级文件夹
        grounding_folder = os.path.join(root_folder, sub_folder, 'grounding_output')
        if os.path.exists(grounding_folder):
            for sub_sub_folder in ['price', 'txt', 'white', 'scene']:
                sub_sub_folder_path = os.path.join(grounding_folder, sub_sub_folder)
                if os.path.exists(sub_sub_folder_path):
                    for image_file in os.listdir(sub_sub_folder_path):
                        if "txt_" in image_file:
                            image_file = image_file.replace("txt_", "")
                        elif "price_" in image_file:
                            image_file = image_file.replace("price_", "")
                        image_info.append([image_file, sub_sub_folder, sub_folder])

# 创建DataFrame并保存为Excel
df = pd.DataFrame(image_info, columns=['图片名', '分类', 'cid3'])
# df.to_excel('D://code//data//Lv2期结论//京喜_from_0501//筛选//分类数据image_info.xlsx', index=False)

# 读取Excel文件
# data = pd.read_csv('D://code//data//Lv2期结论//京喜_from_0501//京喜数据_from_0501_筛选.csv')
df2 = pd.read_csv('D://code//data//Lv2期结论//京喜_from_0501//京喜数据_from_0501_筛选.csv')

# 按照img_url列进行聚合，并对指定列进行求和
aggregated_data = df2.groupby('img_url').agg({
    'uv':'sum',
    'click_uv':'sum',
    'gmv_cj':'sum',
    'sale_qtty_cj':'sum'
}).reset_index()

# 将原始数据中与聚合相关的列合并到聚合后的数据中
aggregated_data = pd.merge(aggregated_data, df2[['sku', 'img_url','img_type', 'bu_id', 'cid1', 'cid2', 'cid3', 'main_brand_code','shop_id']], on='img_url', how='left')

# 保存为新的Excel文件
# aggregated_data.to_excel('D://code//data//Lv2期结论//京喜_from_0501//url加总原始数据.xlsx', index=False)
# csv_file_path = 'D://code//data//Lv2期结论//京喜_from_0501//url加总原始数据.xlsx'
# df = pd.read_excel(csv_file_path)

def extract_matching_part(img_url):
    if pd.isna(img_url):
        return None
    img_url = img_url.split('?')[0]
    img_url = os.path.splitext(img_url)[0]
    parts = img_url.split('/')
    if len(parts) >= 2:
        return f"{parts[-2]}_{parts[-1]}"
    return None

aggregated_data['matching_part'] = aggregated_data['img_url'].apply(extract_matching_part)

# df_x = pd.read_excel('D://code//data//Lv2期结论//京喜_from_0501//筛选//分类数据image_info.xlsx')

# 确保列数据类型匹配（如果需要）
aggregated_data['matching_part'] = aggregated_data['matching_part'].astype(str)
df['图片名'] = df['图片名'].apply(lambda x: str(x).replace('.jpg', '') if isinstance(x, (str, bytes)) else x)

# 根据条件进行拼接
merged_df = pd.merge(aggregated_data, df, left_on='matching_part', right_on='图片名', how='right')
merged_df.to_excel(f'D://code//data//Lv2期结论//{x}//sku分类数据表.xlsx', index=False)


