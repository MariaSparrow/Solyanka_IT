import streamlit as st
import numpy as np
import pandas as pd
import os
from moexalgo import Ticker

fund = 10000
invest_strategy = True
spec_strategy = False
min_instrs_num = 8
comission_pct = 0.03
# st.write(os.getcwd())

sec_portfolio_path = "./main/sec_portfolio.csv"
sec_deals_path = "./main/sec_deals.csv"
fund_path = "./main/fund.csv"
strategy_path = "./main/strategy.csv"

if os.path.exists(fund_path):
    with open(fund_path, "r") as f:
        fund = float(f.readline())
        min_instrs_num = int(f.readline())
        
if os.path.exists(sec_portfolio_path):
    sec_portfolio = pd.read_csv(sec_portfolio_path)
else:
    sec_portfolio = pd.DataFrame(columns=['Количество, лоты', 'Балансовая стоимость, руб.','Процент портфеля, %'])

st.text('Портфель')
st.dataframe(sec_portfolio)

if os.path.exists(sec_deals_path):
    sec_deals = pd.read_csv(sec_deals_path)
else:
    sec_deals = pd.DataFrame(columns=['Дата', 'Время', 'Инструмент', 'Направление (купля/продажа)', 'Объем сделки, лоты', 'Цена сделки, рублей'])

if len(sec_deals) > 5:
    sec_deals = sec_deals.iloc[-5:,:]
st.text('Сделки')
st.dataframe(sec_deals)

    
if os.path.exists(strategy_path):
    with open(strategy_path, "r") as f:
        invest_strategy = bool(f.readline())
        spec_strategy = bool(f.readline())


fund = st.sidebar.number_input("Сумма депозита, рублей", min_value=fund, max_value=10000000, placeholder="Введите сумму депозита...")


#st.sidebar.write(cash)
st.sidebar.write('Выбор стратегии:')

if st.sidebar.checkbox('Инвестиционная', value=invest_strategy, help=f"Только длинные позиции по инструментам. \
                       \nНа один инструмент не более 1/{min_instrs_num} части активов. "):
    invest_strategy = True
else:
    invest_strategy = False
    
if st.sidebar.checkbox('Спекулятивная', value=spec_strategy, help=f"Длинные и короткие позиции по инструментам.\n \
    На один инструмент не более 1/{min_instrs_num} части активов.\n \
    При выборе одновременно двух стратегий на cпекулятивную стратегию\n \
    используется 1/{min_instrs_num} части активов, на инвестиционную\n \
    стратегию остальная часть активов."):
    
    spec_strategy = True
else:
    spec_strategy = False


#=========== Starts Portfolio investigation ===============
fields_path = './main/fields.csv'

@st.cache_data
def sec_length(fields_path):
    data_dict = {}
    sec_fields = pd.read_csv(fields_path)
    for k, v in sec_fields.groupby('BIGFIELD').groups.items():
        field_secs = list(sec_fields.loc[v,'TRADE_CODE'])
        st.write(k)
        fields_df = pd.DataFrame(Ticker(field_secs[0]).candles(date='2001-01-01', till_date='2023-12-04', period='D'))
        fields_df = fields_df.drop(['open', 'high', 'low', 'value', 'volume', 'end'], axis=1)
        fields_df.rename(columns={'close':field_secs[0]},inplace=True)
        # st.write(field_secs[0], len(fields_df), fields_df.loc[0,'begin'],fields_df.loc[len(fields_df)-1,'begin'],fields_df.columns)
        
        for field in field_secs[1:]:
            if field in ['VKCO', 'POSI','ENPG','WUSH','LENT','GEMC','MDMG','SMLT', \
                'RENI','SPBE','ELFV','GLTR','FLOT','FIXP','OKEY']:
                continue
            # получим дневные свечи с 2020 года
            a = pd.DataFrame(Ticker(field).candles(date='2001-01-01', till_date='2023-12-04', period='D')) # D 1h
            a = a.drop(['open', 'high', 'low', 'value', 'volume', 'end'], axis=1)
            a.rename(columns={'close':field},inplace=True)
            # st.write(field, len(a), a.loc[0,'begin'],a.loc[len(a)-1,'begin'])
            # fields_lst.append(a)
            fields_df = pd.merge(fields_df,a,on='begin')
        fields_df = fields_df.dropna(axis=0) #.set_index('begin')
        data_dict[k] = fields_df
        # st.write(k, len(fields_df), fields_df.loc[0,'begin'], fields_df.loc[len(fields_df)-1,'begin'])
    return data_dict
data_dict = sec_length(fields_path)
df = data_dict[list(data_dict.keys())[0]]
df = df.drop(['begin'], axis=1)

first_index = 50
ds_list = []
for col in df.columns:
    ds = pd.Series([0]*len(df))
    ds.name = col
    sum_cidx = 0
    for n in range(first_index+1,len(df)):
        mx = df.loc[n-first_index:n-1,col].max()
        mn = df.loc[n-first_index:n-1,col].min()
        if mx == mn:
            cidx = 0
        else:
            cidx = (df.at[n,col] - mn) / (mx - mn) - 1
        # sum_cidx += cidx
        ds[n] = cidx #sum_cidx
    ds_list.append(ds)
data_field = pd.concat(ds_list, axis=1)
st.line_chart(data_field.loc[:,:])
min_idx = data_field.idxmin(axis=1)
max_idx = data_field.idxmax(axis=1)
res_dict = {k:{'pos':0,'res':0,'deal':0} for k in data_field.columns}
st.write(res_dict)

# for n in range(first_index+1,len(data_field)):
    


            
        
        
    
    
st.line_chart(df)

# for k, v in data_dict.items():




instrs_list = ['AFLT', 'VTBR']

#=========== Ends Portfolio investigation ===============

#=========== Start Portfolio check ===============

instrs_for_buy = ['GAZP']
instrs_for_sell = ['VTBR']

#=========== End Portfolio check ===============
#=========== Start Deals ===============
def make_deal_sell(instr):
    sell_val = 0
    return sell_val

def make_deal_buy(instr):
    buy_val, lots = 0, 0
    return buy_val, lots

def portfolio_value(sec_portfolio):
    return

for instr in instrs_for_sell:
    if instr in instrs_list:
        sell_val = make_deal_sell(instr)
for instr in instrs_for_buy:
    if instr not in instrs_list:
        buy_val, lots  = make_deal_buy(instr)
#=========== End Deals ===============

#sec_portfolio = pd.DataFrame(columns=['Количество, лоты','Балансовая стоимость, руб.','Процент портфеля, %'])



