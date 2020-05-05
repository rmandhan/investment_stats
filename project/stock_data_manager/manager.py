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
WATCHLIST_STOCKS_FILE = '/Users/rakesh/Developer/investment_stats/inputs/watchlist.yml'

# Outputs/Storage
STOCK_DATA_DIR = '/Users/rakesh/Developer/investment_stats/data'

# API Keys
TIINGO_API_KEY = '/Users/rakesh/Developer/investment_stats/api_keys/tiingo'
IEX_API_KEY = '/Users/rakesh/Developer/investment_stats/api_keys/iex'

class StockDataManager:

    def __init__(self):
        self._setup_logger()
        self.all_symbols = []
        self.index_tracker_stocks = []
        self.watchlist_stocks = []
        self.position_stocks = []
        self.positions = []

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

    def _extract_symbols(self, positions: [Position]) -> List[str]:
        symbols = []
        for pos in positions:
            symbols.append(pos.symbol)
        return symbols

    def _remove_duplicats(self, symbols: List[str]) -> List[str]:
        d = {}
        for s in symbols:
            d[s] = 1
        return d.keys()

    def _generate_stock(self, metadata: StockMetaData, latest: StockLatest, historical: StockHistorical) -> Stock:
        stock = Stock(symbol=metadata.symbol, company_name=metadata.company_name, industry=metadata.industry, issue_type=metadata.issue_type, latest_quote=latest.quote, day_quotes=historical.day_quotes)
        return stock

    def get_all_symbols() -> List[str]:
        return self.all_symbols

    def get_index_tracker_stocks() -> List[Stock]:
        return self.index_tracker_stocks

    def get_watchlist_stocks() -> List[Stock]:
        return self.watchlist_stocks

    def get_position_stocks() -> List[Stock]:
        return self.position_stocks
    
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
        sf_reader = StockFileReader(file=WATCHLIST_STOCKS_FILE)
        watchlist = sf_reader.run()

        self.positions = positions
        position_symbols = self._extract_symbols(positions=positions)

        # Create a list of all the symbols
        self.all_symbols = self._remove_duplicats(symbols=position_symbols+index_trackers+watchlist)

        # Initialize data store
        ds = DataStore(data_dir=STOCK_DATA_DIR)

        stock_data = []

        # Update data
        for symbol in self.all_symbols:
            # Read data from local storage
            metadata = ds.read_stock_metadata(symbol=symbol)
            latest = ds.read_stock_latest(symbol=symbol)
            historical = ds.read_stock_historical(symbol=symbol)
            # Fetch/update metadata and latest quote for all symbols using IEX API
            iex = IEXAPI(api_key_path=IEX_API_KEY)
            metadata, updated = iex.update_metadata(symbol=symbol, metadata=metadata)
            latest, updated = iex.update_latest(symbol=symbol, latest=latest)
            # Update local storage
            if updated: ds.write_stock_metadata(symbol=symbol, metadata=metadata)
            if updated: ds.write_stock_latest(symbol=symbol, latest=latest)
            # Fetch/update historical data for all symbols using Tiingo API
            tiingo = TiingoAPI(api_key_path=TIINGO_API_KEY)
            historical, updated = tiingo.update_historical(symbol=symbol, historical=historical)
            # Update local storage
            if updated: ds.write_stock_historical(symbol=symbol, historical=historical)
            # Append stock data to final output
            stock_data.append(self._generate_stock(metadata=metadata, latest=latest, historical=historical))
            self.logger.info('Successfully refreshed data for {}'.format(symbol))

        # Create the various list of stocks
        for stock in stock_data:
            if stock.symbol in index_trackers:
                self.index_tracker_stocks.append(stock)
            if stock.symbol in watchlist:
                self.watchlist_stocks.append(stock)
            if stock.symbol in position_symbols:
                self.position_stocks.append(stock)

        self.logger.info('Finished processing for {} symbols'.format(len(self.all_symbols)))

        return 0
