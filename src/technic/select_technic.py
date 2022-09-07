
from technic import sma, bollinger_bands, macd, rsi, bb_macd_rsi


def get_algorithm(algorithm):
    algorithm = algorithm.lower()
    if algorithm == 'sma':
        return sma.Sma()
    elif algorithm == 'bb':
        return bollinger_bands.BB()
    elif algorithm == 'macd':
        return macd.Macd()
    elif algorithm == 'rsi':
        return rsi.Rsi()
    elif algorithm == 'mix3':
        return bb_macd_rsi.BB_Macd_Rsi()
    else:
        raise Exception()
