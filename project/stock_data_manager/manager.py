import os
import sys
import logging
import logging.handlers

from typing import List, Dict

from .data_types import *
from .yf_positions_reader import *
from .stock_file_reader import *
from .data_store import *
from .tiingo_api import *
from .iex_api import *

LOGLEVEL = logging.DEBUG
LOGDIR = '{}/logs'.format(sys.path[0])

# Inputs
YF_POSITIONS_FILE = '/Users/rakesh/Developer/investment_stats/inputs/positions.csv'
INDEX_TRACKERS_FILE = '/Users/rakesh/Developer/investment_stats/inputs/index_trackers.yml'
STOCKS_LIST_FILE = '/Users/rakesh/Developer/investment_stats/inputs/stocks_list.yml'

# Outputs/Storage
STOCK_DATA_DIR = '/Users/rakesh/Developer/investment_stats/data'

# API Keys
TIINGO_API_KEY = '/Users/rakesh/Developer/investment_stats/api_keys/tiingo'
IEX_API_KEY = '/Users/rakesh/Developer/investment_stats/api_keys/iex'

class StockDataManager:

    def __init__(self):
        self._setup_logger()
        self.all_symbols = []
        self.index_trackers = []
        self.stock_list = []
        self.positions = []
        self.stock_data = []

    def _setup_logger(self):
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

    def _extract_symbols(self, positions: [Position], stock_inputs: List[str]) -> List[str]:
        symbols = {}
        for pos in positions:
            symbols[pos.symbol] = 1
        for stock in stock_inputs:
            symbols[stock] = 1
        return symbols.keys()

    def _generate_stock(metadata: StockMetaData, latest: StockLatest, historical: StockHistorical) -> Stock:
        stock = Stock(symbol=metadata.symbol, company_name=metadata.company_name, industry=metadata.industry, issue_type=metadata.issue_type, latest_quote=latest.quote, day_quotes=historical.day_quotes)
        return stock

    def get_all_symbols() -> List[str]:
        return self.all_symbols

    def get_index_trackers() -> List[str]:
        return self.index_trackers

    def get_stock_list() -> List[str]:
        return self.stock_list

    def get_stocks() -> List[Stock]:
        return self.stock_data
    
    def get_positions() -> List[Position]:
        return self.positions

    def refresh():
        self.run()

    def run(self):

        # Extract data from inputs
        pos_reader = YFPositionsReader(file=YF_POSITIONS_FILE)
        positions = pos_reader.run()
        sf_reader = StockFileReader(file=INDEX_TRACKERS_FILE)
        index_trackers = sf_reader.run()
        sf_reader = StockFileReader(file=STOCKS_LIST_FILE)
        stocks_list = sf_reader.run()

        # Create a list of unique symbols
        self.all_symbols = self._extract_symbols(positions=positions, stock_inputs=index_trackers+stocks_list)

        # Initialize data store
        ds = DataStore(data_dir=STOCK_DATA_DIR)

        # print(self.all_symbols)

        # Update data
        for symbol in self.all_symbols:
            # Read data from local storage
            metadata = ds.read_stock_metadata(symbol=symbol)
            latest = ds.read_stock_latest(symbol=symbol)
            historical = ds.read_stock_historical(symbol=symbol)
            # # Fetch/update metadata and latest quote for all symbols using IEX API
            iex = IEXAPI(api_key_path=IEX_API_KEY)
            metadata, updated = iex.update_metadata(symbol=symbol, metadata=metadata)
            latest, updated = iex.update_latest(symbol=symbol, latest=latest)
            # Update local storage
            if updated: ds.write_stock_metadata(symbol=symbol, metadata=metadata)
            if updated: ds.write_stock_latest(symbol=symbol, latest=latest)
            # # Fetch/update historical data for all symbols using Tiingo API
            # tiingo = TiingoAPI(api_key_path=TIINGO_API_KEY)
            # historical, updated = tiingo.update_historical(historical=historical)
            # # Update local storage
            # if updated: ds.write_stock_historical(historical=historical)
            # # Append stock data to final output
            # self.stock_data.append(self._generate_stock(metadata=metadata, latest=latest, historical=historical))

        return 0
