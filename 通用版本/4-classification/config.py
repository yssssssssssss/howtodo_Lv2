# input变量
z = '男鞋_from_0501'
root_folder = f'D://code//data//Lv2期结论//{z}'
base_path = f'D://code//data//Lv2期结论//{z}'
csv_file_path = f'D://code//data//Lv2期结论//{z}//{z}.csv'
brand_path = f'D://code//data//Lv2期结论//{z}//男鞋品牌分层.xlsx'  # 品牌分类数据源
filter_layer_cases = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]  # 定义不同的筛选条件列表


# output变量
excel_output_path_2 = os.path.join(base_path, 'img_chart.xlsx')
excel_output_path_3 = os.path.join(base_path, f'{z}_{filter_layers}_img_chart.xlsx')
output_chart_path_3 = os.path.join(base_path, f'{z}_{filter_layers}_img_chart.png')
merged_df.to_excel(f'D://code//data//Lv2期结论//{x}//sku分类数据表.xlsx', index=False)


# # py1中出现的变量
# root_folder = "D://code//data//Lv2期结论//男鞋_from_0501"


# # py2中出现的变量
# z = '男鞋_from_0501'
# base_path = f'D://code//data//Lv2期结论//{z}'
# csv_file_path = f'D://code//data//Lv2期结论//{z}//{z}.csv'
# excel_output_path = os.path.join(base_path, 'image_distribution_stats.xlsx')


# # py3中出现的变量
# # z = '女士春夏下装_from_0501'
# base_path = f'D://code//data//Lv2期结论//{z}'
# csv_file_path = f'D://code//data//Lv2期结论//{z}//{z}.csv'
# brand_path = f'D://code//data//Lv2期结论//{z}//男鞋品牌分层.xlsx'  # 品牌分类数据源
# filter_layer_cases = [[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]]  # 定义不同的筛选条件列表
# excel_output_path = os.path.join(base_path, f'{filter_layers}_image_distribution_stats.xlsx')


# # py4中出现的变量
# x = '京喜_from_0501'
# root_folder = f'D://code//data//Lv2期结论//{x}//筛选'  # 一级文件夹路径
# df2 = pd.read_csv('D://code//data//Lv2期结论//京喜_from_0501//京喜数据_from_0501_筛选.csv')
# merged_df.to_excel(f'D://code//data//Lv2期结论//{x}//sku分类数据表.xlsx', index=False)


