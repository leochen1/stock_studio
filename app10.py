import requests
import pandas as pd
import numpy as np
import talib
import yfinance as yf
from tqdm import tqdm
from datetime import datetime
from collections import defaultdict


def get_company_info_data(url):
    res = requests.get(url)
    df = pd.read_html(res.text)[0]
    df.columns = df.iloc[0]
    df = df.iloc[1:]
    df = df[['有價證券代號', '有價證券名稱', '產業別']]
    df = df.dropna()
    return df

def crawelrCompanyData():
    try:
        df1 = get_company_info_data("https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=1&issuetype=1&industry_code=&Page=1&chklike=Y")
        df2 = get_company_info_data("https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=4&industry_code=&Page=1&chklike=Y")
        stock_codes_1 = df1.apply(lambda x: (x['有價證券代號']+'.TW', x['有價證券名稱'], x['產業別']), axis=1).tolist()  # TWSE 上市
        stock_codes_2 = df2.apply(lambda x: (x['有價證券代號']+'.TWO', x['有價證券名稱'], x['產業別']), axis=1).tolist()  # TWSE 上櫃
        stock_codes = stock_codes_1 + stock_codes_2
        return stock_codes
    except Exception as e:
        return str(e)
    
stock_codes = crawelrCompanyData()
# print(stock_codes)


def analyze_stock(stock_code):
    df = yf.Ticker(stock_code).history(period = 'max')
    df_info = yf.Ticker(stock_code).info
    recommendation_mean = df_info.get('recommendationMean', '-')  # 取得股票推薦值
    recommendationKey = df_info.get('recommendationKey', '-') # 取得股票投資建議

    plus_di_result = talib.PLUS_DI(df.High, df.Low, df.Close, timeperiod=14)
    minux_di_result = talib.MINUS_DI(df.High, df.Low, df.Close, timeperiod=14)
    adx_result = talib.ADX(df.High, df.Low, df.Close, timeperiod = 14)
    sma_20 = talib.SMA(df['Close'].values, timeperiod=20)  # 計算20日均線

    result_df = pd.DataFrame(index=df.index)
    result_df['+DI'] = plus_di_result
    result_df['-DI'] = minux_di_result
    result_df['ADX'] = adx_result

    result_df['+DI_increase'] = result_df['+DI'] > result_df['+DI'].shift(1)
    result_df['-DI_decrease'] = result_df['-DI'] < result_df['-DI'].shift(1)
    result_df['ADX_increase'] = result_df['ADX'] > result_df['ADX'].shift(1)
    result_df['+DI_greater_than_-DI'] = result_df['+DI'] > result_df['-DI']
    result_df['ADX_less_than_25'] = result_df['ADX'] < 25
    result_df['Volume_increase'] = df['Volume'] > 2 * df['Volume'].shift(1)
    result_df['Volume_1000'] = df['Volume'] / 1000 
    result_df['Close_less_than_100'] = df['Close']
    result_df['Close_greater_than_SMA20'] = df['Close'] > sma_20  # 收盤價是否大於20日均線
    
    
    # 檢查最後一個日期是否符合規則
    last_row = result_df.iloc[-1]
    if last_row['+DI_increase'] and last_row['-DI_decrease'] and last_row['ADX_increase'] and last_row['+DI_greater_than_-DI'] and last_row['ADX_less_than_25'] and last_row['Volume_increase'] and last_row['Volume_1000'] > 1000 and last_row['Close_less_than_100'] < 100 and last_row['Close_greater_than_SMA20']:
        return True, recommendation_mean, recommendationKey
    else:
        return False, recommendation_mean, recommendationKey


# 建立一個空的列表來儲存符合條件的股票代碼
matched_stocks = []
# 對每一個股票代碼進行迭代，並調用 analyze_stock 函數
count = 0
# 在 analyze_stock 函數中，將股票代碼、名稱和產業別一起添加到 matched_stocks 列表中
for stock_code, stock_name, industry in tqdm(stock_codes):
    match, recommendation_mean, recommendationKey = analyze_stock(stock_code)
    if match:
        count += 1
        print(f'股票代號 : {stock_code} 今天符合規則.')
        matched_stocks.append((stock_code, stock_name, industry, recommendation_mean, recommendationKey))

print("共有幾筆符合 : ", count)

# 修改最後的輸出格式，以便將產業別和推薦平均值一起輸出
industry_stocks = defaultdict(list)
for code, name, industry, recommendation_mean, recommendationKey in matched_stocks:
    code = code.split('.')[0]  # 只保留 "." 前面的部分
    industry_stocks[industry].append(f'{code}({name}) ({recommendation_mean})({recommendationKey})')

matched_stocks_str = ''
for industry, stocks in industry_stocks.items():
    matched_stocks_str += f'產業別 : {industry}\n'
    matched_stocks_str += ',\n'.join(stocks) 
    matched_stocks_str += '\n\n'

# 輸出字串
print(matched_stocks_str)


# 發送 Line Notify 通知
# https://developers.line.biz/en/docs/messaging-api/sticker-list/#sticker-definitions
def send_line_notify(notification_message, stickerPackageId, stickerId):
    line_notify_token = 'boHMgzAvRReM6BADCyM3eodXmqkgrkrwlRD2P4Utf0b'  # LB排程事項通知群
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {
        'message': notification_message,
        'stickerPackageId': stickerPackageId,
        'stickerId': stickerId
    }
    requests.post(line_notify_api, headers=headers, data=data)

# 組合 Line Notify 訊息
msg = f'發送時間 : {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}\n'
msg += '''
選股策略如下 : 
1. +DI 大於昨日 +DI
2. -DI 小於昨日 -DI
3. ADX 大於昨日 ADX
4. +DI 大於 -DI
5. ADX < 25
6. 成交量 > 昨日 * 2
7. 成交量 > 1000 張
8. 收盤股價 < 100 元
9. 收盤價大於20日均線
'''
msg += f'\n符合條件的上市櫃股票代碼 : \n{matched_stocks_str} 共 {count} 檔'
print(msg)

# 發送 Line Notify
send_line_notify(msg, "6632", "11825376")