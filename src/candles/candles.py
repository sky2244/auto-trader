from datetime import datetime
import pandas as pd
import requests


def get_init_candles(dummy_file=None):
    if dummy_file is not None:
        global debug_candles
        debug_candles = pd.read_csv(dummy_file).set_index('Time')
        candles = debug_candles[:1]
        debug_candles = debug_candles.drop(debug_candles.index[0])
    else:
        candles = get_candles(
            "minute", 1000).set_index("Time")
    return candles


def is_finished_candles():
    return len(debug_candles) == 0


def get_current_price(is_debug, trader):
    if is_debug:
        global debug_candles
        res = debug_candles['Close'][0]
        debug_candles = debug_candles.drop(debug_candles.index[0])
        return res
    else:
        current_board = trader.get_board()
        return current_board.json()['mid_price']


def get_candles(timeframe, limit):
    # timeframe（時間軸）には「minute（1分足）」「hour(1時間足)」「day(日足)」のいずれかが入る
    base_url = f"https://min-api.cryptocompare.com/data/histo{timeframe}"

    params = {
        "fsym": "BTC",  # 通貨名(The cryptocurrency symbol of interest)
        "tsym": "JPY",  # 通貨名(The currency symbol to convert into)
        "limit": limit,  # 取得件数(The number of data points to return)
    }

    res = requests.get(base_url, params, timeout=10).json()

    time, open, high, low, close = [], [], [], [], []

    for i in res["Data"]:
        time.append(datetime.fromtimestamp(i["time"]))
        open.append(i["open"])
        high.append(i["high"])
        low.append(i["low"])
        close.append(i["close"])

    candles = pd.DataFrame({
        "Time": time,  # 時刻
        # "Open": open,  # 始値
        # "High": high,  # 高音
        # "Low": low,    # 安値
        "Close": close  # 終値
    })

    return candles
