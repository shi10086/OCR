import fitz
import pytesseract
from pytesseract import Output
import cv2 as cv
import math
import pandas as pd
import os.path
from PIL import Image
from PIL import ImageDraw
import re


def pdf2img(filename):
    '''
    将pdf文件转化为图片
    :param filename PDF文件路径
    :return data: 生成的图片文件名列表
    '''
    try:
        doc = fitz.open(filename)
        page_count = doc.page_count
        pic_list = []
        for page_num in range(page_count):
            page = doc.load_page(page_num)  # 获取第0页
            rotate = int(0)
            # 每个尺寸的缩放系数为8，这将为我们生成分辨率提高64倍的图像。一般设为2
            zoom_x = 2.0
            zoom_y = 2.0
            trans = fitz.Matrix(zoom_x, zoom_y).prerotate(rotate)
            pix = page.get_pixmap(matrix=trans, alpha=False)
            pdf_file = os.path.basename(filename)
            # pic_name = pdf_file.split(".")[0] + "_page_" + str(page_num) + ".png"
            pic_name = "page_" + str(page_num) + ".png"
            pix.save(pic_name)
            pic_list.append(pic_name)
        return pic_list
    except:
        print("error")
        return []


def identify_pic(img, languae):
    data = {}
    d = pytesseract.image_to_data(img, output_type=Output.DICT, lang=languae)
    for i in range(len(d['text'])):
        if 0 < len(d['text'][i]):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            if data.get(d['text'][i].upper()):
                data[d['text'][i].upper()].append([d['left'][i], d['top'][i], d['width'][i], d['height'][i]])
            else:
                data[d['text'][i].upper()] = ([[d['left'][i], d['top'][i], d['width'][i], d['height'][i]]])
    return data


def calculate_center(point):
    return [point[0] + point[2] / 2, point[1] + point[3] / 2]


def find_value(target, pos_lis):
    # 关键字坐标
    target_x = target[0]
    target_y = target[1]
    width = target[2]
    height = target[3]
    # 寻找关键词右侧和下方的单词
    possible_res = {"right": ["", []], "below": ["", []]}
    # possible_res = {"right": "", "below": ""}
    min_below_dis = 9999
    min_right_dis = 9999
    tg_center = calculate_center(target)
    for key in pos_lis.keys():
        tmp_pos_lis = pos_lis[key]
        if not is_invoice(key):
            continue
        for pos in tmp_pos_lis:
            if pos[0] + pos[2] < target_x or pos[1] + pos[3] < target_y + 2 or (
                    pos[0] == target_x and pos[1] == target_y) or (
                    pos[0] >= target_x + width and pos[1] + pos[3] >= target_y):
                continue
            # tmp_dis = math.sqrt((pos[0] - target_x) ** 2 + (pos[1] - target_y) ** 2)
            # 计算距离以更新结果
            pos_center = calculate_center(pos)
            # tmp_dis = abs(pos[0] - target_x) + abs(pos[1] - target_y)
            tmp_dis = abs(tg_center[0] - pos_center[0]) + abs(tg_center[1] - pos_center[1])
            if pos[0] >= target_x + width:
                if tmp_dis < min_right_dis:
                    min_right_dis = tmp_dis
                    possible_res["right"][0] = key
                    possible_res["right"][1] = pos
            if pos[1] + pos[3] >= target_y:
                if tmp_dis < min_below_dis:
                    min_below_dis = tmp_dis
                    possible_res["below"][0] = key
                    possible_res["below"][1] = pos
    return possible_res


def find_amount(target, pos_lis):
    # 关键字坐标
    target_x = target[0]
    target_y = target[1]
    width = target[2]
    height = target[3]
    # 寻找关键词右侧和下方的单词
    # possible_res = {"right": "", "below": ""}
    possible_res = {"right": ["", []], "below": ["", []]}
    min_below_dis = 9999
    min_right_dis = 9999
    tg_center = calculate_center(target)
    for key in pos_lis.keys():
        tmp_pos_lis = pos_lis[key]
        if not is_amount(key):
            continue
        for pos in tmp_pos_lis:
            if pos[0] + pos[2] < target_x or pos[1] + pos[3] < target_y or (
                    pos[0] == target_x and pos[1] == target_y) or (
                    pos[0] >= target_x + width and pos[1] + pos[3] >= target_y):
                continue
            # tmp_dis = math.sqrt((pos[0] - target_x) ** 2 + (pos[1] - target_y) ** 2)
            # 计算距离以更新结果
            pos_center = calculate_center(pos)
            # tmp_dis = abs(pos[0] - target_x) + abs(pos[1] - target_y)
            tmp_dis = abs(tg_center[0] - pos_center[0]) + abs(tg_center[1] - pos_center[1])
            if pos[0] >= target_x + width:
                if tmp_dis < min_right_dis:
                    min_right_dis = tmp_dis
                    possible_res["right"][0] = key
                    possible_res["right"][1] = pos
            if pos[1] + pos[3] >= target_y:
                if tmp_dis < min_below_dis:
                    min_below_dis = tmp_dis
                    possible_res["below"][0] = key
                    possible_res["below"][1] = pos
    return possible_res


