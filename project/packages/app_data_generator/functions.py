import pandas as pd

from datetime import datetime
from typing import List, Dict
from data_types import *

# TODO: Add caching

class AppDataGenerator():

    def __init__(self, all_symbols: List[str], stock_categories: Dict[str, str], index_tracker_stocks: List[Stock], 
                 watchlist_stocks: List[Stock], position_stocks: List[Stock], positions: List[Position]):
        self.all_symbols = all_symbols
        self.stock_categories = stock_categories
        self.index_tracker_stocks = index_tracker_stocks
        self.watchlist_stocks = watchlist_stocks
        self.position_stocks = position_stocks
        self.positions = positions

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
        
    def pct_gain_for_stock(self, symbol: str, start_date: datetime, end_date: datetime):
        df = pd.DataFrame()
        stocks = self.position_stocks+self.watchlist_stocks+self.index_tracker_stocks
        for s in stocks:
            if s.symbol == symbol:
                df = s.df()
                df = df[(df[Quote._date_key] >= start_date) & (df[Quote._date_key] <= end_date)]
                x0 = df.iloc[0][Quote._close_key]
                df['pct_gain'] = df[Quote._close_key].apply(lambda x: ((x-x0)/x0)*100)
        return df
        