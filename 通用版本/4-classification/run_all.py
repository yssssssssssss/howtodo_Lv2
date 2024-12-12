import importlib

# 定义模块的路径
modules = [
    "project.howtodo_Lv2.通用版本.4-classification.1_4img_classification",
    "project.howtodo_Lv2.通用版本.4-classification.2_4img_statistics",
    "project.howtodo_Lv2.通用版本.4-classification.3_4img_statistics_brand",
    "project.howtodo_Lv2.通用版本.4-classification.4_4img_sku&class&excel"
]

# 依次导入并执行每个模块的main函数
for module_name in modules:
    print(f"Executing {module_name}...")
    module = importlib.import_module(module_name)
    module.main()
