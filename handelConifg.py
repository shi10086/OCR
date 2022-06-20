import configparser
import sys
import os

from requests import session
import pandas as pd
def getTemplate(fpath):
    cwd = os.path.join(os.getcwd(), sys.argv[0])
    root_folder = (os.path.dirname(cwd))
    cf = configparser.ConfigParser()
    cf.read(os.path.join(root_folder, 'template.conf')) 
    sessions = cf.sections()
    words = []
    amount = []
    country = []
    print(sessions)
    data = {'reference':[],'amount':[],'country':[]}
    for s in (sessions):
        print(s)
         
        key_refrences = (",").join(cf.get(s, 'reference').strip().split('\n'))
        print(key_refrences)
        print(cf.sections())
        key_amount =  (",").join(cf.get(s, 'amout').strip().split('\n'))
        print(key_amount)
        data['reference'].append(key_refrences)
        data['amount'].append(key_amount)
        data['country'].append(s)

    df = pd.DataFrame(data)
    df.to_excel(fpath+"\config.xlsx",index=False, sheet_name='config')

def changeTemplate():
    cwd = os.path.join(os.getcwd(), sys.argv[0])
    root_folder = (os.path.dirname(cwd))
    cf = configparser.ConfigParser()
    cf.read(os.path.join(root_folder, 'template.conf'))      

if __name__ == '__main__':
    command =  sys.argv[1]
    fpath = sys.argv[2]
    if command == 'read':
        getTemplate(fpath)

    if command == 'change':
        changeTemplate()

