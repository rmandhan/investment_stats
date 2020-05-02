import os
import sys
import logging
import logging.handlers

from typing import List, Dict

from .data_types import *
from .yf_positions_reader import *
from .stock_file_reader import *

LOGLEVEL = logging.DEBUG
LOGDIR = '{}/logs'.format(sys.path[0])

# Inputs
YF_POSITIONS_FILE = '/Users/rakesh/Developer/investment_stats/inputs/positions.csv'
INDEX_TRACKERS_FILE = '/Users/rakesh/Developer/investment_stats/inputs/index_trackers.yml'
STOCKS_LIST_FILE = '/Users/rakesh/Developer/investment_stats/inputs/stocks_list.yml'

class StockDataManager:

    def __init__(self):
        self.setup_logger()
        self.all_symbols = []
        self.positions = []
        self.index_trackers = []
        self.stock_list = []

    def setup_logger(self):
        logger = logging.getLogger('StockDataManager')
        logger.setLevel(LOGLEVEL)
        if not os.path.exists(LOGDIR):
            os.mkdir(LOGDIR)
        rh = logging.handlers.RotatingFileHandler('{}/stock_data_manager.log'.format(LOGDIR), maxBytes=1000000, backupCount=3)
        rh.setLevel(LOGLEVEL)
        ch = logging.StreamHandler()
        ch.setLevel(logging.ERROR)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        rh.setFormatter(formatter)
        ch.setFormatter(formatter)
        logger.addHandler(rh)
        logger.addHandler(ch)
        logger.debug('Logger Intialized')
        self.logger = logger

    def run(self):
        pos_reader = YFPositionsReader(file=YF_POSITIONS_FILE)
        positions = pos_reader.run()
        symbols = {}
        # for pos in positions:
            # pos.pretty_print()
        for pos in positions:
            symbols[pos.symbol] = 1
        # print(symbols)
        sf_reader = StockFileReader(file=INDEX_TRACKERS_FILE)
        index_trackers = sf_reader.run()
        for it in index_trackers:
            symbols[it] = 1
        sf_reader = StockFileReader(file=STOCKS_LIST_FILE)
        stocks_list = sf_reader.run()
        for s in stocks_list:
            symbols[s] = 1
        self.all_symbols = symbols.keys()
        print(self.all_symbols)

        # Use these stocks to fetch historical data using tiingo api - tiingo class checks if it needs to pull
        # Use these stocks to fetch any missing data - let iex ascess the situation

        return 0
