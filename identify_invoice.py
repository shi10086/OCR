import datetime
import os

import cv2 as cv
import pytesseract
from pytesseract.pytesseract import TesseractError

from pdf2img import pdf2img, find_value, identify_pic, find_amount
import configparser
import sys
import os
import xlwt
from PIL import ImageFont, ImageDraw, Image
import numpy as np

global FOLDER
global KEYWORD_LIST
global KEYWORD_AMOUNT


# FOLDER = "./invoices"
# KEYWORD_LIST = ["Rechnungsnr",
#                 "Rechnungsnummer",
#                 "Number",
#                 "Re-Nr",
#                 "number",
#                 "Belegnr.",
#                 "Rechnungs-Nr.",
#                 "Rechnungsnr.",
#                 "nummer",
#                 "Beleg",
#                 "Belegnummer"
#                 ]
# KEYWORD_AMOUNT = ["Betrag","betrag"]
# pytesseract.pytesseract.tesseract_cmd = r'C:\\Users\\I333224\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract'


def getTemplate(country):
    cwd = os.path.join(os.getcwd(), sys.argv[0])
    root_folder = (os.path.dirname(cwd))
    db_config = configparser.ConfigParser()
    db_config.read(os.path.join(root_folder, 'template.conf'), encoding='UTF-8')
    key_refrences = db_config.get(country, 'reference').strip().split('\n')
    print(key_refrences)
    global KEYWORD_LIST
    KEYWORD_LIST = key_refrences
    key_amount = db_config.get(country, 'amount').strip().split('\n')
    global KEYWORD_AMOUNT
    KEYWORD_AMOUNT = key_amount
    print(key_amount)


def getConfig():
    cwd = os.path.join(os.getcwd(), sys.argv[0])
    root_folder = (os.path.dirname(cwd))
    db_config = configparser.ConfigParser()
    db_config.read(os.path.join(root_folder, 'inital.conf'))
    tesseractCmd = db_config.get('config', 'tesseractCmd')
    folderPath = db_config.get('config', 'folderPath')
    pytesseract.pytesseract.tesseract_cmd = tesseractCmd
    global FOLDER
    FOLDER = folderPath


def getFlist(path):
    return os.listdir(path)


def match_invoice_amount(invoice_amount):
    """
    :param invoice_amount: 识别的所有发票号和金额
    :return: 匹配完成的发票号列与金额列
    """
    invoice_list = invoice_amount["invoice"]
    amount = invoice_amount["amount"]
    # print(invoice_amount)
    if len(amount) == 0:
        return {"invoice": [], "amount": []}
    matched_amount = []
    for inv in invoice_list:
        inv_y = inv[1][1]+inv[1][3]/2  # 计算发票中心点的纵坐标
        min_dis = 9999
        tmp_amo = amount[0]
        for amo in amount:
            if amo in matched_amount:
                continue
            amo_y = amo[1][1]+amo[1][3]/2  # 计算金额中心点的纵坐标
            if abs(amo_y - inv_y) < min_dis:
                min_dis = abs(amo_y - inv_y)
                tmp_amo = amo
        matched_amount.append(tmp_amo)
    invoice_amount["amount"] = matched_amount
    return invoice_amount


def write_excel(identified_res, save_path):
    """
    将识别结果以excel的形式存储
    :param identified_res: 识别结果
    :param save_path: 保存路径
    """
    try:
        book = xlwt.Workbook(style_compression=0)
        sheet = book.add_sheet('invoice & amount', cell_overwrite_ok=True)
        col = ('Reference', 'Gross invoice amount')
        inv = identified_res["invoice"]
        amo = identified_res["amount"]
        for i in range(len(col)):
            sheet.write(0, i, col[i])
        for row in range(len(inv)):
            sheet.write(row + 1, 0, inv[row][0])
            sheet.write(row + 1, 1, amo[row][0])
        book.save(save_path)
    except Exception as e:
        print(e)
        print("fail to save the result")
    # book = xlwt.Workbook(style_compression=0)
    # sheet = book.add_sheet('invoice & amount', cell_overwrite_ok=True)
    # col = ('Reference', 'Gross invoice amount')
    # inv = identified_res["invoice"]
    # amo = identified_res["amount"]
    # for i in range(len(col)):
    #     sheet.write(0, i, col[i])
    # for row in range(len(inv)):
    #     sheet.write(row + 1, 0, inv[row][0])
    #     sheet.write(row + 1, 1, amo[row][0])
    # book.save(save_path)


def drawBox(im, result, save_path):
    """
    在图片中将识别结果框出按顺序编号并保存
    :param im: 需要修改的图片
    :param result: 识别结果
    :param save_path: 图片保存路径
    """
    inv = result["invoice"]
    amo = result["amount"]
    for i in range(len(inv)):
        (x, y, w, h) = (inv[i][1][0], inv[i][1][1], inv[i][1][2], inv[i][1][3])
        cv.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv.putText(im, str(i), (x + w, y + h), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)
        (x, y, w, h) = (amo[i][1][0], amo[i][1][1], amo[i][1][2], amo[i][1][3])
        cv.rectangle(im, (x, y), (x + w, y + h), (0, 0, 255), 2)
        cv.putText(im, str(i), (x + w, y + h), cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 1)
    try:
        cv.imwrite(save_path, im)
    except Exception as e:
        print(e)
        print("fail to save the result")
    # cv.namedWindow("recoText", cv.WINDOW_NORMAL)
    # cv.imshow("recoText", im)
    # cv.waitKey(0)


