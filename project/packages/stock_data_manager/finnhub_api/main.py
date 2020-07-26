import logging
import time
import json
import requests

from typing import Tuple
from datetime import datetime, timezone, timedelta
from data_types import *

LATEST_THRESHOLD=timedelta(minutes=5)

API_ENDPOINT='https://finnhub.io/api/v1/quote'
class FinnhubAPI():

    def __init__(self, api_key_path: str):
        self.logger = logging.getLogger('StockDataManager.FinnhubAPI')
        self.key = self._fetch_key(file=api_key_path)
    
    def _fetch_key(self, file: str) -> str:
        self.logger.info('Fetching key from {}'.format(file))
        with open(file) as fp:
            line = fp.readline()
            return line.strip()

    def _should_sync_latest(self, date: datetime) -> bool:
        threshold = datetime.now(timezone.utc).astimezone() - LATEST_THRESHOLD
        if date < threshold:
            return 1
        return 0
        return 1

    def _fetch_quote(self, symbol: str) -> Dict[str, str]:
        endpoint = '{}?symbol={}&token={}'.format( API_ENDPOINT, symbol, self.key)
        r = requests.get(endpoint)
        return r.json()
    
    def update_latest(self, symbol: str, latest: StockLatest) -> Tuple[StockLatest, bool]:
        if latest is not None and not self._should_sync_latest(date=latest.sync_date):
            self.logger.info('Latest stock data already up to date')
            return latest, 0
        self.logger.info('Updating latest stock data')
        now = datetime.now(timezone.utc).astimezone()
        q = self._fetch_quote(symbol=symbol)
        date = datetime.fromtimestamp(q['t']).astimezone(timezone.utc)
        quote = Quote(date=date, high=q['h'], low=q['l'], open=q['o'], close=q['c'], volume=0)
        latest = StockLatest(sync_date=now, quote=quote)
        self.logger.info('Successfully fetched latest stock data')
        return latest, 1