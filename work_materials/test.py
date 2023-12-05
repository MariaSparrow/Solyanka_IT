from moexalgo import Ticker
import pandas as pd

# выбираем акции Сбера
sber = Ticker('SBER')

# получим дневные свечи с 2020 года
a = pd.DataFrame(sber.candles(date='2001-01-01', till_date='2023-11-01', period='D')) # D 1h
print(len(a), a.loc[0,'begin'],a.loc[len(a)-1,'begin'])
print(a.head())