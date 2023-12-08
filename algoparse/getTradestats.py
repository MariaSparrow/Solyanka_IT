from moexalgo import Ticker
import pandas as pd

fields_path = './main/fields.csv'
def get_tradestats(fields_path, start_date='2020-01-01', end_date='2023-12-31', round_digits=4):
    fields = pd.read_csv(fields_path)
    field_names = fields['TRADE_CODE'].unique().tolist()
    for field_name in field_names:
        tiker_set = []
        for date in [start_date, end_date]:
            trade_stats = pd.DataFrame(Ticker(field_name).tradestats(date=date, till_date=date))
            trade_stats = trade_stats.drop(index=0)

            secid = trade_stats.iloc[0]['secid']
            ts = date
            pr_open = trade_stats.iloc[0]['pr_open']
            pr_high = trade_stats.iloc[:, 3].dropna().max()
            pr_low = trade_stats.iloc[:, 4].dropna().min()
            pr_close = trade_stats.iloc[-1]['pr_close']
            pr_change = round((pr_close - pr_open) / pr_open, round_digits)
            trades = trade_stats.iloc[:, 7].dropna().sum()
            vol = trade_stats.iloc[:, 8].dropna().sum()
            val = trade_stats.iloc[:, 9].dropna().sum()
            pr_std_mean = round(trade_stats.iloc[:,10].dropna().mean(), round_digits)
            # disb = 
            pr_vwap = round((trade_stats.iloc[:, 9] * trade_stats.iloc[:, 12]).dropna().sum() / val, round_digits)
            trades_b = trade_stats.iloc[:, 13].dropna().sum()
            vol_b = trade_stats.iloc[:, 14].dropna().sum()
            val_b = trade_stats.iloc[:, 15].dropna().sum()
            pr_vwap_b = round((trade_stats.iloc[:, 15] * trade_stats.iloc[:, 16]).dropna().sum() / val_b, round_digits)
            trades_s = trade_stats.iloc[:, 17].dropna().sum()
            vol_s = trade_stats.iloc[:, 18].dropna().sum()
            val_s = trade_stats.iloc[:, 19].dropna().sum()
            pr_vwap_s = round((trade_stats.iloc[:, 19] * trade_stats.iloc[:, 20]).dropna().sum() / val_s, round_digits)
            disb = round((vol_b - vol_s) / (vol_b + vol_s), round_digits)

            new_row = pd.Series({'ts': ts, 'secid': secid, 'pr_open': pr_open, 'pr_high': pr_high, 'pr_low': pr_low, 'pr_close': pr_close, 'pr_change': pr_change, 'trades': trades, 'vol': vol, 'val': val, 'pr_std_mean': pr_std_mean, 'disb': disb, 'pr_vwap': pr_vwap, 'trades_b': trades_b, 'vol_b': vol_b, 'val_b': val_b, 'pr_vwap_b': pr_vwap_b, 'trades_s': trades_s, 'vol_s': vol_s, 'val_s': val_s, 'pr_vwap_s': pr_vwap_s})
            tiker_set.append(new_row)

        tiker_set_df = pd.DataFrame(tiker_set)
        file_name = f"{field_name}_st={start_date}_en={end_date}.csv"
        tiker_set_df.to_csv(file_name, index=False, header=True)

get_tradestats(fields_path)