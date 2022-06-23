import os

import cv2 as cv
import pytesseract
from pytesseract.pytesseract import TesseractError

from pdf2img import pdf2img, find_value, identify_pic, find_amount, identify_pic_easyocr
import configparser
import sys
import os
import xlwt

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
    db_config.read(os.path.join(root_folder, 'template.conf'))
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
    invoice_list = invoice_amount["invoice"]
    amount = invoice_amount["amount"]
    if len(amount) == 0:
        return {"invoice": [], "amount": []}
    matched_amount = []
    for inv in invoice_list:
        inv_y = inv[1][1]
        min_dis = 9999
        tmp_amo = amount[0]
        for amo in amount:
            if amo in matched_amount:
                continue
            amo_y = amo[1][1]
            if abs(amo_y - inv_y) < min_dis:
                min_dis = abs(amo_y - inv_y)
                tmp_amo = amo
        matched_amount.append(tmp_amo)
    invoice_amount["amount"] = matched_amount
    return invoice_amount


def write_excel(identified_res, save_path):
    # try:
    #     book = xlwt.Workbook(encoding='utf-8', style_compression=0)
    #     sheet = book.add_sheet('invoice & amount', cell_overwrite_ok=True)
    #     col = ('invoice number', 'amount')
    #     inv = identified_res["invoice"]
    #     amo = identified_res["amount"]
    #     for i in range(len(col)):
    #         sheet.write(0, i, col[i])
    #     for row in range(len(inv)):
    #         sheet.write(row + 1, 0, inv[row])
    #         sheet.write(row + 1, 1, amo[row])
    #     book.save(save_path)
    # except Exception as e:
    #     print(e)
    #     print("fail to save the result")
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


if __name__ == '__main__':
    LANGUAGE = sys.argv[1]
    INV_FOLDER = sys.argv[2]
    RES_FOLDER = sys.argv[3]
    COUNTRY = sys.argv[4]
    getTemplate(COUNTRY)
    getConfig()
    FILELIST = getFlist(INV_FOLDER)
    # print(FILELIST)
    # pytesseract.pytesseract.tesseract_cmd = r'C:\\Users\\I559057\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract'
    # steve's machine
    final_res = {"invoice": [], "amount": []}
    for filename in FILELIST:
        print(filename)
        pic_list = pdf2img(INV_FOLDER + "/" + filename)
        for pic_name in pic_list:
            img = cv.imread(pic_name)
            # gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # 转化为灰度图
            # ret, binary = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)
            # data = identify_pic(img, languae=LANGUAGE)
            data = identify_pic_easyocr(img, language=LANGUAGE)
            # cv.namedWindow('img', cv.WINDOW_NORMAL)
            # cv.imshow("img", binary)
            # cv.waitKey(0)
            invoice_amount = {"invoice": [], "amount": []}
            # 识别发票
            for keyword in KEYWORD_LIST:
                tg = data.get(keyword.upper())
                if tg is not None:
                    for pos in tg:
                        res = find_value(target=pos, pos_lis=data)
                        new_keyword = res["below"][0]
                        tg = res["below"][1]
                        if new_keyword == '':
                            break
                        # if len(new_keyword) < 7:
                        #     continue
                        invoice_amount["invoice"].append(res["below"])
                        tmp_idx = 0
                        while new_keyword != "":
                            res = find_value(target=tg, pos_lis=data)
                            new_keyword = res["below"][0]
                            tg = res["below"][1]
                            # if len(new_keyword) < 7:
                            #     break
                            if new_keyword == '':
                                break
                            invoice_amount["invoice"].append(res["below"])
            # 按照发票数量识别金额
            for keyword in KEYWORD_AMOUNT:
                tg = data.get(keyword.upper())
                if tg is not None:
                    for pos in tg:
                        res = find_amount(target=pos, pos_lis=data)
                        new_keyword = res["below"][0]
                        tg = res["below"][1]
                        invoice_amount["amount"].append(res["below"])
                        while new_keyword != '':
                            pre_keyword = new_keyword
                            res = find_amount(target=tg, pos_lis=data)
                            new_keyword = res["below"][0]
                            tg = res["below"][1]
                            if new_keyword == '' or pre_keyword == new_keyword:
                                break
                            invoice_amount["amount"].append(res["below"])
            # if len(invoice_amount["amount"]) > len(invoice_amount["invoice"]):
            #     invoice_amount["amount"] = invoice_amount["amount"][:-1]
            # print(invoice_amount)
            invoice_amount = match_invoice_amount(invoice_amount)
            for inv in invoice_amount["invoice"]:
                final_res["invoice"].append(inv)
            for amo in invoice_amount["amount"]:
                final_res["amount"].append(amo)
            excel_file = pic_name[:-4] + ".xls"
            write_excel(identified_res=invoice_amount,
                        save_path=RES_FOLDER+"\\"+excel_file)
    #write_excel(identified_res=final_res, save_path=RES_FOLDER+"\\res.xls")
