import pandas as pd

from datetime import datetime
from typing import List

class Transaction():

    _trade_date_key = 'trade_date'
    _quantity_key = 'quantity'
    _purchase_price_key = 'purchase_price'

    def __init__(self, trade_date: datetime, quantity: float, purchase_price: float):
        self.trade_date = trade_date
        self.quantity = quantity
        self.purchase_price = purchase_price

    def __str__(self):
        return 'Trade Date: {}, Quantity: {:<5s}, Purchase Price: {:<7s}'.format(self.trade_date, self.quantity, self.purchase_price)

class Position():

    _symbol_key = 'symbol'

    def __init__(self, symbol: str, transactions: List[Transaction]):
        self.symbol = symbol
        self.transactions = transactions

    def __str__(self):
        text_list = []
        text_list.append('Symbol: {}'.format(self.symbol))
        for trans in self.transactions:
            text_list.append(str(trans))
        text = '\n'.join(text_list)
        return text

    def df(self) -> pd.DataFrame:
        trade_dates, quantities, purchase_prices = [], [], []
        for t in self.transactions:
            trade_dates.append(t.trade_date)
            quantities.append(t.quantity)
            purchase_prices.append(t.purchase_price)
        data = { self._symbol_key: self.symbol,
                 Transaction._trade_date_key: trade_dates,
                 Transaction._quantity_key: quantities,
                 Transaction._purchase_price_key: purchase_prices }
        df = pd.DataFrame(data)
        return df