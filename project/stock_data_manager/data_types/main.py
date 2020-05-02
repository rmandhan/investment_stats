from datetime import datetime
from typing import List

class Transaction():

    def __init__(self, trade_date: datetime, quantity: int, purchase_price: float):
        self.trade_date = trade_date
        self.quantity = quantity
        self.purchase_price = purchase_price

    def __str__(self):
        return 'Trade Date: {}, Quantity: {:<5s}, Purchase Price: {:<7s}'.format(self.trade_date, self.quantity, self.purchase_price)

class Position():

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

class DayQuote():

    def __init__(self, date: datetime, price: float):
        self.date = date
        self.price = price

    def __str__(self):
        return 'Date: {}, Price: {}'.format(self.date, self.price)

class Stock():

    def __init__(self, symbol: str, day_quotes=List[DayQuote]):
        self.symbol = symbol
        self.day_quotes = day_quotes

    def __str__(self):
        text_list = []
        text_list.append('Symbol: {}'.format(self.symbol))
        for day_quote in self.day_quotes:
            text_list.append(str(day_quote))
        text = '\n'.join(text_list)
        return text