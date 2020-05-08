import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'packages')))

from packages import data_types
from packages import stock_data_manager
from packages import stock_visualizer

def run():
    sdm = stock_data_manager.StockDataManager()
    sv = stock_visualizer.StockVisualizer(sdm=sdm)
    sv.run()

if __name__ == '__main__':
    run()
