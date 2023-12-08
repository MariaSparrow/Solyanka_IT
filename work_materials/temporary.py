# if st.sidebar.checkbox('Инвестиционная', value=invest_strategy, help=f"Только длинные позиции по инструментам. \
#                        \nНа один инструмент не более 1/{min_instrs_num} части активов. "):
#     invest_strategy = True
# else:
#     invest_strategy = False
    
# if st.sidebar.checkbox('Спекулятивная', value=spec_strategy, help=f"Длинные и короткие позиции по инструментам.\n \
#     На один инструмент не более 1/{min_instrs_num} части активов.\n \
#     При выборе одновременно двух стратегий на cпекулятивную стратегию\n \
#     используется 1/{min_instrs_num} части активов, на инвестиционную\n \
#     стратегию остальная часть активов."):
    
#     spec_strategy = True
# else:
#     spec_strategy = False

# while not spec_strategy and not invest_strategy:
#     st.sidebar.write('Для продолжения работы НЕОБХОДИМО выбрать стратегию.')
#     time.sleep(3)

help=f"Только длинные позиции по инструментам.\n \
                          На один инструмент не более 1/{min_instrs_num} части активов. "+ \
                          f"Длинные и короткие позиции по инструментам.\n \
                          На один инструмент не более 1/{min_instrs_num} части активов.\n"
                          
    # if os.path.exists(strategy_path):
    #     with open(strategy_path, "r") as f:
    #         strategy = f.readline()
    #         if strategy == 'spec':
    #             sell_pos = int(f.readline())
                          