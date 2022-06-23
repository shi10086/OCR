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

if __name__=="__main__":
    app.run(debug=True)
