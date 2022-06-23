from flask import Flask,request,render_template,url_for,redirect
import configparser
import sys
import os

import pandas as pd



app=Flask(__name__)

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
            'lan':s,
            'amount':key_amount,
            'references':key_refrences
        })
    return {'data': data}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/getTemplate')
def getTempalte():
    data = readTemplate()
    return data

@app.route('/saveTemplate',methods=['POST'])
def saveTemplate():
    args = request.json
    items = args['data']
  
    cf = configparser.ConfigParser()
    for item in items:
        lan = item['lan']
        reference = item['references']
        amount = item['amount']
    
    #cf.read("../template.conf")
        cf[lan] = {
            'reference': "\n".join(reference.split(",")),
            'amount': "\n".join(amount.split(","))
        }    
    with open("../template.conf", 'w') as configfile:
        cf.write(configfile)
    return 'success'

def getFlist(path):
    return os.listdir(path)


if __name__=="__main__":
    filePath = sys.argv[1]
    lists = getFlist(filePath)
    print(lists)
    app.run(debug=True)