def drawBox(im):
    """
    识别字符并返回所识别的字符及它们的坐标
    :param im: 需要识别的图片
    :return data: 字符及它们在图片的位置
    """
    data = {}
    d = pytesseract.image_to_data(im, output_type=Output.DICT, lang="deu")
    for i in range(len(d['text'])):
        if 0 < len(d['text'][i]):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
            data[d['text'][i]] = ([d['left'][i], d['top'][i], d['width'][i], d['height'][i]])

            cv.rectangle(im, (x, y), (x + w, y + h), (255, 0, 0), 1)
            pilimg = Image.fromarray(im)
            draw = ImageDraw.Draw(pilimg)
    cv.namedWindow("recoText", cv.WINDOW_NORMAL)
    cv.imshow("recoText", im)
    cv.waitKey(0)
    return data


def is_invoice(s):
    """
    判断字符串是否为发票号
    :param s: string
    :return: bool
    """
    re_str1 = "^\d{7,}[.]?$"
    pattern1 = re.compile(re_str1)
    if re.match(pattern1, s):
        if re.match(pattern1, s).span()[1] == len(s):
            return True
    re_str2 = "^[a-zA-Z]+\d{5,}$"
    pattern2 = re.compile(re_str2)
    if re.match(pattern2, s):
        if re.match(pattern2, s).span()[1] == len(s):
            return True
    re_str3 = "^\d*[a-zA-Z]+\d{5,}$"
    pattern3 = re.compile(re_str3)
    if re.match(pattern3, s):
        if re.match(pattern3, s).span()[1] == len(s):
            return True

    return False


# def read_keywords(path):
#     df = pd.read_csv(path)
#     keywords = df["keyword"]
#     return list(keywords)


def is_amount(s):
    """
    判断金额字符串是否合法
    :param s: string
    :return: bool
    """
    re_str = "(-?\d*[.]?)?(-?\d*[,]?)*(\d*[.]?\d*)?"
    pattern = re.compile(re_str)
    if re.match(pattern, s).span()[1] == len(s):
        return True
    else:
        return False


if __name__ == '__main__':
    print(is_invoice('70395500375397.'))
    img = cv.imread("20201006.png")

    # print(read_keywords("rules.xlsx"))
    # filename = "Birgit Klaerner, reh 2808, FI FS IS-DE_2020_12_02_15_48_04.pdf"
    # # filename = "3892_001.pdf"
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Users\\I559057\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract'
    a = identify_pic(img,"pol")
    print(a)
    # pic_list = pdf2img(filename)
    # for pic_name in pic_list:
    #     img = cv.imread(pic_name)
    #     gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # 转化为灰度图
    #     ret, binary = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)
    #     # BGR = cv2.cvtColor(module,cv2.COLOR_BGR2RGB)# 转化为RGB格式
    #     # ret,thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
    #     # cv.imwrite(pic_name.split('.')[0]+'2.png', binary) # 保
    #     data = identify_pic(img)
    #     # print(data)
    #     # data = drawBox(binary)
    #     # keyword = "Kundennummer"
    #     # keyword = "Rechnungsnummer"
    #     keyword = "DZ22010979"
    #     tg = data.get(keyword)
    #     # cv.rectangle(img, (data['135011'][0][0], data['135011'][0][1]),
    #     #              (data['135011'][0][0] + data['135011'][0][2], data['135011'][0][1] + data['135011'][0][3]), (255, 0, 0), 1)
    #     # cv.rectangle(img, (data['Fichtner'][0][0], data['Fichtner'][0][1]), (data['Fichtner'][0][0] + data[
    #     # 'Fichtner'][0][2], data['Fichtner'][0][1] + data['Fichtner'][0][3]), (255, 0, 0), 1)
    #     print(tg)
    #     point_size = 1
    #     point_color = (0, 0, 255)  # BGR
    #     thickness = 4  # 0 、4、8
    #     # cv.circle(img, (data['Rechnungsnummer'][0][0], data['Rechnungsnummer'][0][1]), point_size, point_color, thickness)
    #     # cv.circle(img,(data['135011'][0][0], data['135011'][0][1]), point_size, point_color, thickness)
    #     # cv.circle(img, (data['Sofort'][0][0], data['Sofort'][0][1]), point_size, point_color, thickness)
    #     cv.circle(img, (1051, 1375), point_size, point_color, thickness)
    #     # cv.circle(img, (data['Gesamtforderung'][0][0], data['Gesamtforderung'][0][1]), point_size, point_color, thickness)
    #     cv.namedWindow('img', cv.WINDOW_NORMAL)
    #     cv.imshow("img", img)
    #     cv.waitKey(0)
    #
    #     print(tg)
    #     if tg is not None:
    #         for pos in tg:
    #             res = find_amount(target=pos, pos_lis=data)
    #             print(res)
    #             new_keyword = ""
    #             while new_keyword != "":
    #                 new_keyword = ""
