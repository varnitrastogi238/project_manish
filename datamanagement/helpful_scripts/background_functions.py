# To add a new cell, type '# %%'
# To add a new markdown cell, type '# %% [markdown]'
# %%

import calendar
from datetime import date
from nsepython import *
from datetime import datetime
from datetime import timedelta
import pandas as pd
from time import strptime
import requests
import json
import pandas as pd
# from datamanagement.models import *



def this_scripts():

    url="https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    data=requests.get(url=url)
    data=data.json()
    df = pd.DataFrame(data)

    # df=pd.read_csv('datamanagement/scripts.csv')

    df1=df[:1]
    # print(df1)


    for i in range(len(df)):
        print(i)

        if '-EQ' in df['symbol'][i] and 'NSE' in df['exch_seg'][i]:
            df1.loc[len(df1.index)] = df.loc[i] 
        else:
            continue


    df1.to_csv("datamanagement/helpful_scripts/scripts.csv")

if __name__== "__main__":
    this_scripts()