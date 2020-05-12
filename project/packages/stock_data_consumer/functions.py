import pandas as pd
import pytz

from datetime import datetime, timezone
from typing import List, Dict
from data_types import *

MIN_DATETIME = datetime(year=1, month=1, day=1, tzinfo=timezone.utc)
MAX_DATETIME = datetime(year=9999, month=12, day=31, tzinfo=timezone.utc)

# Pre-defined Data Keys
SYMBOL_KEY = Stock._symbol_key
COMPANY_NAME_KEY = Stock._company_name_key
INDUSTRY_KEY = Stock._industry_key
ISSUE_TYPE_KEY = Stock._issue_type_key
DATE_KEY = Quote._date_key
HIGH_KEY = Quote._high_key
LOW_KEY = Quote._low_key
OPEN_KEY = Quote._open_key
CLOSE_KEY = Quote._close_key
VOLUME_KEY = Quote._volume_key
TRADE_TRADE_KEY = Transaction._trade_date_key
QUANTITY_KEY = Transaction._quantity_key
PURCHASE_PRICE_KEY = Transaction._purchase_price_key
# New Data Keys
VALUE_KEY = 'value'

class StockDataConsumer():

    def __init__(self, all_symbols: List[str], stock_categories: Dict[str, str], index_tracker_stocks: List[Stock], watchlist_stocks: List[Stock], position_stocks: List[Stock], positions: List[Position]):
        self.all_symbols = all_symbols
        self.stock_categories = stock_categories
        self.index_tracker_stocks = index_tracker_stocks
        self.watchlist_stocks = watchlist_stocks
        self.position_stocks = position_stocks
        self.positions = positions
        if len(self.position_stocks+self.watchlist_stocks+self.index_tracker_stocks) > 0 and len(self.positions) > 0:
            self._derive_data()

    def _derive_data(self):
        stock_df_map = {}
        positions_df = pd.DataFrame()
        portfolio_start_date = None
        portfolio_market_days = []
        # Get stock dfs for all stocks
        stocks = self.position_stocks+self.watchlist_stocks+self.index_tracker_stocks
        for s in stocks:
            stock_df_map[s.symbol] = s.df()
        p_dfs = []
        # Put all positions into a df
        for p in self.positions:
            p_dfs.append(p.df())
        positions_df = pd.concat(p_dfs)
        positions_df.sort_values(by=[TRADE_TRADE_KEY], inplace=True)
        # Get the date of first trade from portfolio
        portfolio_start_date = positions_df[TRADE_TRADE_KEY].min().to_pydatetime()
        # Derive market days from portfolio_start_date based on stock historical data
        earliest_date = portfolio_start_date
        stock_to_use: Stock
        for s in stocks:
            # Use any stock that has data since portfolio_start_date
            if s.day_quotes[0].date < portfolio_start_date:
                stock_to_use = s
                break
        for q in stock_to_use.day_quotes:
            if q.date >= portfolio_start_date:
                portfolio_market_days.append(q.date)
        # Update class variables
        self.stock_df_map = stock_df_map
        self.positions_df = positions_df
        self.portfolio_start_date = portfolio_start_date
        self.portfolio_market_days = portfolio_market_days

    def _print_df(self, df: pd.DataFrame):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df)

    def portfolio_invested_amount_over_time(self):
        final_df = pd.DataFrame()
        invested_amount = []
        stock_r_average = {}
        stock_r_quantity = {}
        index = 0
        total_trades = self.positions_df.shape[0]
        # Iterate over market days and keep track of stock quantity & average cost ever day
        for day in self.portfolio_market_days:
            invested_amount.append(0)
            new_trades_found = False
            while index < total_trades:
                trade = self.positions_df.iloc[index]
                trade_date = trade[TRADE_TRADE_KEY]
                if trade_date > day:
                    break
                trade_symbol = trade[SYMBOL_KEY]
                trade_quantity = trade[QUANTITY_KEY]
                trade_purchase_price = trade[PURCHASE_PRICE_KEY]
                if trade_symbol not in stock_r_average:
                    # Initialize dictionary
                    stock_r_quantity[trade_symbol] = 0
                    stock_r_average[trade_symbol] = 0
                r_quantity = stock_r_quantity[trade_symbol]
                r_average = stock_r_average[trade_symbol]
                if trade_quantity > 0:
                    r_average = ((r_average*r_quantity)+(trade_quantity*trade_purchase_price))/(r_quantity+trade_quantity)
                r_quantity += trade_quantity
                stock_r_quantity[trade_symbol] += trade_quantity
                stock_r_average[trade_symbol] = r_average 
                new_trades_found = True
                index += 1
            # Calculate the investment amount for that day
            if new_trades_found:
                for k in stock_r_average.keys():
                    invested_amount[len(invested_amount)-1] += stock_r_quantity[k]*stock_r_average[k]
            else:
                invested_amount[len(invested_amount)-1] = invested_amount[len(invested_amount)-2]
        # Create final data frame
        data = { DATE_KEY: self.portfolio_market_days, 
                 VALUE_KEY: invested_amount }
        final_df = pd.DataFrame(data)
        return final_df
            
    def calculate_market_value(self) -> float:
        result = 0
        quantities = {}
        for p in self.positions:
            quantities[p.symbol] = 0
            for t in p.transactions:
                # Quantities should never add to a negative number
                quantities[p.symbol] += t.quantity
        for ps in self.position_stocks:
            latest = ps.latest_quote
            result += quantities[ps.symbol]*latest.close
        return result
    
    def calculate_invested_amount(self) -> float:
        result = 0
        for p in self.positions:
            r_quantity = 0
            r_average = 0
            for t in p.transactions:
                if t.quantity > 0:
                    r_average = ((r_average*r_quantity)+(t.quantity*t.purchase_price))/(r_quantity+t.quantity)
                r_quantity += t.quantity
            result += r_quantity*r_average
        return result

    def calculate_unrealized_gain(self) -> (float, float):
        gain, pct = 0, 0
        inv_amount = self.calculate_invested_amount()
        if inv_amount is 0: return gain, pct
        mkt_value = self.calculate_market_value()
        gain = mkt_value-inv_amount
        pct = ((mkt_value-inv_amount)/inv_amount)*100
        return gain, pct

    def realized_gain(self) -> (float, float):
        gain, pct = 0, 0
        for p in self.positions:
            r_quantity = 0
            r_average = 0
            for t in p.transactions:
                if t.quantity > 0:
                    r_average = ((r_average*r_quantity)+(t.quantity*t.purchase_price))/(r_quantity+t.quantity)
                else:
                    gain += (t.purchase_price-r_average)*t.quantity*-1
                r_quantity += t.quantity
        pct = (gain/self.calculate_invested_amount())*100
        return gain, pct
    
    def values_for_stock(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        df = pd.DataFrame()
        stocks = self.position_stocks+self.watchlist_stocks+self.index_tracker_stocks
        for s in stocks:
            if s.symbol == symbol:
                df = s.df()
                df = df[(df[Quote._date_key] >= start_date) & (df[Quote._date_key] <= end_date)]
        return df
        
    def pct_gain_for_stock(self, symbol: str, start_date: datetime, end_date: datetime) -> pd.DataFrame:
        df = pd.DataFrame()
        stocks = self.position_stocks+self.watchlist_stocks+self.index_tracker_stocks
        for s in stocks:
            if s.symbol == symbol:
                df = s.df()
                df = df[(df[Quote._date_key] >= start_date) & (df[Quote._date_key] <= end_date)]
                x0 = df.iloc[0][Quote._close_key]
                df['pct_gain'] = df[Quote._close_key].apply(lambda x: ((x-x0)/x0)*100)
        return df

    # def portfolio_invested_amount(self) -> pd.DataFrame:
    #     final_df = pd.DataFrame()
    #     time_array = []
    #     value_array = []
    #     tmp_dfs = []
    #     for p in self.positions:
    #         tmp_dfs.append(p.df())
    #     pos_df = pd.concat(tmp_dfs, ignore_index=True)
    #     # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #         # print(pos_df)
    #     pos_df.sort_values(by=[Transaction._trade_date_key], inplace=True)
    #     # with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    #     #     print(pos_df)
    #     earliest_date = pytz.utc.localize(pos_df.iloc[0][Transaction._trade_date_key])
    #     # print(earliest_date)
    #     iter_quotes = self.position_stocks[0].day_quotes
    #     # for q in iter_quotes:
    #     #     print(q.date)
    #     i = len(iter_quotes)-1
    #     while i >= 0:
    #         if iter_quotes[i].date == earliest_date:
    #             break
    #         i -= 1
    #     running_index = 0
    #     total_trades = pos_df.shape[0]
    #     cumulative_invested = 0
    #     r_quantity_dict = {}
    #     r_average_dict = {}
    #     for x in range(i, len(iter_quotes)):
    #         # print(iter_quotes[x].date)
    #         time_array.append(iter_quotes[x].date)
    #         pos_date = pytz.utc.localize(pos_df.iloc[running_index][Transaction._trade_date_key])
    #         print(pos_date)
    #         print(iter_quotes[x].date)
    #         if pos_date >= iter_quotes[x].date:
    #             while running_index < total_trades:
    #                 pos_date = pytz.utc.localize(pos_df.iloc[running_index][Transaction._trade_date_key])
    #                 if pos_date > iter_quotes[x].date:
    #                     break
    #                 quantity = pos_df.iloc[running_index][Transaction._quantity_key]
    #                 purchase_price = pos_df.iloc[running_index][Transaction._purchase_price_key]
    #                 symbol = pos_df.iloc[running_index][Position._symbol_key]
    #                 r_quantity = 0
    #                 r_average = 0
    #                 if symbol in r_quantity_dict:
    #                     r_quantity = r_quantity_dict[symbol]
    #                 if symbol in r_average_dict:
    #                     r_average = r_average_dict[symbol] 
    #                 if quantity > 0:
    #                     r_average = ((r_average*r_quantity)+(quantity*purchase_price))/(r_quantity+quantity)
    #                 r_quantity += quantity
    #                 cumulative_invested += r_quantity*r_average
    #                 r_quantity_dict[symbol] = r_quantity
    #                 r_average_dict[symbol] = r_average
    #                 running_index += 1
    #         value_array.append(cumulative_invested)
    #         print(cumulative_invested)
    #     return final_df

    # def portfolio_market_value(self) -> pd.DataFrame:
    #     final_df = pd.DataFrame()
    #     return final_df

    # def portfolio_unrealized_gains(self) -> pd.DataFrame:
    #     final_df = pd.DataFrame()
    #     return final_df

    # def portfolio_realized_gains(self) -> pd.DataFrame:
    #     final_df = pd.DataFrame()
    #     return final_df

    # def portfolio_total_gains(self) -> pd.DataFrame:
    #     final_df = pd.DataFrame()
    #     return final_df

    