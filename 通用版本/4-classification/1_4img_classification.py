import os
import shutil
from PIL import Image
from paddleocr import PaddleOCR
from tqdm import tqdm
from datetime import datetime
import math
import time
import numpy as np
import pandas as pd


%config IPCompleter.greedy=True


def process_folder(root_folder):
    # 初始化 PaddleOCR
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", show_log=False)

    # 遍历根文件夹下的所有子文件夹
    for dirpath, dirnames, filenames in os.walk(root_folder):
        if os.path.basename(dirpath) == 'grounding_output':
            price_folder = os.path.join(dirpath, 'price')
            txt_folder = os.path.join(dirpath, 'txt')
            scene_folder = os.path.join(dirpath, 'scene')
            white_folder = os.path.join(dirpath, 'white')

            # 如果文件夹不存在，则创建
            for folder in [price_folder, txt_folder, scene_folder, white_folder]:
                if not os.path.exists(folder):
                    os.makedirs(folder)

            '''
            step1 - 筛选价促卖点图
            '''
            print('Step 1: 筛选价促卖点图')

            image_files = [os.path.join(dirpath, filename) for filename in os.listdir(dirpath) if filename.endswith(('.jpg', '.png'))]

            # 使用 tqdm 创建进度条
            with tqdm(total=len(image_files), desc="Processing images") as pbar:
                # 遍历源文件夹中的所有图片文件
                for filename in image_files:
                    img_path = os.path.join(dirpath, filename)

                    # 使用 PaddleOCR 进行文字识别
                    result = ocr.ocr(img_path, cls=True)

                    if not result:
                        # 如果识别结果为空,则跳过这张图片,不进行移动操作
                        pbar.write(f"Image '{filename}' skipped due to empty OCR result.")
                        pbar.update(1)
                        continue

                    data_list = result[0]

                    # 检查识别结果是否有关键词
                    contains_keyword = False

                    if data_list:
                        # 定义关键词列表
                        keywords = ['满', '减', '折', '到手价', '送', '免息', '活动价', '包邮价', '参考价',
                                    r'.*满.*减.*', r'.*满.*-.*', r'.*满.*赠.*', r'.*满.*送.*', r'.*价.*',
                                    '券', '优惠', '用券', '领券', '券', '送', '低至', '立减', '直降', '免息',
                                    '¥', '夫', '￥']

                        # 遍历识别结果中的文本
                        for data in data_list:
                            text = data[1][0]  # 获取文本内容
                            # 检查当前文本是否包含关键词
                            if any(keyword in text for keyword in keywords):
                                contains_keyword = True
                                break

                    # 根据检查结果移动文件
                    if contains_keyword:
                        try:
                            shutil.move(img_path, price_folder)
                            # pbar.write(f"Image '{filename}' moved to price_folder.")
                        except Exception as e:
                            pbar.write(f"Failed to move image '{filename}': {e}")
                            continue
                    # else:
                    #     # 如果不包含关键词，移动到其他文件夹
                    #     # 你可以根据需要修改这里的逻辑
                    #     try:
                    #         shutil.move(img_path, txt_folder)
                    #         pbar.write(f"Image '{filename}' moved to scene_folder.")
                    #     except Exception as e:
                    #         pbar.write(f"Failed to move image '{filename}': {e}")

                    # 重置 contains_keyword 变量
                    contains_keyword = False

                    # 更新进度条
                    pbar.update(1)

            print("卖点图 classification completed.")

            # 获取当前时间
            current_time = datetime.now()

            # 格式化输出当前时间
            print("完成时间:", current_time)

            '''
            step2 - 筛选白底图
            '''

            print('Step 2: 筛选白底图')

            def move_images_with_white_pixels(base_path, white_folder, threshold=0.40):
                # 获取源文件夹中的图片文件列表
                image_files = [filename for filename in os.listdir(base_path) if filename.endswith(('.jpg', '.png'))]

                # 使用 tqdm 创建进度条
                with tqdm(total=len(image_files), desc=f"Moving images from {base_path}") as pbar:
                    # 遍历源文件夹中的所有图片文件
                    for filename in image_files:
                        img_path = os.path.join(base_path, filename)

                        # 打开图片并获取像素信息
                        with Image.open(img_path) as img:
                            # 确认图片是 RGB 模式
                            if img.mode!= 'RGB':
                                img = img.convert('RGB')
                            # 获取图片的宽度和高度
                            width, height = img.size

                            # 统计白色像素点的数量
                            white_pixels = 0
                            for x in range(width):
                                for y in range(height):
                                    # 获取像素点的 RGB 值
                                    pixel_value = img.getpixel((x, y))
                                    # 如果是 RGB 图像，解包为三个值，否则为四个值
                                    if len(pixel_value) == 3:
                                        r, g, b = pixel_value
                                    else:  # 处理带有透明度的图像
                                        r, g, b, a = pixel_value
                                    # 如果 RGB 值都大于 230，则认为是白色像素点
                                    if r > 230 and g > 230 and b > 230:
                                        white_pixels += 1

                            # 计算白色像素点占比
                            white_ratio = white_pixels / (width * height)

                            # 如果白色像素点占比超过阈值，则将图片移动到目标文件夹
                            if white_ratio > threshold:
                                target_path = os.path.join(white_folder, filename)
                                try:
                                    shutil.move(img_path, white_folder)
                                    # pbar.write(f"Image '{filename}' moved to white folder.")
                                except Exception as e:
                                    pbar.write(f"Error moving image '{filename}': {e}")
                                    continue

                        # 更新进度条
                        pbar.update(1)

            # 调用函数，将白色像素点占比超过 30%的图片从源文件夹列表中移动到目标文件夹
            move_images_with_white_pixels(dirpath, white_folder, threshold=0.40)

            # 获取当前时间
            current_time = datetime.now()

            # 格式化输出当前时间
            print("完成时间:", current_time)

            '''
            step3 - 筛选功能卖点图
            '''

            print('Step 3: 筛选功能卖点图')

            image_files = [filename for filename in os.listdir(dirpath) if filename.endswith(('.jpg', '.png'))]
            for filename in image_files:

                img_path = os.path.join(dirpath, filename)
                # print(f"Processing image: {img_path}")

                img = Image.open(img_path)
                width, height = img.size

                # 读取图片下部分 5/6
                cropped_img = img.crop((0, height // 6, width, height))

                # 将 PIL 图像对象转换为 numpy 数组
                img_np = np.array(cropped_img)

                # OCR 处理
                result = ocr.ocr(img_np, cls=True)

                if result is None:
                    continue

                rectangles_with_text = result[0]

                if rectangles_with_text is None:
                    continue

                line_count = len(rectangles_with_text)

                # 如果文本行数大于等于 3, 将图片移动到目标文件夹
                if line_count >= 2:
                    target_path = os.path.join(txt_folder, filename)
                    shutil.move(img_path, txt_folder)
                    # print(f"'{filename}' moved to txt folder.")

                else:
                    # print(f"'{filename}' remains in source folder.")
                    continue

            '''
            step4 - 将剩余图片归类到 scene
            '''

            print('Step 4: 归类图片到 scene')

            # 检查目标文件夹是否存在，如果不存在则创建
            if not os.path.exists(scene_folder):
                os.makedirs(scene_folder)

            # 获取源文件夹中的所有图片文件列表
            image_files = [filename for filename in os.listdir(dirpath) if filename.endswith(('.jpg', '.png'))]

            # 移动图片到 txt_folder
            for filename in image_files:
                img_path = os.path.join(dirpath, filename)
                target_path = os.path.join(scene_folder, filename)
                shutil.move(img_path, scene_folder)
                # print(f"Image '{filename}' moved to scene_folder.")

            print("Image moving completed.")

            # 获取当前时间
            current_time = datetime.now()

            # 格式化输出当前时间
            print("完成时间:", current_time)

            '''
            step5 - 将 white 中有文本的图片移到 txt_folder
            '''

            # 获取源文件夹中的所有图片文件列表
            image_files = [filename for filename in os.listdir(white_folder) if filename.endswith(('.jpg', '.png'))]

            # 使用 tqdm 创建进度条
            with tqdm(total=len(image_files), desc="Processing images") as pbar:

                # 遍历源文件夹中的所有图片文件
                for filename in image_files:
                    img_path = os.path.join(white_folder, filename)

                    img = Image.open(img_path)
                    width, height = img.size

                    # 读取图片下部分 3/4
                    cropped_img = img.crop((0, height // 6, width, height))

                    # 将 PIL 图像对象转换为 numpy 数组
                    img_np = np.array(cropped_img)

                    # OCR 处理
                    result = ocr.ocr(img_np, cls=True)

                    if result is None:
                        continue

                    rectangles_with_text = result[0]

                    if rectangles_with_text is None:
                        continue

                    # 统计文本框高度大于 30 像素的行数
                    lines_above_30_count = 0
                    for rectangle in rectangles_with_text:
                        # 计算文本框的高度和宽度
                        points = rectangle[0]
                        x_A, y_A = points[0]

                        # 计算 A 点到 BCD 的距离
                        distances = []
                        for point in points[1:]:
                            x_B, y_B = point
                            distance = math.sqrt((x_B - x_A) ** 2 + (y_B - y_A) ** 2)
                            distances.append(distance)

                        # 获取最短的距离作为文本框的大小
                        text_size = min(distances)

                        # 统计高度大于 x 像素的行数
                        if text_size > 30:
                            lines_above_30_count += 1

                    # 如果大于 30 像素的行数大于等于 2，将图片移动到目标文件夹
                    if lines_above_30_count >= 2:
                        # 如果识别结果不为空且行数小于等于 3，则将图片复制到 txt_folder
                        target_path = os.path.join(txt_folder, filename)
                        shutil.move(img_path, target_path)
                        # pbar.write(f"Image '{filename}' copied to txt_folder.")
                    else:
                        # pbar.write(f"Image '{filename}' remains in source folder.")
                        continue

                    # 更新进度条
                    pbar.update(1)

            print("Image classification completed.")

            print('okkk')

            # 获取当前时间
            current_time = datetime.now()

            # 打印当前时间
            print("当前系统时间是:", current_time)
            print("当前系统时间是:", current_time)
            print("当前系统时间是:", current_time)


# root_folder = "D://code//data//Lv2期结论//男鞋_from_0501"
process_folder(root_folder)


