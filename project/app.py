import sys
import os

from typing import List, Dict
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'packages')))

from packages import data_types
from packages import stock_data_manager
from packages import stock_data_consumer

sdm = stock_data_manager.StockDataManager()
sdm._testing = True
sdm.run()

sdc = stock_data_consumer.StockDataConsumer(all_symbols=sdm.all_symbols, stock_categories=sdm.stock_categories, 
                                        index_tracker_stocks=sdm.index_tracker_stocks, watchlist_stocks=sdm.watchlist_stocks,
                                        portfolio_stocks=sdm.portfolio_stocks, positions=sdm.positions)
sdc.run()

portfolio_stock_stats = sdc.get_portfolio_stock_stats()
portfolio_aggregated_stats = sdc.get_portfolio_aggregate_stats()

for k,v in portfolio_stock_stats.items():
    print('-------- PORTFOLIO STATS FOR {} --------'.format(k))
    print(sdc._print_df(v))

print('-------- AGGREGATED PORTFOLIO STATS --------')
print(sdc._print_df(portfolio_aggregated_stats))