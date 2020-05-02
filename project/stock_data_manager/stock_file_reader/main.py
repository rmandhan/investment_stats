import os
import yaml
import logging

from typing import List

STOCKS_KEY='stocks'

class StockFileReader():

    def __init__(self, file: str):
        self.logger = logging.getLogger('StockDataManager.StockFileReader')
        self.file = file
    
    def read_file(self) -> List[str]:
        if not os.path.exists(self.file):
            self.logger.error('File {} not found'.format(self.file))
            raise FileNotFoundError('Stock file not found')

        with open(self.file, mode='r') as yaml_file:
            data = yaml.load(yaml_file, Loader=yaml.FullLoader)

        stocks_list = data[STOCKS_KEY]
        self.logger.info('Found {} stocks in {}'.format(len(stocks_list), self.file))

        return stocks_list

    def run(self):
        return self.read_file()