import pandas as pd
import numpy as np
import pytz

from datetime import datetime, timezone
from typing import List, Dict, Tuple
from scipy.optimize import minimize
from data_types import *

MIN_DATETIME = datetime(year=1, month=1, day=1, tzinfo=timezone.utc)
MAX_DATETIME = datetime(year=9999, month=12, day=31, tzinfo=timezone.utc)

ROUNDING_DECIMAL_PLACES = 2

# Pre-defined Data Keys
SYMBOL_KEY = Stock._symbol_key
COMPANY_NAME_KEY = Stock._company_name_key
INDUSTRY_KEY = Stock._industry_key
ISSUE_TYPE_KEY = Stock._issue_type_key
DATE_KEY = Quote._date_key
HIGH_KEY = Quote._high_key
LOW_KEY = Quote._low_key
OPEN_KEY = Quote._open_key
CLOSE_KEY = Quote._close_key
VOLUME_KEY = Quote._volume_key
TRADE_DATE_KEY = Transaction._trade_date_key
QUANTITY_KEY = Transaction._quantity_key
PURCHASE_PRICE_KEY = Transaction._purchase_price_key
# New Data Keys
INVESTED_AMOUNT_KEY = 'invested_amount'
MARKET_VALUE_KEY = 'market_value'
UNREALIZED_GAIN_KEY = 'unrealized_gain'
UNREALIZED_PCT_GAIN_KEY = 'unrealized_pct_gain'
REALIZED_GAIN_KEY = 'realized_gain'
REALIZED_PCT_GAIN_KEY = 'realized_pct_gain'
TOTAL_GAIN_KEY = 'total_gain'
TOTAL_PCT_GAIN_KEY = 'total_pct_gain'
AVERAGE_COST_KEY = 'average_cost'
CATEGORY_KEY = 'category'
COMP_INVESTED_KEY = 'composition_invested'
COMP_MARKET_KEY = 'composition_market'
REL_UNREALIZED_GAIN_KEY = 'relative_unrealized_gain'
REL_REALIZED_GAIN_KEY = 'relative_realized_gain'
REL_TOTAL_GAIN_KEY = 'relative_total_gain'
DESIRED_ALLOCATION_KEY = 'desired_allocation'
DESIRED_COMP_INV_DIFF_KEY = 'desired_composition_invested_diff'
ALLOCATION_BREAK_EVEN_KEY = 'allocation_break_even'

