import streamlit as st
import numpy as np
import pandas as pd
import os
from moexalgo import Ticker
import math
import time

fund = 10000
invest_strategy = True
spec_strategy = False
min_instrs_num = 8
comission_part = 0.0003 # доля комиссии от цены сделки
# st.write(os.getcwd())

# файлы для сохранения
sec_portfolio_path = "./main/sec_portfolio.csv" # портфель
sec_deals_path = "./main/sec_deals.csv"         # сделки
fund_path = "./main/fund.csv"                   # сумма депозита
strategy_path = "./main/strategy.csv"           # стратегия

# проверка существования сохраненных данных и загрузка при наличии
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

while not spec_strategy and not invest_strategy:
    st.sidebar.write('Для продолжения работы НЕОБХОДИМО выбрать стратегию.')
    time.sleep(3)
#=========== Starts Portfolio investigation ===============
fields_path = './main/fields.csv'

@st.cache_data
def sec_length(fields_path):
    st.text("Скачивание данных")
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
                'RENI','SPBE','ELFV','GLTR','FLOT','FIXP','OKEY','VSMO', 'BANEP']:
                continue
            # получим дневные свечи
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

first_index = 30

for k in data_dict.keys():
    st.write("Сектор экономики: ", k)
    df = data_dict[k]
    date_col = df.pop('begin')
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
    # st.write("Индексы инструментов")
    # st.line_chart(data_field.loc[:,:])
    # st.dataframe(data_field.head()) 
    min_idx = data_field.idxmin(axis=1)
    max_idx = data_field.idxmax(axis=1)
    data_field['min_idx'] = min_idx
    data_field['max_idx'] = max_idx
    res_columns = []
    for col in df.columns:
        data_field[col+'_pos'] = 0
        data_field[col+'_res'] = 0
        data_field[col+'_deal'] = 0
        res_columns.append(col+'_res')

    # st.dataframe(data_field)     


    buy_pos = 1
    if spec_strategy == True:
        sell_pos = -1
    else:
        sell_pos = 0

    for n in range(first_index+1,len(data_field)):
        for col in df.columns:
            price = df.at[n,col] / df.at[0,col]
            if col == data_field.at[n,'min_idx']:
                if data_field.at[n,col]>0:
                    deal_pos = 0
                else:
                    deal_pos = sell_pos
                if data_field.at[n-1,col+'_deal'] >= 0:
                    data_field.at[n,col+'_res'] = data_field.at[n-1,col+'_pos'] \
                                    + data_field.at[n-1,col+'_deal'] * price
                    data_field.at[n,col+'_pos'] = data_field.at[n-1,col+'_pos'] \
                                    - (deal_pos - data_field.at[n-1,col+'_deal'] \
                                    - math.fabs(deal_pos - data_field.at[n-1,col+'_deal']) * comission_part \
                                    ) * price
                    data_field.at[n,col+'_deal'] = deal_pos
                else:
                    data_field.at[n,col+'_res'] = data_field.at[n-1,col+'_pos'] \
                                    + data_field.at[n-1,col+'_deal'] * price
                    data_field.at[n,col+'_pos'] = data_field.at[n-1,col+'_pos'] 
                    data_field.at[n,col+'_deal'] = data_field.at[n-1,col+'_deal']
                
            elif col == data_field.at[n,'max_idx']:
                if data_field.at[n,col]<0:
                    deal_pos = 0
                else:
                    deal_pos = buy_pos
                if data_field.at[n-1,col+'_deal'] <= 0:
                    data_field.at[n,col+'_res'] = data_field.at[n-1,col+'_pos'] \
                                    + data_field.at[n-1,col+'_deal'] * price
                    data_field.at[n,col+'_pos'] = data_field.at[n-1,col+'_pos'] \
                                    - (deal_pos - data_field.at[n-1,col+'_deal'] \
                                    - math.fabs(deal_pos - data_field.at[n-1,col+'_deal']) * comission_part \
                                    ) * price
                    data_field.at[n,col+'_deal'] = deal_pos
                else:
                    data_field.at[n,col+'_res'] = data_field.at[n-1,col+'_pos'] \
                                    + data_field.at[n-1,col+'_deal'] * price
                    data_field.at[n,col+'_pos'] = data_field.at[n-1,col+'_pos']
                    data_field.at[n,col+'_deal'] = data_field.at[n-1,col+'_deal']
            
            else:
                data_field.at[n,col+'_res'] = data_field.at[n-1,col+'_pos'] \
                                + data_field.at[n-1,col+'_deal'] * price
                data_field.at[n,col+'_pos'] = data_field.at[n-1,col+'_pos'] \
                                - (0 - data_field.at[n-1,col+'_deal'] \
                                - math.fabs(0 - data_field.at[n-1,col+'_deal']) * comission_part \
                                ) * price
                data_field.at[n,col+'_deal'] = 0

                # data_field.at[n,col+'_res'] = data_field.at[n-1,col+'_pos'] \
                #                 + data_field.at[n-1,col+'_deal'] * price
                # data_field.at[n,col+'_pos'] = data_field.at[n-1,col+'_pos']
                # data_field.at[n,col+'_deal'] = data_field.at[n-1,col+'_deal']
                
                

    data_field['res'] = data_field.loc[:, res_columns].sum(axis=1)
    st.text("Результат")
    st.text("Доля от депозита на 1 инструмент,\nусредненная по всем инструментам\n в секторе.")
    
    data_field.index = date_col
    
    st.line_chart(data_field['res']/len(df.columns))

    # st.write(len(data_field), len(df))

    st.dataframe(data_field)     
# st.dataframe(df)     

    


            
        
        
    
    
# st.line_chart(df)

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



