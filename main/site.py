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
        sec_deals = pd.DataFrame(columns=['Дата, Время', 'Инструмент', 'Объем сделки, лоты', 'Цена сделки, рублей'])

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

strategy = st.sidebar.radio('Выбор стратегии:', ['Инвестиционная', 'Спекулятивная'], key='strategy',
                            help="Инвестиционная стратегия использует машинное обучение временных рядов. На графиках \
                                отражается тенденция изменения цены инструмента в будущие периоды.\n \
                                Спекулятивная стратегия использует индексы по инструментам, сгруппированным \
                                по экономическим секторам. Инструмент с максимальным индексом в секторе - покупается, \
                                с минимальным - продается, по оставшимся инструментам позиция закрывается.",
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
        td = timedelta(days=2)
        start_day_dict[period] = (date.today() - timedelta(minutes=10000)).strftime("%Y-%m-%d")
    elif period == '10 минут':
        td = timedelta(days=2)
        period = '10m'
        start_day_dict[period] = (date.today() - timedelta(minutes=10000)).strftime("%Y-%m-%d")
    elif period == '1 час':
        td = timedelta(days=5)
        period = '1h'
        start_day_dict[period] = (date.today() - timedelta(hours=10000)).strftime("%Y-%m-%d")
    elif period == 'День':
        td = timedelta(days=first_index+1)
        period = '1D'
        start_day_dict[period] = (date.today() - timedelta(days=10000)).strftime("%Y-%m-%d")
    elif period == 'Неделя':
        td = timedelta(month=(first_index+2)//4)
        period = '1W'
        start_day_dict[period] = (date.today() - timedelta(weeks=1000)).strftime("%Y-%m-%d")
    else:
        td = timedelta(days=first_index+1)
        period = '1D'
        start_day_dict[period] = (date.today() - timedelta(days=10000)).strftime("%Y-%m-%d")

elif strategy == 'Инвестиционная':
    strategy = 'invest'
    period='1D'
    operation_text = "Прогноз"
    prognoz_text = 'Прогноз движения цен по выбранной стратегии'

buy_pos = 1

operation = st.sidebar.radio('Выбор операций:', ['Тестирование', operation_text],  key = 'operation',
                    captions = ['Вывод результатов теста по выбранной стратегии', prognoz_text], index=1)
init_fund = 0
if operation == 'Торговля':
    # operation = 'trade'
    exec_type = 'trading'
    init_fund, current_fund, min_instrs_num, sec_portfolio, sec_deals = load_portfolio(path_to_data="./main", 
                                                                                       strategy = 'invest', sell_pos = "")
elif operation == 'Прогноз':
    exec_type = 'trading'

elif operation == 'Тестирование':
    # operation = 'test'
    exec_type = 'testing'
        
if init_fund == 0:
    fund = st.sidebar.number_input("Сумма начального депозита, рублей", min_value=fund, max_value=10000000, key='fund', 
                                   placeholder="Введите сумму депозита...")
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
    
    # with st.sidebar:
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
    # st.sidebar.success('Биржевые данные загружены.')
    st.success('Биржевые данные загружены.')
    return data_dict

@st.cache_data(show_spinner=False)
def sec_length_ml(fields_path, period='D'):
    
    # with st.sidebar:
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
    # st.sidebar.success('Биржевые данные загружены.')
    st.success('Биржевые данные загружены.')
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

@st.cache_data()
def data_deals_table(data_dict):
    # st.write("314=================data_dict.keys()==============")
    # st.write(data_dict.keys())
    data_deals = {}
    secs_names = {}
    last_times = {}
    for k in data_dict.keys(): # k - сектор экономики
        data_deals[k] = pd.DataFrame(index=[0], columns=data_dict[k].columns)
        data_deals[k].loc[0,:] = 0
        data_deals[k].pop('begin')
        # st.dataframe(data_deals[k])
        secs_names[k] = list(data_deals[k].columns)
        # st.write(secs_names)
        for col in secs_names[k]:
            data_deals[k][col+'_pos'] = 0
            data_deals[k][col+'_res'] = 0
            data_deals[k][col+'_deal'] = 0
            last_times['time'+k+col] = datetime.now().strftime("%d/%m/%y %H:%M:%S")
        # st.write("330=================data_deals==============")
        # st.write("Сектор экономики: ", k)
        # st.dataframe(data_deals[k])
    return data_deals, secs_names, last_times

#=========== Starts Portfolio investigation ===============

if strategy == 'spec':
    st.title('Спекулятивная стратегия.')
    if sell_pos == -1:
        st.text('Стратегия включает короткие продажи')
    else:
        st.text('Стратегия включает только длинные позиции')
    # Спекулятивная стратегия testing start =======================
    if exec_type == 'testing':
        data_dict = sec_length(fields_path, period)
        st.subheader("Тестовые результаты расчета модели.")

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
            st.text("Доход (в долях от депозита) на 1 инструмент,\nусредненный по всем инструментам\n в секторе.")
            
            data_field.index = date_col
            
            st.line_chart(data_field['res']/len(df.columns))

            # st.write(len(data_field), len(df))

            # st.dataframe(data_field)   
    # Спекулятивная стратегия testing end =======================
    
    # Спекулятивная стратегия trading start =======================
    elif exec_type == 'trading':     
        st.title('Раздел Торговля находится в разработке')
        # if  "data_dict" in st.session_state:
        #     data_dict = st.session_state['data_dict']
        # else:
        data_dict = sec_length(fields_path, period) # словарь формата : {сектор:[DataFrame(), ...]}
        # st.session_state['data_dict'] = data_dict
        data_deals, secs_names, last_times = data_deals_table(data_dict)
        # st.write("399=================data_deals==============")
        # st.write(data_deals, secs_names, last_times)
        
        if  "data_deals" in st.session_state:
            data_deals = st.session_state['data_deals']
        else:
            st.session_state['data_deals'] = data_deals
            
        if  "last_times" in st.session_state:
            last_times = st.session_state['last_times']
        else:
            st.session_state['last_times'] = last_times
            
        if  "sec_deals" in st.session_state:
            sec_deals = st.session_state['sec_deals']
        else:
            st.session_state['sec_deals'] = sec_deals
            
        # st.write("383=================data_dict['ИТ']==============")
        # st.dataframe(data_dict['ИТ'])
        # st.write("383=================data_deals==============")
        # st.dataframe(data_deals['ИТ'])

        # fields_df = pd.DataFrame(Ticker('SBER').candles(date=start_day_dict[period], till_date=today_date, period=period))
        # st.write("3=================fields_df==============")
        # st.dataframe(fields_df)
        
        # last_time0 = fields_df.at[len(fields_df)-1, 'end']
        # last_time0 = last_time
        
        for k in data_dict.keys():
            # st.write("Сектор экономики: ", k)
            # st.write("424=================data_deals==============")
            # st.dataframe(data_deals[k])
            df = data_dict[k].loc[len(data_dict[k])-first_index-2:,:]
            # st.write("434=================df==============")
            # st.dataframe(df)
            date_col = df.pop('begin')
            # Расчет индексов по бумагам
            next_row = len(data_deals[k])
            # st.write("439=================secs_names[k]==============")
            # st.write(secs_names[k])
            for col in secs_names[k]:
                mx = df.loc[df.index[-first_index]:df.index[-1],col].max()
                mn = df.loc[df.index[-first_index]:df.index[-1],col].min()
                # st.write("=================mx mn==============")
                # st.write(mn, mx)
                if mx == mn:
                    cidx = 0
                else:
                    cidx = (df.at[df.index[-1],col] - mn) / (mx - mn) - 1
                data_deals[k].at[next_row,col] = cidx 
                # st.write(data_field)

            # st.write("453=================data_deals[k]==============")
            # st.dataframe(data_deals[k])
            # st.write("Индексы инструментов")
            # st.line_chart(data_field.loc[:,:])
            # st.dataframe(data_field.head()) 
            # Выбор бумаг с минимальным и максимальным индексами
            min_idx = data_deals[k].loc[:,df.columns].idxmin(axis=1,skipna=True)
            max_idx = data_deals[k].loc[:,df.columns].idxmax(axis=1,skipna=True)
            # st.write("=================max_idx==============")
            # st.dataframe(max_idx)

            # st.write("=================min_idx==============")
            # st.dataframe(min_idx)
            
            data_deals[k].loc[:,'min_idx'] = min_idx
            data_deals[k].loc[:,'max_idx'] = max_idx
            # st.write("=================data_field==============")
            # st.dataframe(data_field)
            # res_columns = []
            # st.write("471=================data_deals[k]==============")
            # st.write(data_deals[k])
            for col in secs_names[k]:
                # res_columns.append(col+'_res')
                price_df = pd.DataFrame(Ticker(col).candles(date=(date.today() - td).strftime("%Y-%m-%d"), 
                                                            till_date=today_date, period=period))
                # st.write("477=================price_df==============")
                # st.write(col)
                # st.dataframe(price_df)
                if price_df.empty:
                    continue
                if price_df.at[price_df.index[-1],'begin'] != st.session_state['last_times']['time'+k+col]:
                    st.session_state['last_times']['time'+k+col] = price_df.at[price_df.index[-1],'begin']
                    price = price_df.at[price_df.index[-1],'open']
                    # st.write("483=================data_deals[k]==============")
                    # st.write(data_deals[k])
                    data_deals[k] = take_deal(data_deals[k], data_deals[k].index[-1], price, col)
                    st.write("488=================data_deals[k]==============")
                    st.write(data_deals[k])
                    #sec_deals ['Дата, Время', 'Инструмент', 'Объем сделки, лоты', 'Цена сделки, рублей']
                    last_index = data_deals[k].index[-1]
                    index_2 = data_deals[k].index[-2]
                    lidx = len(sec_deals)
                    if data_deals[k].at[last_index,col+'_deal'] != data_deals[k].at[index_2,col+'_deal']:
                        sec_deals.at[lidx,'Дата, Время'] = price_df.at[price_df.index[-1],'begin']
                        sec_deals.at[lidx,'Инструмент'] = col
                        
                        st.write("492=================data_deals[k].at[last_index,col+'_deal']  index_2==============")
                        st.write(data_deals[k].at[last_index,col+'_deal'])
                        st.write(data_deals[k].at[index_2,col+'_deal'])
                        sec_deals.at[lidx,'Объем сделки, лоты'] = data_deals[k].at[last_index,col+'_deal'] - data_deals[k].at[index_2,col+'_deal']
                        sec_deals.at[lidx,'Цена сделки, рублей'] = price
                    
            # st.dataframe(data_deals[k])
            
            # st.write("493=================data_deals[k]==============")
            # st.dataframe(data_deals[k])
                
        st.text('Портфель')
        st.dataframe(sec_portfolio)
        
        st.text('Последние сделки')
        st.dataframe(sec_deals)

            # while last_time == last_time0:
            #     fields_df = pd.DataFrame(Ticker('SBER').candles(date=today_date, till_date=today_date, period=period))
            #     last_time = fields_df.at[len(fields_df)-1, 'end']
        st.text(datetime.now().strftime("%d/%m/%y %H:%M:%S"))
        st.session_state['data_deals'] = data_deals
        st.session_state['sec_deals'] = sec_deals
        time.sleep(60)

        if datetime.now().hour==0:
            st.stop()
        st.rerun()


# st.dataframe(df)     
    # Спекулятивная стратегия trading end =======================
        

elif strategy == 'invest':
    st.title('Инвестиционная стратегия.')
    if exec_type == 'testing':
        fields_path = st.file_uploader("Выбор файла для теста.")
        if fields_path == None:
            fields_path = './main/ml_pred.csv'
        data_ml_dict = sec_length_ml(fields_path, period='D')
        st.subheader("Тестовые результаты расчета модели.")
        
        # st.write(data_ml_dict.keys())
        # st.write("=================data_ml_dict==============")
        # st.dataframe(data_ml_dict['AKRN'])
        sec_name_list = list(data_ml_dict.keys())
        for sec, sec_data in data_ml_dict.items():
            st.write('Инструмент: ',sec)
            # st.dataframe(data_ml_dict[sec])
            # sec_data['open'] = sec_data['open'] / sec_data.at[0, 'open']
            sec_data['open'] = (sec_data['open'] - sec_data['open'].min()) / (sec_data['open'].max() - sec_data['open'].min())
            sec_data['koef_pred'] = 1 - sec_data['koef']
            # st.dataframe(sec_data)
            
            sec_data['open'] = (sec_data['open'] - 1)
            sec_data['koef_pred'] = sec_data['koef_pred'].cumsum(axis=0)
            sec_data['koef_pred'] = (sec_data['koef_pred'] - sec_data['koef_pred'].min()) / (sec_data['koef_pred'].max() - sec_data['koef_pred'].min())
            # st.dataframe(sec_data)
            # (sec_data['koef_pred'].cumsum(axis=0).max() - sec_data['koef_pred'].cumsum(axis=0).min()) 
            sec_data = sec_data.set_index('begin')
            # st.dataframe(sec_data)
            st.write('Относительное изменение цены открытия "open" и предсказанного коэффициента "koef_pred"')
            st.line_chart(sec_data[['open', 'koef_pred']])
    elif exec_type == 'trading':     
        fields_path = st.file_uploader("Выбор файла для прогноза.")
        if fields_path == None:
            fields_path = './main/preds.csv'
        first_forcast_date = st.date_input("Введите дату, с которой начинается прогноз", value='today', format="YYYY-MM-DD")
        st.subheader("Предсказание модели.")
        preds = pd.read_csv(fields_path)
        preds = preds[preds['ds']>=first_forcast_date.strftime("%Y-%m-%d")]
        # st.write("=================preds==============")
        # st.dataframe(preds)
        
        preds_dict = preds.groupby('unique_id').groups
        secs_name_list = list(preds_dict.keys())
        
        # data_ml_dict = sec_length_ml(fields_path, period='D')
        # st.write(data_ml_dict.keys())
        for sec, sec_data in preds_dict.items():
            st.write('Инструмент: ',sec)
            sec_data = preds.loc[sec_data,:]
            sec_data.drop('Unnamed: 0', axis=1, inplace=True)
            # st.wFrite(sec, sec_data)
            # st.dataframe(data_ml_dict[sec])
            sec_data['koef_pred'] = 1 - sec_data['koef']
            # st.write("=================sec_data==============0")
            # st.dataframe(sec_data)
            
            sec_data['open_preds'] = sec_data['koef_pred'].cumsum(axis=0)
            sec_data['open_preds'] = (sec_data['open_preds'] - sec_data['open_preds'].min()) / (sec_data['open_preds'].max() - sec_data['open_preds'].min())
            sec_data['open_preds'] = sec_data['open_preds'] - sec_data.at[sec_data.index[0], 'open_preds']
            
            sec_data.index = pd.Index(sec_data['ds'])
            
            sec_df = pd.DataFrame(Ticker(sec).candles(date=first_forcast_date.strftime("%Y-%m-%d"), till_date=today_date, period='1D'))
            sec_df.index = pd.Index(map(lambda x: str(x).split(' ')[0], sec_df['begin']))
            sec_df['open'] = (sec_df['open'] - sec_df['open'].min()) / (sec_df['open'].max() - sec_df['open'].min())
            sec_df['open'] = sec_df['open'] - sec_df.at[sec_df.index[0], 'open']
            # st.dataframe(sec_df)
            
            # sec_data = sec_data.set_index('begin')
            # st.dataframe(sec_data)
            sec_data = pd.concat([sec_data, sec_df], axis=1)
            st.write(f'Прогноз относительного изменения цены открытия, начиная с даты {first_forcast_date.strftime("%Y-%m-%d")}')
            chrt_dat = sec_data.loc[:,['open','open_preds']]
            # st.dataframe(sec_data)
            st.line_chart(chrt_dat)
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



