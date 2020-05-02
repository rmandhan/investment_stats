import os
import sys
import logging
import logging.handlers

LOGLEVEL = logging.DEBUG
LOGDIR = '{}/logs'.format(sys.path[0])



class StockDataManager:

    def __init__(self):
        self.setup_logger()

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
        # Read YF Positions and get the positions output
        # Read Stocks List and get the stock list w/ category
        # Use these stocks to fetch historical data using tiingo api - tiingo class checks if it needs to pull
        # Use these stocks to fetch any missing data - let iex ascess the situation
        # Generate Stock object which contains the stock symbol, maybe metadata, and DayQuote data which has stock data for a date
        # Generate Positions object which contains the stock symbol, and contains Transaction object which contains the data bought/sold and the quantity, and the price
        # Return Stocks & Positions
        return 0

    # Include other helper methods in a different module which can manipulate Stocks & Positions to generate certain data required for any graphs


manager = StockDataManager()