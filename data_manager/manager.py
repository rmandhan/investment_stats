import yf_positions_reader
import tiingo_api
import iex_api
import stock_file_reader

def testing():
    yf_positions_reader.test()
    tiingo_api.test()
    iex_api.test()
    stock_file_reader.test()

testing()