def make_dir(res_folder):
    """
    创建保存当前日期下识别结果的文件夹
    :param res_folder: 在该目录下创建文件夹
    :return: 创建成功的路径
    """
    today = str(datetime.date.today())
    os.makedirs(res_folder + "\\" + today, exist_ok=True)
    return res_folder + "\\" + today


if __name__ == '__main__':
    COUNTRY_CODE = sys.argv[1].upper()
    INV_FOLDER = sys.argv[2]
    RES_FOLDER = sys.argv[3]
    LANGUAGE_COUNTRY = {'AT': ['deu', 'austria'],
                        'DE': ['deu', 'german'],
                        'FR': ['fra', 'france'],
                        'UK': ['eng', 'unitedkingdom'],
                        'PL': ['pol', 'poland'],
                        'CZ': ['ces', 'czech'],
                        'NL': ['nld', 'netherlands'],
                        'BE': ['nld', 'belgium'],
                        'SK': ['slk', 'slovakia'],
                        'CH': ['deu', 'switzerland'],
                        'LT': ['lit', 'lithuania'],
                        'LV': ['lat', 'latvia'],
                        'EE': ['est', 'estonia'],
                        'SE': ['swe', 'sweden'],
                        'DK': ['dan', 'denmark'],
                        'FI': ['fin', 'finland']}
    try:
        [LANGUAGE, COUNTRY] = LANGUAGE_COUNTRY[COUNTRY_CODE]
    except:
        sys.exit()
    getTemplate(COUNTRY)
    getConfig()
    FILELIST = getFlist(INV_FOLDER)
    # print(FILELIST)
    # pytesseract.pytesseract.tesseract_cmd = r'C:\\Users\\I559057\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract'
    # steve's machine
    final_res = {"invoice": [], "amount": []}
    RES_FOLDER = make_dir(RES_FOLDER)
    for filename in FILELIST:
        print(filename)
        pic_list = pdf2img(INV_FOLDER + "/" + filename)
        if len(pic_list) == 0:
            continue
        tmp_file_res = {"invoice": [], "amount": []}
        pic_count = 1
        for pic_name in pic_list:
            img = cv.imread(pic_name)
            # gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # 转化为灰度图
            # ret, binary = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)
            data = identify_pic(img, languae=LANGUAGE)
            # cv.namedWindow('img', cv.WINDOW_NORMAL)
            # cv.imshow("img", binary)
            # cv.waitKey(0)
            invoice_amount = {"invoice": [], "amount": []}
            # 识别发票
            for keyword in KEYWORD_LIST:
                tg = data.get(keyword.upper())
                if tg is not None:
                    for pos in tg:  # 循环keyword的位置
                        res = find_value(target=pos, pos_lis=data)
                        new_keyword = res["below"][0]
                        tg = res["below"][1]
                        if new_keyword == '':
                            break
                        invoice_amount["invoice"].append(res["below"])
                        count = 0
                        while new_keyword != "":
                            if count >= 50:  # 循环超过50次强行退出
                                break
                            res = find_value(target=tg, pos_lis=data)
                            new_keyword = res["below"][0]
                            tg = res["below"][1]
                            if new_keyword == '':
                                break
                            invoice_amount["invoice"].append(res["below"])
                            count += 1
            # 按照发票数量识别金额
            for keyword in KEYWORD_AMOUNT:
                tg = data.get(keyword.upper())
                if tg is not None:
                    for pos in tg:
                        res = find_amount(target=pos, pos_lis=data)
                        new_keyword = res["below"][0]
                        tg = res["below"][1]
                        if new_keyword == '':
                            break
                        invoice_amount["amount"].append(res["below"])
                        count = 1
                        while new_keyword != '':
                            if count >= 50:
                                break
                            res = find_amount(target=tg, pos_lis=data)
                            new_keyword = res["below"][0]
                            tg = res["below"][1]
                            if new_keyword == '':
                                break
                            invoice_amount["amount"].append(res["below"])
                            count += 1
            # if len(invoice_amount["amount"]) > len(invoice_amount["invoice"]):
            #     invoice_amount["amount"] = invoice_amount["amount"][:-1]
            # print(invoice_amount)
            invoice_amount = match_invoice_amount(invoice_amount)
            for inv in invoice_amount["invoice"]:
                # final_res["invoice"].append(inv)
                tmp_file_res["invoice"].append(inv)
            for amo in invoice_amount["amount"]:
                # final_res["amount"].append(amo)
                tmp_file_res["amount"].append(amo)
            pic_file = filename[:-4] + "_" + str(pic_count) + ".jpg"
            drawBox(im=img, result=invoice_amount, save_path=RES_FOLDER + "\\" + pic_file)
            pic_count += 1
        excel_file = filename[:-4] + ".xls"
        write_excel(identified_res=tmp_file_res, save_path=RES_FOLDER + "\\" + excel_file)

    # write_excel(identified_res=final_res, save_path=RES_FOLDER+"\\res.xls")
