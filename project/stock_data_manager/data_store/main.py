import os
import logging
import json

from typing import Dict
from ..data_types import *

class DataStore():

    def __init__(self, data_dir: str):
        self.logger = logging.getLogger('StockDataManager.DataStore')
        self.data_dir = data_dir
        self.__validate_dir()

    def __validate_dir(self):
        if not os.path.exists(self.data_dir):
            self.logger.error("{} data directory doesn't exist".format(self.data_dir))
            raise FileNotFoundError('Data directory not found')

    def _file_exists(self, file: str) -> bool:
        return os.path.exists(file)

    def _file_empty(self, file: str) -> bool:
        return os.stat(file).st_size == 0
    
    def _get_stock_metadata_fp(self, symbol: str) -> str:
        fp = '{}/{}/metadata.json'.format(self.data_dir, symbol)
        return fp

    def _get_stock_latest_fp(self, symbol: str) -> str:
        fp = '{}/{}/latest.json'.format(self.data_dir, symbol)
        return fp

    # For now, historical means day data
    def _get_stock_historical_fp(self, symbol: str) -> str:
        fp = '{}/{}/historical/day.json'.format(self.data_dir, symbol)
        return fp

    def _read_checks_pass(self, file: str) -> bool:
        if not self._file_exists(file=file):
            self.logger.info('No data found')
            return 0
        if self._file_empty(file=file):
            self.logger.info('Data file empty')
            return 0
        return 1

    def _perform_write_checks(self, file: str):
        f_dir = os.path.splitext(file)[0]
        if not os.path.exists(f_dir):
            os.makedirs(f_dir)

    def _read_json(self, file: str) -> Dict:
        with open(file) as f:
            data = json.load(f)
            return data

    def _write_json(self, file: str, data: object):
        with open(file, 'w') as json_file:
            json.dump(obj=data.__dict__, fp=fp, indent=4)

    def read_stock_metadata(self, symbol: str) -> StockMetaData:
        fp = self._get_stock_metadata_fp(symbol=symbol)
        self.logger.info('Reading metadata from {}'.format(fp))
        if not self._read_checks_pass(file=fp): return None
        data = self._read_json(file=fp)
        print(data)

    def read_stock_latest(self, symbol: str) -> StockLatest:
        fp = self._get_stock_latest_fp(symbol=symbol)
        self.logger.info('Reading latest stock data from {}'.format(fp))
        if not self._read_checks_pass(file=fp): return None
        data = self._read_json(file=fp)
        print(data)

    # For now, historical means day data
    def read_stock_historical(self, symbol: str) -> StockHistorical:
        fp = self._get_stock_historical_fp(symbol=symbol)
        self.logger.info('Reading historical stock data from {}'.format(fp))
        if not self._read_checks_pass(file=fp): return None
        data = self._read_json(file=fp)
        print(data)

    def write_stock_metadata(self, symbol: str, metadata: StockMetaData):
        fp = self._get_stock_metadata_fp(symbol=symbol)
        self.logger.info('Writing metadata to {}'.format(fp))
        self._perform_write_checks(file=fp)
        self._write_json(file=fp, data=metadata)
        
    def write_stock_latest(self, symbol: str, latest: StockLatest):
        fp = self._get_stock_latest_fp(symbol=symbol)
        self.logger.info('Writing latest stock data to {}'.format(fp))
        self._perform_write_checks(file=fp)
        self._write_json(file=fp, data=metadata)
    
    def write_stock_historical(self, symbol: str, historical: StockHistorical):
        fp = self._get_stock_historical_fp(symbol=symbol)
        self.logger.info('Writing historical stock data to {}'.format(fp))
        self._perform_write_checks(file=fp)
        self._write_json(file=fp, data=metadata)
