import streamlit as st
import pandas as pd
import os
from moexalgo import Ticker
import math
import time
from datetime import date, datetime, timedelta

today_date = date.today().strftime("%Y-%m-%d")
fund = 10000
first_index = 30
path_to_data="./main"
min_instrs_num = 8
comission_part = 0.0008 # доля комиссии от цены сделки: 0.04% и проскальзывание: 0.04%
# st.write(os.getcwd())

def load_portfolio(path_to_data="./main", strategy = 'invest', sell_pos = ""):
    sec_portfolio_path = os.path.join(path_to_data,"sec_portfolio_"+strategy+str(sell_pos)+'.csv') # портфель
    sec_deals_path = os.path.join(path_to_data,"sec_deals_"+strategy+str(sell_pos)+'.csv')         # сделки
    fund_path = os.path.join(path_to_data,"fund_"+strategy+str(sell_pos)+'.csv')                   # сумма депозита
    # strategy_path = os.path.join(path_to_data,"strategy_"+strategy+str(sell_pos)+'.csv')           # стратегия
    if os.path.exists(sec_portfolio_path):
        sec_portfolio = pd.read_csv(sec_portfolio_path)
    else:
        sec_portfolio = pd.DataFrame(columns=['Количество, лоты', 'Балансовая стоимость, руб.','Процент портфеля, %'])

    if os.path.exists(sec_deals_path):
        sec_deals = pd.read_csv(sec_deals_path)
    else:
        sec_deals = pd.DataFrame(columns=['Дата', 'Время', 'Инструмент', 'Направление (купля/продажа)', 'Объем сделки, лоты', 'Цена сделки, рублей'])


    if os.path.exists(fund_path):
        with open(fund_path, "r") as f:
            init_fund = float(f.readline())
            current_fund = float(f.readline())
            min_instrs_num = int(f.readline())
    else:
        init_fund = 0
        current_fund = 0
        min_instrs_num = 8
    
    return init_fund, current_fund, min_instrs_num, sec_portfolio, sec_deals
            




#=========== Starts Input parameters ===============


#st.sidebar.write(cash)
# st.sidebar.write('Выбор стратегии:')
st.sidebar.title('Параметры задачи.')

strategy = st.sidebar.radio('Выбор стратегии:', ['Инвестиционная', 'Спекулятивная'],
                    captions = [f"Только длинные позиции по инструментам.\n", \
                                f"Длинные и короткие позиции по инструментам."], index=0)

if strategy == 'Спекулятивная':
    strategy = 'spec'
    operation_text = 'Торговля'
    prognoz_text = 'Проведение торговых операций  по выбранной стратегии'
    if st.sidebar.checkbox('Включая короткие продажи'):
        sell_pos = -1
    else:
        sell_pos = 0
    period = st.sidebar.selectbox('Выберите временной интервал.',
    ('1 минута', '10 минут', '1 час', 'День', 'Неделя'), index=3)
    start_day_dict = {}
    if period == '1 минута':
        period = '1m'
        start_day_dict[period] = (date.today() - timedelta(minutes=10000)).strftime("%Y-%m-%d")
    elif period == '10 минут':
        period = '10m'
        start_day_dict[period] = (date.today() - timedelta(minutes=10000)).strftime("%Y-%m-%d")
    elif period == '1 час':
        period = '1h'
        start_day_dict[period] = (date.today() - timedelta(hours=10000)).strftime("%Y-%m-%d")
    elif period == 'День':
        period = '1D'
        start_day_dict[period] = (date.today() - timedelta(days=10000)).strftime("%Y-%m-%d")
    elif period == 'Неделя':
        period = '1W'
        start_day_dict[period] = (date.today() - timedelta(weeks=1000)).strftime("%Y-%m-%d")
    else:
        period = '1D'
        start_day_dict[period] = (date.today() - timedelta(days=10000)).strftime("%Y-%m-%d")

elif strategy == 'Инвестиционная':
    strategy = 'invest'
    period='1D'
    operation_text = "Прогноз"
    prognoz_text = 'Прогноз движения цен по выбранной стратегии'

buy_pos = 1

operation = st.sidebar.radio('Выбор операций:', [operation_text, 'Тестирование'],
                    captions = [prognoz_text, 'Вывод результатов теста по выбранной стратегии'], index=1)
init_fund = 0
if operation == 'Торговля':
    # operation = 'trade'
    exec_type = 'trading'
    init_fund, current_fund, min_instrs_num, sec_portfolio, sec_deals = load_portfolio(path_to_data="./main", strategy = 'invest', sell_pos = "")
elif operation == 'Прогноз':
    exec_type = 'trading'
elif operation == 'Тестирование':
    # operation = 'test'
    exec_type = 'testing'
        