class StockDataConsumer():

    def __init__(self, all_symbols: List[str], stock_categories: Dict[str, str], category_allocations: Dict[str, float], index_tracker_stocks: List[Stock], watchlist_stocks: List[Stock], portfolio_stocks: List[Stock], positions: List[Position]):
        self.all_symbols = all_symbols
        self.stock_categories = stock_categories
        self.category_allocations = category_allocations
        self.index_tracker_stocks = index_tracker_stocks
        self.watchlist_stocks = watchlist_stocks
        self.portfolio_stocks = portfolio_stocks
        self.positions = positions
        # Outputs
        self.portfolio_stock_stats = {} # Key = Symbol
        self.portfolio_aggregate_stats = pd.DataFrame()
        self.portfolio_stock_composition_stats = {} # Key = Date
        self.portfolio_category_composition_stats = {} # Key = Date

    def _derive_base_stock_data(self):
        stock_df_map = {}
        stocks = self.portfolio_stocks+self.watchlist_stocks+self.index_tracker_stocks
        for s in stocks:
            stock_df_map[s.symbol] = s.df()
        self.stock_df_map = stock_df_map

    def _derive_base_portfolio_data(self):
        positions_df_map = {}
        portfolio_start_date = None
        portfolio_market_dates = []
        stocks = self.portfolio_stocks
        # Put all positions into a df
        portfolio_start_date = MAX_DATETIME
        for p in self.positions:
            positions_df_map[p.symbol] = p.df()
            d = p.transactions[0].trade_date
            if d < portfolio_start_date:
                portfolio_start_date = d
        stock_to_use: Stock
        for s in stocks:
            # Use any stock that has data since portfolio_start_date
            if s.day_quotes[0].date < portfolio_start_date:
                stock_to_use = s
                break
        # Add all historical quote dates
        for q in stock_to_use.day_quotes:
            if q.date >= portfolio_start_date:
                portfolio_market_dates.append(q.date)
        # Also add date from the latest stock data
        portfolio_market_dates.append(stock_to_use.latest_quote.date)
        # Update class variables
        self.positions_df_map = positions_df_map
        self.portfolio_start_date = portfolio_start_date
        self.portfolio_market_dates = portfolio_market_dates

    def _print_df(self, df: pd.DataFrame):
        with pd.option_context('display.max_rows', None, 'display.max_columns', None):
            print(df)

    def _calculate_portfolio_stats_for_stock(self, symbol: str) -> pd.DataFrame:
        final_df = pd.DataFrame()
        # final_df is made up of these
        dates_a = self.portfolio_market_dates
        invested_amount_a = []
        market_value_a = []
        unrealized_gain_a = []
        unrealized_pct_gain_a = []
        realized_gain_a = []
        realized_pct_gain_a = []
        quantity_a = []
        average_cost_a = []
        total_gain_a = []
        total_pct_gain_a = []
        high_price_a = []
        low_price_a = []
        open_price_a = []
        close_price_a = []
        volume_a = []
        company_a = []
        # Get stock and it's transactions
        stock = self.stock_df_map[symbol]
        transactions = self.positions_df_map[symbol]
        transactions_processed_count = 0
        num_dates = len(dates_a)
        # Iterate over each market day, calculating values
        for i in range(0, len(dates_a)):
            date = dates_a[i]
            # Values that change with market value or are derived from cumulative values below
            market_value_d = 0
            unrealized_gain_d = 0
            unrealized_pct_gain_d = 0
            realized_pct_gain_d = 0
            total_pct_gain_d = 0
            # These values are cumulative
            if len(quantity_a) > 0:
                invested_amount_d = invested_amount_a[len(invested_amount_a)-1] 
                realized_gain_d = realized_gain_a[len(realized_gain_a)-1]
                total_gain_d = total_gain_a[len(total_gain_a)-1]
                quantity_d = quantity_a[len(quantity_a)-1] 
                average_cost_d = average_cost_a[len(average_cost_a)-1]
            else:
                invested_amount_d = 0
                realized_gain_d = 0
                total_gain_d = 0
                quantity_d = 0
                average_cost_d = 0
            # Process any remaining transactions
            while transactions_processed_count < len(transactions):
                # Get the next transaction
                transaction = transactions.iloc[transactions_processed_count]
                trade_date = transaction[TRADE_DATE_KEY].to_pydatetime()
                # If trade wasn't made today, skip
                if trade_date > date:
                    break
                quantity = transaction[QUANTITY_KEY]
                purchase_price = transaction[PURCHASE_PRICE_KEY]
                # Check if transaction was a buy or a sell
                if quantity > 0:
                    # Update average cost when a buy
                    average_cost_d = ((average_cost_d*quantity_d)+(quantity*purchase_price))/(quantity_d+quantity)
                else:
                    # Average cost doesn't change, but add to realized gains when a sell
                    realized_gain_d += (purchase_price-average_cost_d)*quantity*-1
                # Update today's quantity
                quantity_d += quantity
                transactions_processed_count += 1
            # Get stock values for today
            df_index = stock.shape[0]-num_dates+i    # Offset to get close price for this date
            high_price = stock.iloc[df_index][HIGH_KEY]
            low_price = stock.iloc[df_index][LOW_KEY]
            open_price = stock.iloc[df_index][OPEN_KEY]
            close_price = stock.iloc[df_index][CLOSE_KEY]
            volume  = stock.iloc[df_index][VOLUME_KEY]
            company = stock.iloc[df_index][COMPANY_NAME_KEY]
            # Calculate values based on transactions or previous day's values
            invested_amount_d = quantity_d*average_cost_d
            if invested_amount_d > 0:
                realized_pct_gain_d = (realized_gain_d/invested_amount_d)*100
                market_value_d = close_price*quantity_d
                unrealized_gain_d = market_value_d-invested_amount_d
                unrealized_pct_gain_d = (unrealized_gain_d/invested_amount_d)*100
                total_gain_d = unrealized_gain_d+realized_gain_d
                total_pct_gain_d = (total_gain_d/invested_amount_d)*100
            # Append final values to arrays
            invested_amount_a.append(invested_amount_d)
            market_value_a.append(market_value_d)
            unrealized_gain_a.append(unrealized_gain_d)
            unrealized_pct_gain_a.append(unrealized_pct_gain_d)
            realized_gain_a.append(realized_gain_d)
            realized_pct_gain_a.append(realized_pct_gain_d)
            quantity_a.append(quantity_d)
            average_cost_a.append(average_cost_d)
            total_gain_a.append(total_gain_d)
            total_pct_gain_a.append(total_pct_gain_d)
            high_price_a.append(high_price)
            low_price_a.append(low_price)
            open_price_a.append(open_price)
            close_price_a.append(close_price)
            volume_a.append(volume)
            company_a.append(company)
        # Create and return final df
        final_df[DATE_KEY] = dates_a
        final_df[INVESTED_AMOUNT_KEY] = invested_amount_a
        final_df[MARKET_VALUE_KEY] = market_value_a
        final_df[UNREALIZED_GAIN_KEY] = unrealized_gain_a
        final_df[UNREALIZED_PCT_GAIN_KEY] = unrealized_pct_gain_a
        final_df[REALIZED_GAIN_KEY] = realized_gain_a
        final_df[REALIZED_PCT_GAIN_KEY] = realized_pct_gain_a
        final_df[TOTAL_GAIN_KEY] = total_gain_a
        final_df[TOTAL_PCT_GAIN_KEY] = total_pct_gain_a
        final_df[QUANTITY_KEY] = quantity_a
        final_df[AVERAGE_COST_KEY] = average_cost_a
        final_df[HIGH_KEY] = high_price_a
        final_df[LOW_KEY] = low_price_a
        final_df[OPEN_KEY] = open_price_a
        final_df[CLOSE_KEY] = close_price_a
        final_df[VOLUME_KEY] = volume_a
        final_df[COMPANY_NAME_KEY] = company_a
        return final_df.round(ROUNDING_DECIMAL_PLACES)
    
    def _aggregate_portfolio_stock_stats(self) -> pd.DataFrame:
        final_df = pd.DataFrame()
        # final_df is made up of these
        dates_a = self.portfolio_market_dates
        invested_amount_a = []
        market_value_a = []
        unrealized_gain_a = []
        unrealized_pct_gain_a = []
        realized_gain_a = []
        realized_pct_gain_a = []
        total_gain_a = []
        total_pct_gain_a = []
        # The values we need are calculated from these
        stock_dfs = self.get_portfolio_stock_stats()
        for i in range(0, len(dates_a)):
            invested_amount_d = 0
            market_value_d = 0
            unrealized_gain_d = 0
            unrealized_pct_gain_d = 0
            realized_gain_d = 0
            realized_pct_gain_d = 0
            total_gain_d = 0
            total_pct_gain_d = 0
            # Sum up these values for all the stocks
            for symbol, df in stock_dfs.items():
                values = df.iloc[i]
                invested_amount_d += values[INVESTED_AMOUNT_KEY]
                market_value_d += values[MARKET_VALUE_KEY]
                unrealized_gain_d += values[UNREALIZED_GAIN_KEY]
                realized_gain_d += values[REALIZED_GAIN_KEY]
                total_gain_d += values[TOTAL_GAIN_KEY]
            # Derive these values from the summed up values
            unrealized_pct_gain_d = (unrealized_gain_d/invested_amount_d)*100
            realized_pct_gain_d = (realized_gain_d/invested_amount_d)*100
            total_pct_gain_d = (total_gain_d/invested_amount_d)*100
            # Append final values to arrays
            invested_amount_a.append(invested_amount_d)
            market_value_a.append(market_value_d)
            unrealized_gain_a.append(unrealized_gain_d)
            unrealized_pct_gain_a.append(unrealized_pct_gain_d)
            realized_gain_a.append(realized_gain_d)
            realized_pct_gain_a.append(realized_pct_gain_d)
            total_gain_a.append(total_gain_d)
            total_pct_gain_a.append(total_pct_gain_d)
        # Create and return final df
        final_df[DATE_KEY] = dates_a
        final_df[INVESTED_AMOUNT_KEY] = invested_amount_a
        final_df[MARKET_VALUE_KEY] = market_value_a
        final_df[UNREALIZED_GAIN_KEY] = unrealized_gain_a
        final_df[UNREALIZED_PCT_GAIN_KEY] = unrealized_pct_gain_a
        final_df[REALIZED_GAIN_KEY] = realized_gain_a
        final_df[REALIZED_PCT_GAIN_KEY] = realized_pct_gain_a
        final_df[TOTAL_GAIN_KEY] = total_gain_a
        final_df[TOTAL_PCT_GAIN_KEY] = total_pct_gain_a
        return final_df.round(ROUNDING_DECIMAL_PLACES)
    
    def _calculate_portfolio_composition_stats(self, index: int) -> Tuple[pd.DataFrame, pd.DataFrame]:
        stock_c_df = pd.DataFrame()
        category_c_df = pd.DataFrame()
        stock_stats = self.portfolio_stock_stats
        aggregated_values = self.portfolio_aggregate_stats.iloc[index]
        stock_categories = self.stock_categories
        unique_categories = np.unique(list(stock_categories.values())+['Unknown'])
        # stock_c_df is made up of these
        symbol_a_s = []
        category_a_s = []
        composition_invested_a_s = []
        composition_market_a_s = []
        relative_realized_gain_a_s = []
        relative_unrealized_gain_a_s = []
        relative_total_gain_a_s = []
        # these are copied over
        invested_amount_a_s = []
        realized_gain_a_s = []
        realized_pct_gain_a_s = []
        unrealized_gain_a_s = []
        unrealized_pct_gain_a_s = []
        total_gain_a_s = []
        total_pct_gain_a_s = []
        company_name_a_s = []
        # category_c_df is derived from these dictionaries
        composition_invested_a_c = {}
        composition_market_a_c = {}
        relative_realized_gains_a_c = {}
        relative_unrealized_gain_a_c = {}
        relative_total_gain_a_c = {}
        invested_amount_a_c = {}
        realized_gain_a_c = {}
        unrealized_gain_a_c = {}
        total_gain_a_c = {}
        # category_c_df is made up of these
        composition_invested_a_c_l = []
        composition_market_a_c_l = []
        relative_realized_gains_a_c_l = []
        relative_unrealized_gain_a_c_l = []
        relative_total_gain_a_c_l = []
        invested_amount_a_c_l = []
        realized_gain_a_c_l = []
        unrealized_gain_a_c_l = []
        total_gain_a_c_l = []
        # Derived at the end
        realized_pct_gain_a_c_l = []
        unrealized_pct_gain_a_c_l = []
        total_pct_gain_a_c_l = []
        desired_allocation_a_c_l = []
        comp_inv_diff_a_c_l = []
        # Intialize category dictionaries
        for cat in unique_categories:
            composition_invested_a_c[cat] = 0
            composition_market_a_c[cat] = 0
            relative_realized_gains_a_c[cat] = 0
            relative_unrealized_gain_a_c[cat] = 0
            relative_total_gain_a_c[cat] = 0
            invested_amount_a_c[cat] = 0
            realized_gain_a_c[cat] = 0
            unrealized_gain_a_c[cat] = 0
            total_gain_a_c[cat] = 0
        categories_found = {}
        # Iterate over each stock
        for symbol, stock in stock_stats.items():
            stock_values = stock.iloc[index]
            cat = stock_categories.get(symbol, 'Unknown')
            categories_found[cat] = 1
            # Calculate composition and relative values for stock_c_df
            composition_invested = (stock_values[INVESTED_AMOUNT_KEY]/aggregated_values[INVESTED_AMOUNT_KEY])*100
            composition_market = (stock_values[MARKET_VALUE_KEY]/aggregated_values[MARKET_VALUE_KEY])*100
            a_gain = aggregated_values[REALIZED_GAIN_KEY]
            relative_realized_gain = 0 if a_gain == 0 else (stock_values[REALIZED_GAIN_KEY]/a_gain)*100
            a_gain = aggregated_values[UNREALIZED_GAIN_KEY]
            relative_unrealized_gain = 0 if a_gain == 0 else (stock_values[UNREALIZED_GAIN_KEY]/a_gain)*100
            a_gain = aggregated_values[TOTAL_GAIN_KEY]
            realtive_total_gain = 0 if a_gain == 0 else (stock_values[TOTAL_GAIN_KEY]/a_gain)*100
            # Append values for this symbol for stock_c_df
            symbol_a_s.append(symbol)
            category_a_s.append(cat)
            composition_invested_a_s.append(composition_invested)
            composition_market_a_s.append(composition_market)
            relative_realized_gain_a_s.append(relative_realized_gain)
            relative_unrealized_gain_a_s.append(relative_unrealized_gain)
            relative_total_gain_a_s.append(realtive_total_gain)
            invested_amount_a_s.append(stock_values[INVESTED_AMOUNT_KEY])
            realized_gain_a_s.append(stock_values[REALIZED_GAIN_KEY])
            realized_pct_gain_a_s.append(stock_values[REALIZED_PCT_GAIN_KEY])
            unrealized_gain_a_s.append(stock_values[UNREALIZED_GAIN_KEY])
            unrealized_pct_gain_a_s.append(stock_values[UNREALIZED_PCT_GAIN_KEY])
            total_gain_a_s.append(stock_values[TOTAL_GAIN_KEY])
            total_pct_gain_a_s.append(stock_values[TOTAL_PCT_GAIN_KEY])
            company_name_a_s.append(stock_values[COMPANY_NAME_KEY])
            # Update values for this category for category_c_df
            composition_invested_a_c[cat] += composition_invested
            composition_market_a_c[cat] += composition_market
            relative_realized_gains_a_c[cat] += relative_realized_gain
            relative_unrealized_gain_a_c[cat] += relative_unrealized_gain
            relative_total_gain_a_c[cat] += realtive_total_gain
            invested_amount_a_c[cat] += stock_values[INVESTED_AMOUNT_KEY]
            realized_gain_a_c[cat] += stock_values[REALIZED_GAIN_KEY]
            unrealized_gain_a_c[cat] += stock_values[UNREALIZED_GAIN_KEY]
            total_gain_a_c[cat] += stock_values[TOTAL_GAIN_KEY]
        # Create category_c_df
        stock_c_df[SYMBOL_KEY] = symbol_a_s
        stock_c_df[CATEGORY_KEY] = category_a_s
        stock_c_df[COMP_INVESTED_KEY] = composition_invested_a_s
        stock_c_df[COMP_MARKET_KEY] = composition_market_a_s
        stock_c_df[REL_REALIZED_GAIN_KEY] = relative_realized_gain_a_s
        stock_c_df[REL_UNREALIZED_GAIN_KEY] = relative_unrealized_gain_a_s
        stock_c_df[REL_TOTAL_GAIN_KEY] = relative_total_gain_a_s
        stock_c_df[INVESTED_AMOUNT_KEY] = invested_amount_a_s
        stock_c_df[REALIZED_GAIN_KEY] = realized_gain_a_s
        stock_c_df[REALIZED_PCT_GAIN_KEY] = realized_pct_gain_a_s
        stock_c_df[UNREALIZED_GAIN_KEY] = unrealized_gain_a_s
        stock_c_df[UNREALIZED_PCT_GAIN_KEY] = unrealized_pct_gain_a_s
        stock_c_df[TOTAL_GAIN_KEY] = total_gain_a_s
        stock_c_df[TOTAL_PCT_GAIN_KEY] = total_pct_gain_a_s
        stock_c_df[COMPANY_NAME_KEY] = company_name_a_s
        # Calculate remaining values and create category_c_df
        # Build the final arrays
        for cat in categories_found.keys():
            composition_invested_a_c_l.append(composition_invested_a_c[cat])
            composition_market_a_c_l.append(composition_market_a_c[cat])
            relative_realized_gains_a_c_l.append(relative_realized_gains_a_c[cat])
            relative_unrealized_gain_a_c_l.append(relative_unrealized_gain_a_c[cat])
            relative_total_gain_a_c_l.append(relative_total_gain_a_c[cat])
            invested_amount_a_c_l.append(invested_amount_a_c[cat])
            realized_gain_a_c_l.append(realized_gain_a_c[cat])
            unrealized_gain_a_c_l.append(unrealized_gain_a_c[cat])
            total_gain_a_c_l.append(total_gain_a_c[cat])
            # Derive percentages
            inv_amount = invested_amount_a_c[cat]
            if inv_amount > 0:
                realized_pct_gain_c = (realized_gain_a_c[cat]/inv_amount)*100
                unrealized_pct_gain_c = (unrealized_gain_a_c[cat]/inv_amount)*100
                total_pct_gain_c = (total_gain_a_c[cat]/inv_amount)*100
            else:
                realized_pct_gain_c = 0
                unrealized_pct_gain_c = 0
                total_pct_gain_c = 0
            realized_pct_gain_a_c_l.append(realized_pct_gain_c)
            unrealized_pct_gain_a_c_l.append(unrealized_pct_gain_c)
            total_pct_gain_a_c_l.append(total_pct_gain_c)
            # Calculate composition invested diff
            comp_diff = composition_invested_a_c[cat]
            desired_comp = 0
            if cat != 'Unknown' and cat in self.category_allocations:
                desired_comp = self.category_allocations[cat]
                comp_diff = composition_invested_a_c[cat]-desired_comp
            comp_inv_diff_a_c_l.append(comp_diff)
            desired_allocation_a_c_l.append(desired_comp)
        category_c_df[CATEGORY_KEY] = categories_found.keys()
        category_c_df[COMP_INVESTED_KEY] = composition_invested_a_c_l
        category_c_df[COMP_MARKET_KEY] = composition_market_a_c_l
        category_c_df[REL_REALIZED_GAIN_KEY] = relative_realized_gains_a_c_l
        category_c_df[REL_UNREALIZED_GAIN_KEY] = relative_unrealized_gain_a_c_l
        category_c_df[REL_TOTAL_GAIN_KEY] = relative_total_gain_a_c_l
        category_c_df[INVESTED_AMOUNT_KEY] = invested_amount_a_c_l
        category_c_df[REALIZED_GAIN_KEY] = realized_gain_a_c_l
        category_c_df[UNREALIZED_GAIN_KEY] = unrealized_gain_a_c_l
        category_c_df[TOTAL_GAIN_KEY] = total_gain_a_c_l
        category_c_df[REALIZED_PCT_GAIN_KEY] = realized_pct_gain_a_c_l
        category_c_df[UNREALIZED_PCT_GAIN_KEY] = unrealized_pct_gain_a_c_l
        category_c_df[TOTAL_PCT_GAIN_KEY] = total_pct_gain_a_c_l
        category_c_df[DESIRED_ALLOCATION_KEY] = desired_allocation_a_c_l
        category_c_df[DESIRED_COMP_INV_DIFF_KEY] = comp_inv_diff_a_c_l
        return stock_c_df.round(ROUNDING_DECIMAL_PLACES), category_c_df.round(ROUNDING_DECIMAL_PLACES)

    def maximize_desired_allocation(self, date: datetime) -> pd.DataFrame():
        final_df = pd.DataFrame()
        category_df = self.portfolio_category_composition_stats[date]

        current_inv_amount = category_df[INVESTED_AMOUNT_KEY]
        desired_allocation_amount = category_df[DESIRED_ALLOCATION_KEY].divide(100)
        unknown_vars_count = category_df.shape[0]

        # Define objective & constraints
        def objective(x):
            return sum(x)
        def ineq_cons(x):
            return sum(x)
        constraint_funcs = {}
        inv_amount_sum = sum(current_inv_amount)
        for i in range(unknown_vars_count):
            inv_amount = current_inv_amount[i]
            desired_allocation = desired_allocation_amount[i]
            code = """def eq_cons_{0:d}(x): return (({1:f}+x[{0:d}])/(sum(x)+{2:f}))-{3:f}""".format(i, inv_amount, inv_amount_sum, desired_allocation)
            exec(code, {}, constraint_funcs)

        # Create constraints list
        cons = []
        cons.append({'type': 'ineq','fun': ineq_cons})
        for i in range(unknown_vars_count):
            cons.append({'type': 'ineq', 'fun': constraint_funcs['eq_cons_{0:d}'.format(i)]})

        # TODO: Improve bounds & initial guess
        bnds = [(0.0, inv_amount_sum)] * unknown_vars_count
        x0 = [1] * unknown_vars_count

        # Minimize
        sol = minimize(objective, x0, method='SLSQP', bounds=bnds, constraints=cons)
        solution = [0] * unknown_vars_count
        if sol.success:
            solution = np.around(sol.x, decimals=2)

        final_df[CATEGORY_KEY] = category_df[CATEGORY_KEY]
        final_df[ALLOCATION_BREAK_EVEN_KEY] = solution

        return final_df

    def get_portfolio_stock_stats(self, combined=False) -> Dict[str, pd.DataFrame]:
        final_df = self.portfolio_stock_stats
        if combined:
            dfs = []
            for symbol, df in self.portfolio_stock_stats.items():
                df['symbol'] = symbol
                dfs.append(df)
            final_df = pd.concat(dfs)
        return final_df
    
    def get_portfolio_aggregate_stats(self) -> pd.DataFrame:
        return self.portfolio_aggregate_stats

    def get_portfolio_stock_composition_stats(self, combined=False) -> Dict[str, pd.DataFrame]:
        final_df = self.portfolio_stock_composition_stats
        if combined:
            dfs = []
            for date, df in self.portfolio_stock_composition_stats.items():
                df['date'] = date
                dfs.append(df)
            final_df = pd.concat(dfs)
        return final_df

    def get_portfolio_category_composition_stats(self, combined=False) -> Dict[str, pd.DataFrame]:
        final_df = self.portfolio_category_composition_stats
        if combined:
            dfs = []
            for date, df in self.portfolio_category_composition_stats.items():
                df['date'] = date
                dfs.append(df)
            final_df = pd.concat(dfs)
        return final_df

    def run(self):
        if len(self.portfolio_stocks+self.watchlist_stocks+self.index_tracker_stocks) > 0:
            self._derive_base_stock_data()
        if len(self.positions) > 0:
            self._derive_base_portfolio_data()
        for s in self.portfolio_stocks:
            self.portfolio_stock_stats[s.symbol] = self._calculate_portfolio_stats_for_stock(symbol=s.symbol)
        self.portfolio_aggregate_stats = self._aggregate_portfolio_stock_stats()
        for i in range(0, len(self.portfolio_market_dates)):
            date = self.portfolio_market_dates[i]
            stock_c, category_c = self._calculate_portfolio_composition_stats(index=i)
            self.portfolio_stock_composition_stats[date] = stock_c
            self.portfolio_category_composition_stats[date] = category_c
