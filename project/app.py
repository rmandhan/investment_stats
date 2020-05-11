import sys
import os
import dash

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'packages')))

from typing import List, Dict
from packages import data_types
from packages import stock_data_manager
from packages import stock_data_consumer

from datetime import datetime, timedelta

sdm = stock_data_manager.StockDataManager()
sdm._testing = True
sdc = stock_data_consumer.StockDataConsumer(all_symbols=[], stock_categories={}, index_tracker_stocks=[], 
                                            watchlist_stocks=[], position_stocks=[], positions=[])

def refresh_data() -> stock_data_consumer.StockDataConsumer:
    sdm.run()
    sdc = stock_data_consumer.StockDataConsumer(all_symbols=sdm.all_symbols, stock_categories=sdm.stock_categories, 
                                            index_tracker_stocks=sdm.index_tracker_stocks, watchlist_stocks=sdm.watchlist_stocks,
                                            position_stocks=sdm.position_stocks, positions=sdm.positions)
    return sdc

sdc = refresh_data()

# print('------- STOCK DF MAP -------')
# print(sdc.stock_df_map)
# print('------- POSITIONS DF -------')
# print(sdc.positions_df)
# print('------- PORTFOLIO START DATE -------')
# print(sdc.portfolio_start_date)
# print('------- MARKET DAYS -------')
# print(sdc.portfolio_market_days)
# print('------- PORTFOLIO INVESTED AMOUNT OVER TIME -------')
# print(sdc.portfolio_invested_amount_over_time())

# start_date = datetime.fromisoformat('2015-01-01').astimezone()
# end_date = datetime.now().astimezone()

# print('Invested Amount: {}'.format(sdc.calculate_invested_amount()))
# print('Market Value: {}'.format(sdc.calculate_market_value()))
# print('Unrealized Gain: {}'.format(sdc.calculate_unrealized_gain()))
# print('Realized Gain: {}'.format(sdc.realized_gain()))
# print('Values for Stock: {}'.format(sdc.values_for_stock(symbol='ARKK', start_date=start_date, end_date=end_date)))
# print('Percent Gain DateFrame: {}'.format(sdc.pct_gain_for_stock(symbol='ARKK', start_date=start_date, end_date=end_date)))