if init_fund == 0:
    fund = st.sidebar.number_input("Сумма начального депозита, рублей", min_value=fund, max_value=10000000, placeholder="Введите сумму депозита...")
    current_fund = fund
else:
    st.text("Начальный депозит, руб. : " + str(init_fund))
    st.text("Остаток на счете, руб. : " + str(current_fund))
    
#=========== Ends Input parameters ===============

#=========== Disclaimer ===============

# agree = st.checkbox('Отказ от ответственности.', value=True)
# while agree:
#     txt = st.text_area()
#=========== Ends Disclaimer ===============


# файлы для сохранения

# проверка существования сохраненных данных и загрузка при наличии
    
#=========== Starts loading data ===============
fields_path = './main/fields.csv'

@st.cache_data(show_spinner=False)
def sec_length(fields_path, period='D'):
    
    with st.sidebar:
        with st.spinner("Загрузка биржевых данных в разрезе экономических секторов...\n"):
            data_dict = {}
            sec_fields = pd.read_csv(fields_path)
            my_bar = st.progress(0, text="")
            groups_field = sec_fields.groupby('BIGFIELD').groups
            groups_field_len = len(groups_field.keys())
            nprogress = 1
            for k, v in groups_field.items():
                my_bar.progress(nprogress*groups_field_len, text=str(k))
                nprogress += 1
                field_secs = list(sec_fields.loc[v,'TRADE_CODE'])
                stoplist = []
                for fs in field_secs:
                    fields_df = pd.DataFrame(Ticker(fs).candles(date=start_day_dict[period], till_date=today_date, period=period))
                    if exec_type == 'trading':
                        if int(fields_df.at[len(fields_df)-1,'end'].hour) <= 18 and datetime.now().hour>=19:
                            stoplist.append(fs)
                        else:
                            break
                    else:
                        break
                if field_secs == stoplist:
                    continue
                # st.write("stoplist=", stoplist)
                fields_df = fields_df.drop(['close', 'high', 'low', 'value', 'volume', 'end'], axis=1)
                fields_df.rename(columns={'open':fs},inplace=True)
                # st.write(field_secs[0], len(fields_df), fields_df.loc[0,'begin'],fields_df.loc[len(fields_df)-1,'begin'],fields_df.columns)
                # st.write("=================fields_df==============")
                # st.dataframe(fields_df)
                
                for field in field_secs[1+len(stoplist):]:
                    if field in stoplist:
                        # st.write("break=", field)
                        continue
                    # if period == '1D':
                    #     if field in ['VKCO', 'POSI','ENPG','WUSH','LENT','GEMC','MDMG','SMLT', \
                    #         'RENI','SPBE','ELFV','GLTR','FLOT','FIXP','OKEY','VSMO', 'BANEP']:
                    #         continue
                    # получим дневные свечи
                    a = pd.DataFrame(Ticker(field).candles(date=start_day_dict[period], till_date=today_date, period=period)) # D 1h
                    if exec_type == 'trading':
                        if int(a.at[len(a)-1,'end'].hour) <= 18 and datetime.now().hour>=19:
                            continue
                    a = a.drop(['close', 'high', 'low', 'value', 'volume', 'end'], axis=1)
                    a.rename(columns={'open':field},inplace=True)
                    # st.write(field, len(a), a.loc[0,'begin'],a.loc[len(a)-1,'begin'])
                    fields_df = pd.merge(fields_df,a,on='begin')
                fields_df = fields_df.dropna(axis=0) #.set_index('begin')
                # st.write("=================fields_df==============")
                # st.dataframe(fields_df)
                data_dict[k] = fields_df
                # st.write("=================fields_df==============")
                # st.dataframe(fields_df)
                # st.write(k, len(fields_df), fields_df.at[0,'begin'], fields_df.at[len(fields_df)-1,'begin'])
            my_bar.empty()
    st.sidebar.success('Биржевые данные загружены.')
    return data_dict

@st.cache_data(show_spinner=False)
def sec_length_ml(fields_path, period='D'):
    
    with st.sidebar:
        with st.spinner("Загрузка биржевых данных по инструментам ...\n"):
            data_dict = {}
            ml_index_data = pd.read_csv(fields_path)
            ml_index_data_sec_dict = ml_index_data.groupby('unique_id').groups
            my_bar = st.progress(0, text="")
            secs_name_list = list(ml_index_data_sec_dict.keys())
            ml_index_data_sec_dict_len = len(secs_name_list)
            nprogress = 0
            for k in secs_name_list: # k- бумага
                my_bar.progress(nprogress/ml_index_data_sec_dict_len, text=str(k))
                nprogress += 1
                one_sec_pred_df =  ml_index_data[ml_index_data['unique_id'] == k]
                one_sec_pred_df.drop('Unnamed: 0', axis=1, inplace=True)
                one_sec_pred_df.index = pd.Index(range(len(one_sec_pred_df)))
                start_day = one_sec_pred_df.at[0,'ds']         
                end_day = one_sec_pred_df['ds'].iloc[-1] 
                sec_df = pd.DataFrame(Ticker(k).candles(date=start_day, till_date=end_day, period=period))
                sec_df = sec_df.drop(['close', 'high', 'low', 'value', 'volume', 'end'], axis=1)
                
                sec_df = pd.concat([sec_df,one_sec_pred_df], axis=1)
                
                sec_df = sec_df.dropna(axis=0) #.set_index('begin')
                data_dict[k] = sec_df
                # st.write("=================sec_df==============2")
                # st.dataframe(sec_df)
                # st.write(k, len(fields_df), fields_df.at[0,'begin'], fields_df.at[len(fields_df)-1,'begin'])
            my_bar.empty()
    st.sidebar.success('Биржевые данные загружены.')
    return data_dict


