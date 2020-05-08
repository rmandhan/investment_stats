import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'packages')))

from packages import stock_data_manager

def run():
    sdm = stock_data_manager.StockDataManager()
    sdm.run()

if __name__ == '__main__':
    run()
