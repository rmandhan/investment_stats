import os
import csv
import logging

from typing import List
from datetime import datetime

from . import csv_keys
from ..data_types import *

class YFPositionsReader():

    def __init__(self, file: str):
        self.logger = logging.getLogger('StockDataManager.YFPositionsReader')
        self.file = file

    def read_file(self) -> List:
        if not os.path.exists(self.file):
            self.logger.error('File {} not found'.format(self.file))
            raise FileNotFoundError('Yahoo Finance Positions file not found')

        csv_rows = []
        with open(self.file, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                csv_rows.append(row)
            if len(csv_rows) < 1:
                self.logger.warn('CSV File Empty')
            elif len(csv_rows) < 2:
                self.logger.warn('No positions found')
            else:
                csv_rows = csv_rows[1:len(csv_rows)-1]
                self.logger.info('{} trades found in positions file'.format(len(csv_rows)))

        return csv_rows

    def parse_csv(self, csv_rows: List) -> List[Position]:
        # Mapping of symbol to transactions
        symbol_transactions = {}
        positions = []

        for row in csv_rows:
            symbol = row[csv_keys.SYMBOL]
            quantity = row[csv_keys.QUANTITY]
            purchase_price = row[csv_keys.PURCHASE_PRICE]
            trade_date = row[csv_keys.TRADE_DATE]
            # Convert date to datetime
            trade_date = datetime.strptime(trade_date, '%Y%m%d')
            # Create a transaction
            trans = Transaction(trade_date=trade_date, quantity=quantity, purchase_price=purchase_price)
            if symbol in symbol_transactions:
                transactions = symbol_transactions[symbol]
                transactions.append(trans)
                symbol_transactions[symbol] = transactions
            else:
                symbol_transactions[symbol] = [trans]
            
        for symbol in symbol_transactions:
            # Create positions
            position = Position(symbol=symbol, transactions=symbol_transactions[symbol])
            positions.append(position)

        self.logger.info('Successfully parsed all positions')

        return positions

    def run(self) -> List[Position]:
        csv_rows = self.read_file()
        positions = self.parse_csv(csv_rows)
        return positions