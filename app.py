import numpy as np
import pandas as pd
import talib
import yfinance as yf

df = yf.Ticker('2313.TW').history(period = 'max')

plus_di_result = talib.PLUS_DI(df.High, df.Low, df.Close, timeperiod=14)
minux_di_result = talib.MINUS_DI(df.High, df.Low, df.Close, timeperiod=14)
adx_result = talib.ADX(df.High, df.Low, df.Close, timeperiod = 14)

# 建立一個新的 DataFrame 來存儲結果
result_df = pd.DataFrame(index=df.index)
result_df['+DI'] = plus_di_result
result_df['-DI'] = minux_di_result
result_df['ADX'] = adx_result

# 找出符合條件的日期
result_df['+DI_increase'] = result_df['+DI'] > result_df['+DI'].shift(1)
result_df['-DI_decrease'] = result_df['-DI'] < result_df['-DI'].shift(1)
result_df['ADX_increase'] = result_df['ADX'] > result_df['ADX'].shift(1)

# 所有條件都符合的日期
match_dates = result_df[result_df['+DI_increase'] & result_df['-DI_decrease'] & result_df['ADX_increase']]

print(match_dates)