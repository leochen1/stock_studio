import requests
import pandas as pd

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
        df2 = get_company_info_data("https://isin.twse.com.tw/isin/class_main.jsp?owncode=&stockname=&isincode=&market=2&issuetype=4&industry_code=&Page=1&chklike=Y")
        df = pd.concat([df1,df2])
        stock_codes = df['有價證券代號'].apply(lambda x: x+'.TW').tolist()
        return stock_codes
    except Exception as e:
        return str(e)
    
stock_codes = crawelrCompanyData()
print(stock_codes)