#=========== Ends loading data ===============

def minmaxidx(df, first_index):
    ds_list = []
    for col in df.columns:
        ds = pd.Series([0]*len(df))
        ds.name = col
        for n in range(first_index+1,len(df)):
            mx = df.loc[n-first_index:n-1,col].max()
            mn = df.loc[n-first_index:n-1,col].min()
            if mx == mn:
                cidx = 0
            else:
                cidx = (df.at[n,col] - mn) / (mx - mn) - 1
            ds[n] = cidx 
        ds_list.append(ds)
    data_field = pd.concat(ds_list, axis=1)
    return data_field

def take_deal(data_field, n, price, col): 
    # st.write("=================data_field==============")
    # st.dataframe(data_field)
       
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
                            + math.fabs(deal_pos - data_field.at[n-1,col+'_deal']) * comission_part \
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
                            + math.fabs(deal_pos - data_field.at[n-1,col+'_deal']) * comission_part \
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
                        + math.fabs(0 - data_field.at[n-1,col+'_deal']) * comission_part \
                        ) * price
        data_field.at[n,col+'_deal'] = 0
    return data_field

#=========== Starts Portfolio investigation ===============

if strategy == 'spec':
    st.title('Спекулятивная стратегия.')
    if sell_pos == -1:
        st.text('Стратегия включает короткие продажи')
    else:
        st.text('Стратегия включает только длинные позиции')
    # Спекулятивная стратегия testing start =======================
    if exec_type == 'testing':
        st.subheader("Тестовые результаты расчета модели.")
        data_dict = sec_length(fields_path, period)

        for k in data_dict.keys():
            st.write("Сектор экономики: ", k)
            df = data_dict[k]
            date_col = df.pop('begin')
            # Расчет индексов по бумагам за каждый день
            data_field = minmaxidx(df, first_index)
    # st.write("Индексы инструментов")
    # st.line_chart(data_field.loc[:,:])
    # st.dataframe(data_field.head()) 
    # Выбор бумаг с минимальным и максимальным индексами
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

            # 
            for n in range(first_index+1,len(data_field)):
                for col in df.columns:
                    price = df.at[n,col] / df.at[0,col]
                    data_field = take_deal(data_field, n, price, col)
                        
            data_field['res'] = data_field.loc[:, res_columns].sum(axis=1)
            st.text("Доля от депозита на 1 инструмент,\nусредненная по всем инструментам\n в секторе.")
            
            data_field.index = date_col
            
            st.line_chart(data_field['res']/len(df.columns))

            # st.write(len(data_field), len(df))

            # st.dataframe(data_field)   
    # Спекулятивная стратегия testing end =======================
    
    # Спекулятивная стратегия trading start =======================
    elif exec_type == 'trading':     
        st.title('Торговля в разработке')
        data_dict = sec_length(fields_path, period)
        data_deals = {}
        for k in data_dict.keys():
            data_deals[k] = pd.DataFrame(index=[0], columns=data_dict[k].columns)
            data_deals[k][0] = 0
            data_deals[k].pop('begin')
            st.write(k, "=================data_deals==============")
            st.dataframe(data_deals[k])
            
        stop = True
        while stop:
            fields_df = pd.DataFrame(Ticker('SBER').candles(date=start_day_dict[period], till_date=today_date, period=period))
            
            last_time = fields_df.at[len(fields_df)-1, 'end']
            last_time0 = last_time
            
            for k in data_dict.keys():
                st.write("Сектор экономики: ", k)
                df = data_dict[k].loc[-first_index:,:]
                date_col = df.pop('begin')
                data_field = data_deals[k]
                # st.write("0=================df==============")
                # st.dataframe(df)
                
                # Расчет индексов по бумагам за каждый день
                next_row = len(data_field)
                for col in df.columns:
                    mx = df.loc[len(df)-first_index:len(df)-1,col].max()
                    mn = df.loc[len(df)-first_index:len(df)-1,col].min()
                    if mx == mn:
                        cidx = 0
                    else:
                        cidx = (df.at[len(df)-1,col] - mn) / (mx - mn) - 1
                    data_field.at[next_row,col] = cidx 
                    # st.write(data_field)

                # st.write("1=================data_field==============")
                # st.dataframe(data_field)
                # st.write("Индексы инструментов")
                # st.line_chart(data_field.loc[:,:])
                # st.dataframe(data_field.head()) 
                # Выбор бумаг с минимальным и максимальным индексами
                min_idx = data_field.loc[:,df.columns].idxmin(axis=1)
                max_idx = data_field.loc[:,df.columns].idxmax(axis=1)
                # st.write("=================max_idx==============")
                # st.dataframe(max_idx)

                # st.write("=================min_idx==============")
                # st.dataframe(min_idx)
                
                data_field.loc[:,'min_idx'] = min_idx
                data_field.loc[:,'max_idx'] = max_idx
                # st.write("=================data_field==============")
                # st.dataframe(data_field)
                # res_columns = []
                for col in df.columns:
                    data_field[col+'_pos'] = 0
                    data_field[col+'_res'] = 0
                    data_field[col+'_deal'] = 0
                    # res_columns.append(col+'_res')
                    price_df = pd.DataFrame(Ticker(col).candles(date=today_date, till_date=today_date, period='D'))
                    price = price_df.at[len(price_df)-1,'open']
                    # st.write("0=================data_field==============")
                    # st.dataframe(data_field)
                    data_field = take_deal(data_field, len(data_field)-1, price, col)
                st.dataframe(data_field)
                data_deals[k] = data_field
                # st.dataframe(data_deals[k])
                
            st.text('Портфель')
            st.dataframe(sec_portfolio)
            st.text('Последние сделки')
            st.dataframe(sec_deals)

            # while last_time == last_time0:
            #     fields_df = pd.DataFrame(Ticker('SBER').candles(date=today_date, till_date=today_date, period=period))
            #     last_time = fields_df.at[len(fields_df)-1, 'end']
            time.sleep(60)
            if datetime.now().hour==0:
                st.stop()
        # st.rerun()


