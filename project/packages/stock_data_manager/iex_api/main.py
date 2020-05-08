import logging
import time

from typing import Tuple
from datetime import datetime, timedelta
from iexfinance.stocks import Stock as IEXClient
from data_types import *

METADATA_THRESHOLD=timedelta(days=7)
LATEST_THRESHOLD=timedelta(minutes=5)

class IEXAPI():

    def __init__(self, api_key_path: str):
        self.logger = logging.getLogger('StockDataManager.IEXAPI')
        self.key = self._fetch_key(file=api_key_path)
    
    def _fetch_key(self, file: str) -> str:
        self.logger.info('Fetching key from {}'.format(file))
        with open(file) as fp:
            line = fp.readline()
            return line.strip()

    def _should_sync_metadata(self, date: datetime) -> bool:
        threshold = datetime.now() - METADATA_THRESHOLD
        if date < threshold:
            return 1
        return 0

    def _should_sync_latest(self, date: datetime) -> bool:
        threshold = datetime.now() - LATEST_THRESHOLD
        if date < threshold:
            return 1
        return 0

    def update_metadata(self, symbol: str, metadata: StockMetaData) -> Tuple[StockMetaData, bool]:
        if metadata is not None and not self._should_sync_metadata(date=metadata.sync_date):
            self.logger.info('Metadata already up to date')
            return metadata, 0
        self.logger.info('Updating metadata')
        now = datetime.now()
        iex = IEXClient(symbols=symbol, token=self.key)
        c = iex.get_company()
        metadata = StockMetaData(symbol=symbol, sync_date=now, company_name=c['companyName'], security_name=c['securityName'], exchange=c['exchange'], industry=c['industry'], issue_type=c['issueType'], sector=c['sector'])
        self.logger.info('Successfully fetched latest metadata')
        return metadata, 1
    
    def update_latest(self, symbol: str, latest: StockLatest) -> Tuple[StockLatest, bool]:
        if latest is not None and not self._should_sync_latest(date=latest.sync_date):
            self.logger.info('Latest stock data already up to date')
            return latest, 0
        self.logger.info('Updating latest stock data')
        now = datetime.now()
        iex = IEXClient(symbols=symbol, token=self.key)
        q = iex.get_quote()
        # Sometimes latest quote information isn't available depending on the time you query
        if q['close'] is None:
            self.logger.info('Latest stock data currently unavailable')
            latest.sync_date = now
            return latest, 1
        date = datetime.fromtimestamp(q['latestUpdate']/1000)
        quote = Quote(date=date, high=q['high'], low=q['low'], open=q['open'], close=q['close'], volume=q['volume'])
        latest = StockLatest(sync_date=now, quote=quote)
        self.logger.info('Successfully fetched latest stock data')
        return latest, 1