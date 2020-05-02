from datetime import datetime
from typing import List

class Transaction():

    def __init__(self, trade_date: datetime, quantity: int, purchase_price: float):
        self.trade_date = trade_date
        self.quantity = quantity
        self.purchase_price = purchase_price

class Position():

    def __init__(self, symbol: str, transactions: List[Transaction]):
        self.symbol = symbol
        self.transactions = transactions

    def pretty_print(self):
        print('Symbol: {}'.format(self.symbol))
        for trans in self.transactions:
            print('Trade Date: {}, Quantity: {:<5s}, Purchase Price: {:<7s}'.format(trans.trade_date, trans.quantity, trans.purchase_price))

class DayQuote():

    def __init__(self, date: datetime, price: float):
        self.date = date
        self.price = price

class Stock():

    def __init__(self, symbol: str, day_quotes=List[DayQuote]):
        self.symbol = Symbol
        self.day_quotes = day_quotes

    def pretty_print(self):
        print('Symbol: {}'.format(self.symbol))
        for day_quote in self.day_quotes:
            print('Date: {}, Price: {}'.format(day_quote.date, day_quote.price))