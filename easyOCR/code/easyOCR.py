import sys
import fitz
import os
import datetime
import easyocr
from PIL import Image, ImageDraw
import re


def pyMuPDF_fitz(pdfPath, imagePath):
    startTime_pdf2img = datetime.datetime.now()  # 开始时间
    # print("imagePath="+imagePath)
    pdfDoc = fitz.open(pdfPath)
    # print(pdfDoc)
    for pg in range(pdfDoc.pageCount):
        page = pdfDoc[pg]
        rotate = int(0)
        # 每个尺寸的缩放系数为1.3，这将为我们生成分辨率提高2.6的图像。
        # 此处若是不做设置，默认图片大小为：792X612, dpi=72
        zoom_x = 1.33333333  # (1.33333333-->1056x816)   (2-->1584x1224)
        zoom_y = 1.33333333
        mat = fitz.Matrix(zoom_x, zoom_y).preRotate(rotate)
        pix = page.getPixmap(matrix=mat, alpha=False)

        if not os.path.exists(imagePath):  # 判断存放图片的文件夹是否存在
            os.makedirs(imagePath)  # 若图片文件夹不存在就创建

        image_name = pdfPath.split('/')[-1].strip('.pdf')
        pix.writePNG(imagePath+'/'+f'images_{image_name}.png')  # 将图片写入指定的文件夹内

    endTime_pdf2img = datetime.datetime.now()  # 结束时间
    # print('pdf2img时间=',(endTime_pdf2img - startTime_pdf2img).seconds)


def ocr(pdfPath, imagePath):
    pyMuPDF_fitz(pdfPath, imagePath)
    image_name = pdfPath.split('/')[-1].strip('.pdf')
    file_path = imagePath+'/'+f'images_{image_name}.png'
    # this needs to run only once to load the model into memory
    reader = easyocr.Reader(['de'], gpu=False)
    result_width = reader.readtext(file_path, width_ths=0.2)
    invoice_number = ''
    # print(result_width[40])
    for i in result_width:
        if 'Rechnungsnr' in i[1]:
            index = result_width.index(i)
            for j in range(index, index+10):
                n = result_width[j][1]
                if re.match(r'\d{7}', n):
                    invoice_number = n
                else:
                    invoive_number = 'no matched'
    return invoice_number


if __name__ == "__main__":
    pdfPath = "../invoices/all_languages/German/1.pdf"
    imagePath = '../image'
    invoice_number = ocr(pdfPath, imagePath)
