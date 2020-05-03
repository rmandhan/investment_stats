import logging

from ..data_types import *

class DataStore():

    def __init__(self, data_dir: str):
        self.logger = logging.getLogger('StockDataManager.DataStore')
        self.data_dir = data_dir

    def _file_exists(self, file: str):
        return 0

    def _create_dir(self, dir: dir):
        return 0
    
    def _get_stock_metadata_fp(self, symbol: str):
        return 0

    def _get_stock_latest_fp(self, symbol: str):
        return 0

    def _get_stock_historical_fp(self, symbol: str):
        return 0

    def read_stock_metadata(self, symbol: str) -> StockMetaData:
        return 0

    def read_stock_latest(self, symbol: str) -> StockLatest:
        return 0

    # For now, historical means day data
    def read_stock_historical(self, symbol: str) -> StockHistorical:
        return 0

    def write_stock_metadata(self, symbol: str, metadata: StockMetaData):
        return 0
        
    def write_stock_latest(self, symbol: str, latest: StockLatest):
        return 0
    
    def write_stock_historical(self, symbol: str, historical: StockHistorical):
        return 0