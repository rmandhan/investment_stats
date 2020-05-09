import os
import yaml
import logging

from typing import List, Dict

class YamlFileReader():

    def __init__(self):
        self.logger = logging.getLogger('StockDataManager.StockFileReader')
    
    def read_stocks_file(self, file: str) -> List[str]:
        if not os.path.exists(file):
            self.logger.error('File {} not found'.format(file))
            raise FileNotFoundError('Stock file not found')

        with open(file, mode='r') as yaml_file:
            data = yaml.load(yaml_file, Loader=yaml.FullLoader)

        stocks_list = data['stocks']
        self.logger.info('Found {} stocks in {}'.format(len(stocks_list), file))

        return stocks_list

    def read_category_file(self, file: str) -> Dict[str, str]:
        if not os.path.exists(file):
            self.logger.error('File {} not found'.format(file))
            raise FileNotFoundError('Stock Category file not found')

        with open(file, mode='r') as yaml_file:
            data = yaml.load(yaml_file, Loader=yaml.FullLoader)

        categories_dict = data['categories']
        self.logger.info('Found categories for {} stocks in {}'.format(len(categories_dict), file))

        category_map = {}
        for s,c in categories_dict.items():
            category_map[s] = c

        return category_map