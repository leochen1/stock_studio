import numpy as np
import pandas as pd
import talib
import yfinance as yf
from tqdm import tqdm
from datetime import datetime

# 台股所有上市櫃公司的股票代碼列表
# 這裡只是一個示例，你需要替換成實際的股票代碼列表
stock_codes = ['8438.TW', '1102.TW', '2317.TW', '2330.TW', '3008.TW', '2313.TW', '2360.TW']

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
for stock_code in tqdm(stock_codes):
    if analyze_stock(stock_code):
        print(f'股票代號 : {stock_code} 今天符合規則.')