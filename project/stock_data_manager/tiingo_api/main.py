import logging
import tiingo

from typing import Tuple
from ..data_types import *

class TiingoAPI():

    def __init__(self, api_key_path: str):
        self.logger = logging.getLogger('StockDataManager.TiingoAPI')
        self.key = self._fetch_key(file=api_key_path)
    
    def _fetch_key(self, file: str) -> str:
        self.logger.info('Fetching key from {}'.format(file))
        with open(file) as fp:
            line = fp.readline()
            return line.strip()
    
    def update_historical(self, historical: StockHistorical) -> Tuple[StockHistorical, bool]:
        return historical, 0
