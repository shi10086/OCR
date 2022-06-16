import os

import cv2 as cv
import pytesseract

from pdf2img import pdf2img, find_value, identify_pic

FOLDER = "./invoices"
KEYWORD_LIST = ["Rechnungsnr",
                "Rechnungsnummer",
                "Number",
                "Re-Nr",
                "number",
                "Belegnr.",
                "Rechnungs-Nr.",
                "Rechnungsnr.",
                "nummer",
                "Beleg"
                ]
pytesseract.pytesseract.tesseract_cmd = r'C:\\Users\\I559057\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract'


def getFlist(path):
    for root, dirs, files in os.walk(path):
        print('root_dir:', root)  # 当前路径
        print('sub_dirs:', dirs)  # 子文件夹
        print('files:', files)  # 文件名称，返回list类型
    return files


FILELIST = getFlist(FOLDER)

for filename in FILELIST:
    print(filename)
    pic_list = pdf2img("./invoices/" + filename)
    for pic_name in pic_list:
        img = cv.imread(pic_name)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # 转化为灰度图
        ret, binary = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)
        # BGR = cv2.cvtColor(module,cv2.COLOR_BGR2RGB)# 转化为RGB格式
        # ret,thresh = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY)
        # cv.imwrite(pic_name.split('.')[0]+'2.png', binary) # 保
        data = identify_pic(binary)
        cv.namedWindow('img', cv.WINDOW_NORMAL)
        cv.imshow("img", binary)
        cv.waitKey(0)
        # print(data)
        # data = drawBox(binary)
        # keyword = "Kundennummer"
        # keyword = "Rechnungsnummer"
        for keyword in KEYWORD_LIST:
            tg = data.get(keyword)
            # cv.rectangle(img, (data['135011'][0][0], data['135011'][0][1]),
            #              (data['135011'][0][0] + data['135011'][0][2], data['135011'][0][1] + data['135011'][0][3]), (255, 0, 0), 1)
            # cv.rectangle(img, (data['Fichtner'][0][0], data['Fichtner'][0][1]), (data['Fichtner'][0][0] + data[
            # 'Fichtner'][0][2], data['Fichtner'][0][1] + data['Fichtner'][0][3]), (255, 0, 0), 1)

            # point_size = 1
            # point_color = (0, 0, 255)  # BGR
            # thickness = 4  # 0 、4、8
            # cv.circle(img, (799, 1137), point_size, point_color, thickness)

            if tg is not None:
                print(keyword)
                tmp_res = []
                for pos in tg:
                    res = find_value(target=pos, pos_lis=data)
                    new_keyword = res["below"]
                    print(new_keyword)
                    if len(new_keyword) < 7:
                        continue
                    tmp_res.append(new_keyword)
                    tmp_idx = 0
                    while new_keyword != "":
                        new_pos = data.get(new_keyword)
                        # if new_keyword ==
                        res = find_value(target=new_pos[tmp_idx], pos_lis=data)
                        print(res)
                        new_keyword = res["below"]
                        if len(new_keyword) < 7:
                            break
                        tmp_res.append(new_keyword)
                print(tmp_res)
