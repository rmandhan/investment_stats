import sys
import os
import logging
import logging.handlers

import dash
import dash_core_components as dcc
import dash_html_components as html

from data_types import *
from stock_data_manager import *

LOGLEVEL = logging.DEBUG
LOGDIR = '{}/logs'.format(sys.path[0])

class StockVisualizer():

    def __init__(self, sdm: StockDataManager):
        self._setup_logger()
        self.sdm = sdm

    def _setup_logger(self):
        logger = logging.getLogger('StockVisualizer')
        logger.setLevel(LOGLEVEL)
        if not os.path.exists(LOGDIR):
            os.mkdir(LOGDIR)
        rh = logging.handlers.RotatingFileHandler('{}/stock_visualizer.log'.format(LOGDIR), maxBytes=1000000, backupCount=3)
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
        self.sdm.run()