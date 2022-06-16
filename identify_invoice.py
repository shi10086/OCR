import os

import cv2 as cv
import pytesseract

from pdf2img import pdf2img, find_value, identify_pic, find_amount

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
                "Beleg",
                "Belegnummer"
                ]
KEYWORD_AMOUNT = ["Betrag"]
pytesseract.pytesseract.tesseract_cmd = r'C:\\Users\\I559057\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract'


def getFlist(path):
    # for root, dirs, files in os.walk(path):
    #     print('root_dir:', root)  # 当前路径
    #     print('sub_dirs:', dirs)  # 子文件夹
    #     print('files:', files)  # 文件名称，返回list类型
    # return files
    return os.listdir(path)


FILELIST = getFlist(FOLDER)
print(FILELIST)

for filename in FILELIST:
    print(filename)
    pic_list = pdf2img("./invoices/" + filename)
    for pic_name in pic_list:
        img = cv.imread(pic_name)
        gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)  # 转化为灰度图
        ret, binary = cv.threshold(gray, 200, 255, cv.THRESH_BINARY)
        data = identify_pic(binary)
        cv.namedWindow('img', cv.WINDOW_NORMAL)
        cv.imshow("img", binary)
        cv.waitKey(0)
        invoice_amount = {"invoice": [], "amount": []}
        for keyword in KEYWORD_LIST:
            tg = data.get(keyword)
            if tg is not None:
                print(keyword)
                for pos in tg:
                    res = find_value(target=pos, pos_lis=data)
                    new_keyword = res["below"]
                    print(new_keyword)
                    if len(new_keyword) < 7:
                        continue
                    invoice_amount["invoice"].append(new_keyword)
                    tmp_idx = 0
                    while new_keyword != "":
                        new_pos = data.get(new_keyword)
                        res = find_value(target=new_pos[tmp_idx], pos_lis=data)
                        new_keyword = res["below"]
                        if len(new_keyword) < 7:
                            break
                        invoice_amount["invoice"].append(new_keyword)
        num_of_invoice = len(invoice_amount["invoice"])  # 发票数量
        print(num_of_invoice)
        for keyword in KEYWORD_AMOUNT:
            tg = data.get(keyword)
            if tg is not None:
                print(keyword)
                for pos in tg:
                    res = find_amount(target=pos, pos_lis=data)
                    new_keyword = res["below"]
                    invoice_amount["amount"].append(new_keyword)
                    while new_keyword != "" and len(invoice_amount["amount"]) < len(invoice_amount["invoice"]):
                        new_pos = data.get(new_keyword)
                        res = find_amount(target=new_pos[0], pos_lis=data)
                        new_keyword = res["below"]
                        invoice_amount["amount"].append(new_keyword)
        if len(invoice_amount["amount"]) > len(invoice_amount["invoice"]):
            invoice_amount["amount"] = invoice_amount["amount"][:-1]
        print(invoice_amount)
