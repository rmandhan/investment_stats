import logging
import tiingo

from datetime import datetime, timezone, timedelta
from tiingo import TiingoClient
from typing import Tuple
from data_types import *

# Tiingo provides at max 5 year old historical data (for free)
START_DATE='2015-01-01'

# Tiingo API only provides EOD historical data

class TiingoAPI():

    def __init__(self, api_key_path: str):
        self.logger = logging.getLogger('StockDataManager.TiingoAPI')
        self.key = self._fetch_key(file=api_key_path)
    
    def _fetch_key(self, file: str) -> str:
        self.logger.info('Fetching key from {}'.format(file))
        with open(file) as fp:
            line = fp.readline()
            return line.strip()

    def _should_sync_historical(self, date: datetime) -> bool:
        if datetime.now(timezone.utc).astimezone().date() == date.date():
            return 0
        return 1

    def update_historical(self, symbol: str, historical: StockHistorical) -> Tuple[StockHistorical, bool]:
        if historical is not None and not self._should_sync_historical(date=historical.sync_date):
            self.logger.info('Historical stock data already up to date')
            return historical, 0
        else:
            self.logger.info('Updating historical stock data')

        update_in_place = historical is not None
        if update_in_place:
            self.logger.info('Will update historical stock data in-place')
        else:
            self.logger.info('Will fetch max(5 years, inception date) historical data')

        start_date = historical.latest_date + timedelta(days=1) if update_in_place else START_DATE
        now = datetime.now(timezone.utc).astimezone()
        tiingo = TiingoClient(config={'api_key': self.key})
        h_data = tiingo.get_ticker_price(ticker=symbol, startDate=start_date)

        if len(h_data) is 0:
            self.logger.info('No new historical data found after : {}'.format(historical.latest_date))
            historical.sync_date = now
            return historical, 1

        quotes = []
        for q in h_data:
            quote = Quote(date=datetime.fromisoformat(q['date'].replace('Z', '+00:00')), high=q['high'], low=q['low'], open=q['open'], close=q['close'], volume=q['volume'])
            quotes.append(quote)

        earliest_date = historical.day_quotes[0].date if update_in_place else quotes[0].date
        latest_date = quotes[len(quotes)-1].date

        if update_in_place:
            historical.sync_date = now
            historical.earliest_date = earliest_date
            historical.latest_date = latest_date
            historical.day_quotes = historical.day_quotes+quotes
        else:
            historical = StockHistorical(sync_date=now, earliest_date=earliest_date, latest_date=latest_date, day_quotes=quotes)

        self.logger.info('Successfully fetched historical stock data')

        return historical, 1
