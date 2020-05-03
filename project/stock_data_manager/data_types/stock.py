from datetime import datetime
from typing import List

class Quote():

    def __init__(self, date: datetime, high: float, low: float, open: float, close: float, volume: float, price: float):
        self.date = date
        self.high = high
        self.low = low
        self.open = open
        self.close = close
        self.volume = volume

    def __str__(self):
        return 'Date: {}, High: {:<6s}, Low: {:<6s}, Open: {:<6s}, Close: {:<6s}, Volume: {}'.format(self.date, self.high, self.low, self.open, self.close, self.volume)

class Stock():

    def __init__(self, symbol: str, company_name: str, industry: str, issue_type: str, latest_quote: Quote, day_quotes: List[Quote]):
        self.symbol = symbol
        self.company_name = company_name
        self.industry = industry
        self.issue_type = issuetype
        self.latest_quote = latest_quote
        self.day_quotes = day_quotes

    def __str__(self):
        text_list = []
        text_list.append('Symbol: {}, Company Name: {}, Industry: {}, Issue Type: {}'.format(self.symbol, self.company_name, self.industry, self.issue_type))
        text_list.append('Latest Quote:')
        text_list.append(str(self.latest_quote))
        text_list.append('Day Historical Quotes:')
        for day_quote in self.day_quotes:
            text_list.append(str(day_quote))
        text = '\n'.join(text_list)
        return text

### Used when reading stock files ###

class StockMetaData():

    def __init__(self, symbol: str, sync_date: datetime, company_name: str, security_name: str, exchange: str, industry: str, issue_type: str, sector: str):
        self.symbol = symbol
        self.sync_date = sync_date
        self.company_name = company_name
        self.security_name = security_name
        self.exchange = exchange
        self.industry = industry
        self.issue_type = issue_type
        self.sector = sector

class StockLatest():

    def __init__(self, sync_date: datetime, quote: Quote):
        self.sync_date = datetime
        self.quote = quote

class StockHistorical():

    def __init__(self, sync_date: datetime, earliest_date: datetime, latest_date: datetime, day_quotes: List[Quote]):
        self.sync_date = sync_date
        self.earliest_date = earliest_date
        self.latest_date = latest_date
        self.day_quotes = day_quotes
