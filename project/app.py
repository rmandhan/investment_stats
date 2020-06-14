import sys
import os
import argparse

from typing import List, Dict
from datetime import datetime, timedelta

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'packages')))

from packages import data_types
from packages import stock_data_manager
from packages import stock_data_consumer

PRINT_OUTPUTS=False

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--testing', type=int, required=True,
                   help='Disable testing to use API to refresh Data')
parser.add_argument('-n', '--portfolio_name', type=str, required=False,
                   default='main', help='Portfolio Name')
args = parser.parse_args()

sdm = stock_data_manager.StockDataManager(portfolio_name=args.portfolio_name)
sdm._testing = bool(args.testing)
sdm.run()

sdc = stock_data_consumer.StockDataConsumer(all_symbols=sdm.all_symbols,
                                            stock_categories=sdm.stock_categories,
                                            category_allocations=sdm.category_allocations,
                                            index_tracker_stocks=sdm.index_tracker_stocks,
                                            watchlist_stocks=sdm.watchlist_stocks,
                                            portfolio_stocks=sdm.portfolio_stocks,
                                            positions=sdm.positions)
sdc.run()

portfolio_market_dates = sdc.portfolio_market_dates

portfolio_stock_stats = sdc.get_portfolio_stock_stats()
portfolio_aggregated_stats = sdc.get_portfolio_aggregate_stats()
portfolio_index_comparison_stats = sdc.get_portfolio_index_comparison_stats()
portfolio_stock_composition_stats = sdc.get_portfolio_stock_composition_stats()
portfolio_category_composition_stats = sdc.get_portfolio_category_composition_stats()

# Pick last date
date = portfolio_market_dates[len(portfolio_market_dates)-1]
allocation_solution = sdc.maximize_desired_allocation(date=date)

if PRINT_OUTPUTS:
    for k,v in portfolio_stock_stats.items():
        print('-------- PORTFOLIO STATS FOR {} --------'.format(k))
        sdc._print_df(v)
    print('-------- AGGREGATED PORTFOLIO STATS --------')
    sdc._print_df(portfolio_aggregated_stats)
    print('-------- PORTFOLIO INDEX COMPARISON STATS --------')
    sdc._print_df(portfolio_index_comparison_stats)
    for k,v in portfolio_stock_composition_stats.items():
        print('-------- PORTFOLIO STOCK COMPOSITION STATS FOR {} --------'.format(k))
        sdc._print_df(v)
    for k,v in portfolio_category_composition_stats.items():
        print('-------- PORTFOLIO CATEGORY COMPOSITION STATS FOR {} --------'.format(k))
        sdc._print_df(v)
    print('-------- ALLOCATION BREAK EVEN FOR {} --------'.format(date))
    sdc._print_df(allocation_solution)