# st.dataframe(df)     
    # Спекулятивная стратегия trading end =======================
        

elif strategy == 'invest':
    st.title('Инвестиционная стратегия.')
    if exec_type == 'testing':
        st.subheader("Тестовые результаты расчета модели.")
        fields_path = './main/ml_pred.csv'
        
        data_ml_dict = sec_length_ml(fields_path, period='D')
        # st.write(data_ml_dict.keys())
        # st.write("=================data_ml_dict==============")
        # st.dataframe(list(data_ml_dict.keys()))
        sec_name_list = list(data_ml_dict.keys())
        for sec, sec_data in data_ml_dict.items():
            st.write(sec)
            # st.dataframe(data_ml_dict[sec])
            sec_data['open'] = sec_data['open'] / sec_data.at[0, 'open']
            sec_data['koef_pred'] = 1 - sec_data['koef']
            
            sec_data['open'] = sec_data['open'] - 1
            sec_data['koef_pred'] = sec_data['koef_pred'].cumsum(axis=0)
            
            sec_data = sec_data.set_index('begin')
            # st.dataframe(sec_data)
            st.write('Относительное изменение цены открытия "open" и предсказанного коэффициента "koef_pred"')
            st.line_chart(sec_data[['open', 'koef_pred']])
    elif exec_type == 'trading':     
        st.subheader("Предсказание модели.")
        fields_path = './main/ml_pred.csv'
        preds = pd.read_csv(fields_path)
        # st.write("=================preds==============")
        # st.dataframe(preds)
        preds_dict = preds.groupby('unique_id').groups
        secs_name_list = list(preds_dict.keys())
        
        # st.write(data_ml_dict.keys())
        for sec, sec_data in preds_dict.items():
            sec_data = preds.loc[sec_data,:]
            sec_data.drop('Unnamed: 0', axis=1, inplace=True)
            # st.wFrite(sec, sec_data)
            # st.dataframe(data_ml_dict[sec])
            sec_data['koef_pred'] = 1 - sec_data['koef']
            # st.write("=================sec_data==============0")
            # st.dataframe(sec_data)
            
            sec_data['open_preds'] = sec_data['koef_pred'].cumsum(axis=0)
            sec_data.index = pd.Index(range(len(sec_data)))
            
            # sec_data = sec_data.set_index('begin')
            # st.dataframe(sec_data)
            st.write('Прогноз относительного изменения цены открытия')
            st.line_chart(sec_data['open_preds'], y='open_preds')
            # st.write("Дни")

        
else:
    st.title('Cтратегия не выбрана.')
    

    


            
        
        
    
    

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



