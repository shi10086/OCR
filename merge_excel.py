import os
import sys
import pandas as pd
import datetime


def merge_excel(files):
    res = {"Reference": [], "Gross invoice amount": []}
    for file in files:
        try:
            data = pd.read_excel(file)
            res["Reference"] += [str(s) for s in list(data["Reference"])]
            res["Gross invoice amount"] += [str(s) for s in list(data["Gross invoice amount"])]
        except:
            continue
    return pd.DataFrame(res)


if __name__ == '__main__':
    RES_FOLDER = sys.argv[1]
    today = str(datetime.date.today())
    RES_FOLDER += "\\" + today
    # TARGET_FOLDER = "C:\\Users\\I559057\\Desktop\\OCR_res"
    FILE_LIST = os.listdir(RES_FOLDER)
    FILE_LIST = [RES_FOLDER + "\\" + file for file in FILE_LIST]
    merged_data = merge_excel(FILE_LIST)
    writer = pd.ExcelWriter(RES_FOLDER+"\\result.xls")
    merged_data.to_excel(writer, index=False)
    writer.save()
    writer.close()

