import sys
import json
import pandas as pd

from datetime import date
from datetime import datetime
from typing import List, Dict

class DataEncoder(json.JSONEncoder):

    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif '__dict__' in dir(o):
            return o.__dict__
        return super().default(o)

class DataDecoder():

    def object_hook(dict):
        class_name = dict['_class']
        class_ = getattr(sys.modules[__name__], class_name)
        return class_.toObject(dict)

class Quote():

    _date_key = 'date'
    _high_key = 'high'
    _low_key = 'low'
    _open_key = 'open'
    _close_key = 'close'
    _volume_key = 'volume'

    def __init__(self, date: datetime, high: float, low: float, open: float, close: float, volume: float):
        self._class = self.__class__.__name__
        self.date = date
        self.high = high
        self.low = low
        self.open = open
        self.close = close
        self.volume = volume

    def __str__(self):
        return 'Date: {}, High: {:<6f}, Low: {:<6f}, Open: {:<6f}, Close: {:<6f}, Volume: {}'.format(self.date, self.high, self.low, self.open, self.close, self.volume)

    def toObject(dict):
        return Quote(date=datetime.fromisoformat(dict[Quote._date_key]), high=dict[Quote._high_key], low=dict[Quote._low_key], open=dict[Quote._open_key], close=dict[Quote._close_key], volume=dict[Quote._volume_key])

class Stock():

    _symbol_key = 'symbol'
    _company_name_key = 'company_name'
    _industry_key = 'industry'
    _issue_type_key = 'issue_type'

    def __init__(self, symbol: str, company_name: str, industry: str, issue_type: str, latest_quote: Quote, day_quotes: List[Quote]):
        self._class = self.__class__.__name__
        self.symbol = symbol
        self.company_name = company_name
        self.industry = industry
        self.issue_type = issue_type
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

    def df(self) -> pd.DataFrame:
        date_a, high_a, low_a, open_a, close_a, volume_a = [], [], [], [], [], []
        all_quotes = self.day_quotes+[self.latest_quote]
        for q in all_quotes:
            date_a.append(q.date)
            high_a.append(q.high)
            low_a.append(q.low)
            open_a.append(q.open)
            close_a.append(q.close)
            volume_a.append(q.volume)
        data = { self._symbol_key: self.symbol,
                 self._company_name_key: self.company_name,
                 self._industry_key: self.industry,
                 self._issue_type_key: self.issue_type,
                 Quote._date_key: date_a,
                 Quote._high_key: high_a,
                 Quote._low_key: low_a,
                 Quote._open_key: open_a,
                 Quote._close_key: close_a,
                 Quote._volume_key: volume_a }
        df = pd.DataFrame(data)
        return df

### Data models for reading/writing stock data ####

class StockMetaData():

    def __init__(self, symbol: str, sync_date: datetime, company_name: str, security_name: str, exchange: str, industry: str, issue_type: str, sector: str):
        self._class = self.__class__.__name__
        self.symbol = symbol
        self.sync_date = sync_date
        self.company_name = company_name
        self.security_name = security_name
        self.exchange = exchange
        self.industry = industry
        self.issue_type = issue_type
        self.sector = sector

    def toJSON(self):
        return json.dumps(self, cls=DataEncoder, sort_keys=True, indent=4)

    def toObject(dict):
        return StockMetaData(symbol=dict['symbol'], sync_date=datetime.fromisoformat(dict['sync_date']), company_name=dict['company_name'], security_name=dict['security_name'], exchange=dict['exchange'], industry=dict['industry'], issue_type=dict['issue_type'], sector=dict['sector'])

class StockLatest():

    def __init__(self, sync_date: datetime, quote: Quote):
        self._class = self.__class__.__name__
        self.sync_date = sync_date
        self.quote = quote

    def toJSON(self):
        return json.dumps(self, cls=DataEncoder, sort_keys=True, indent=4)

    def toObject(dict):
        return StockLatest(sync_date=datetime.fromisoformat(dict['sync_date']), quote=dict['quote'])

class StockHistorical():

    def __init__(self, sync_date: datetime, earliest_date: datetime, latest_date: datetime, day_quotes: List[Quote]):
        self._class = self.__class__.__name__
        self.sync_date = sync_date
        self.earliest_date = earliest_date
        self.latest_date = latest_date
        self.day_quotes = day_quotes

    def toJSON(self):
        return json.dumps(self, cls=DataEncoder, sort_keys=True, indent=4)
    
    def toObject(dict):
        return StockHistorical(sync_date=datetime.fromisoformat(dict['sync_date']), earliest_date=datetime.fromisoformat(dict['earliest_date']), latest_date=datetime.fromisoformat(dict['latest_date']), day_quotes=dict['day_quotes'])