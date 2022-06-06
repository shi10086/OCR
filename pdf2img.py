import fitz
import pytesseract
from pytesseract import Output
import cv2 as cv


def pdf2img(filename):
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
        pic_name = filename.split(".")[0]+"_page_"+str(page_num)+".png"
        pix.save(pic_name)
        pic_list.append(pic_name)
    return pic_list


def identify_pic(img):
    data = {}
    d = pytesseract.image_to_data(img, output_type=Output.DICT)
    for i in range(len(d['text'])):
        if 0 < len(d['text'][i]):
            (x, y, w, h) = (d['left'][i], d['top']
                            [i], d['width'][i], d['height'][i])
            if data.get(d['text'][i]):
                data[d['text'][i]].append(
                    [d['left'][i], d['top'][i], d['width'][i], d['height'][i]])
            data[d['text'][i]] = (
                [[d['left'][i], d['top'][i], d['width'][i], d['height'][i]]])
    return data


if __name__ == '__main__':
    filename = "Birgit Klaerner, reh 2808, FI FS IS-DE_2020_11_27_12_56_53.pdf"
    pytesseract.pytesseract.tesseract_cmd = r'C:\\Users\\I559057\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract'
    pic_list = pdf2img(filename)
    for pic_name in pic_list:
        img = cv.imread(pic_name)
        data = identify_pic(img)
        print(data)
        keyword = "Kundennummer"
        print(data.get(keyword))
