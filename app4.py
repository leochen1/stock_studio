import requests
import pandas as pd
import numpy as np
import talib
import yfinance as yf
from tqdm import tqdm
from datetime import datetime


def get_company_info_data(url):
    res = requests.get(url)
    df = pd.read_html(res.text)[0]
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    df = df[['有價證券代號']]
    df = df.dropna()
    return df

def crawelrCompanyData():
    try:
        df1 = get_company_info_data("https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y")
        # df2 = get_company_info_data("https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=4&industry_code=&Page=1&chklike=Y")
        df = pd.concat([df1])
        stock_codes = df['有價證券代號'].apply(lambda x: x+'.TW').tolist()
        return stock_codes
    except Exception as e:
        return str(e)
    
stock_codes = crawelrCompanyData()
# print(stock_codes)


def analyze_stock(stock_code):
    df = yf.Ticker(stock_code).history(period = 'max')

    plus_di_result = talib.PLUS_DI(df.High, df.Low, df.Close, timeperiod=14)
    minux_di_result = talib.MINUS_DI(df.High, df.Low, df.Close, timeperiod=14)
    adx_result = talib.ADX(df.High, df.Low, df.Close, timeperiod = 14)

    result_df = pd.DataFrame(index=df.index)
    result_df['+DI'] = plus_di_result
    result_df['-DI'] = minux_di_result
    result_df['ADX'] = adx_result

    result_df['+DI_increase'] = result_df['+DI'] > result_df['+DI'].shift(1)
    result_df['-DI_decrease'] = result_df['-DI'] < result_df['-DI'].shift(1)
    result_df['ADX_increase'] = result_df['ADX'] > result_df['ADX'].shift(1)

    # 檢查最後一個日期是否符合規則
    last_row = result_df.iloc[-1]
    if last_row['+DI_increase'] and last_row['-DI_decrease'] and last_row['ADX_increase']:
        return True
    else:
        return False

# 對每一個股票代碼進行迭代，並調用 analyze_stock 函數
count = 0
for stock_code in tqdm(stock_codes):
    if analyze_stock(stock_code):
        count += 1
        print(f'股票代號 : {stock_code} 今天符合規則.')
print("共有幾筆符合 : ", count)
