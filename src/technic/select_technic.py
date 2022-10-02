
from technic import sma, bollinger_bands, macd, rsi, bb_macd_rsi


def get_algorithm(algorithm_name):
    if algorithm_name == 'sma':
        return sma.Sma()
    elif algorithm_name == 'bb':
        return bollinger_bands.BB()
    elif algorithm_name == 'macd':
        return macd.Macd()
    elif algorithm_name == 'rsi':
        return rsi.Rsi()
    elif algorithm_name == 'mix3':
        return bb_macd_rsi.BB_Macd_Rsi()
    else:
        raise Exception()
