from csv import excel
from flask import Flask, request, render_template, url_for, redirect, render_template_string, Response, make_response, send_file
import configparser
import sys
import os
from functools import partial
import pandas as pd
import datetime

filePath = ''
app = Flask(__name__)

app.jinja_env.variable_start_string = '<<'
app.jinja_env.variable_end_string = '>>'


def readTemplate():
    cwd = os.path.join(os.getcwd(), sys.argv[0])
    root_folder = (os.path.dirname(cwd))
    cf = configparser.ConfigParser()
    print(root_folder)
    cf.read('../template.conf')
    sessions = cf.sections()
    words = []
    amount = []
    country = []
    print(sessions)
    data = []
    for s in (sessions):
        print(s)
        key_refrences = (",").join(cf.get(s, 'reference').strip().split('\n'))
        key_amount = (",").join(cf.get(s, 'amount').strip().split('\n'))
        print(key_amount)
        data.append({
            'lan': s,
            'amount': key_amount,
            'references': key_refrences
        })
    return {'data': data}


@app.route('/')
def index():
    return render_template('index.html')


def file_filter(types, f):
    print(types)
    print(f)
    if f[-4:] in types:
        return True
    else:
        return False


@app.route('/getFileList')
def getFileList():

    lists = getFlist(filePath)
    excelList = list(filter(partial(file_filter, ['.xls']), lists))
    pgList = list(filter(partial(file_filter, ['.jpg']), lists))
    return {
        'excelList': excelList,
        'pgList': pgList
    }


@app.route('/getTemplate')
def getTempalte():
    data = readTemplate()
    return data


@app.route('/saveTemplate', methods=['POST'])
def saveTemplate():
    args = request.json
    items = args['data']

    cf = configparser.ConfigParser()
    for item in items:
        lan = item['lan']
        reference = item['references']
        amount = item['amount']

    # cf.read("../template.conf")
        cf[lan] = {
            'reference': "\n".join(reference.split(",")),
            'amount': "\n".join(amount.split(","))
        }
    with open("../template.conf", 'w') as configfile:
        cf.write(configfile)
    return 'success'


def getFlist(path):
    return os.listdir(path)


@app.route('/imgFile/<path:index_path>')
def img_view(index_path=''):
    path = os.path.join(filePath, index_path)
    return send_file(path, mimetype='image/jpg')

@app.route('/fileExcle/<path:index_path>')
def file_view(index_path=''):
    path = os.path.join(filePath, index_path)
    df = pd.read_excel(path)
    table_html = df.to_html(header = True,justify='center',col_space=150)
    return f"""
    <html>
    <body>
    <div>{table_html}</div>
    </body>
    </html>
    
    """



if __name__ == "__main__":
    path = sys.argv[1]
    today = str(datetime.date.today())
    filePath = path + "\\" + today
    print(filePath)
    app.run(debug=True)
