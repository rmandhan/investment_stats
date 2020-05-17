import os
import yaml
import logging

from typing import List, Dict

class YamlFileReader():

    def __init__(self):
        self.logger = logging.getLogger('StockDataManager.StockFileReader')

    def _read_from_file(self, file: str, key: str) -> List[str]:
        if not os.path.exists(file):
            self.logger.error('File {} not found'.format(file))
            raise FileNotFoundError('Yaml file not found')

        with open(file, mode='r') as yaml_file:
            data = yaml.load(yaml_file, Loader=yaml.FullLoader)

        output = data[key]
        self.logger.info('Successfully read {}'.format(file))

        return output

    def read_stocks_file(self, file: str) -> List[str]:
        return self._read_from_file(file=file, key='stocks')

    def read_category_file(self, file: str) -> Dict[str, str]:
        categories_dict = self._read_from_file(file=file, key='categories')
        category_map = {}
        for s,c in categories_dict.items():
            category_map[s] = c

        return category_map

    def read_category_allocation_file(self, file: str) -> Dict[str, float]:
        category_allocations = self._read_from_file(file=file, key='allocation')
        # Force all values to floats
        for k,v in category_allocations.items():
            category_allocations[k] = float(v)
        return category_allocations