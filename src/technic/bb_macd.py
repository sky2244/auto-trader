from .algorithm import Algorithm

import pandas as pd


class BB_macd(Algorithm):
    def __init__(self):
        pass


def hybrid(df, key):
    """
    ボリンジャーバンドとMACDによる判定
    :rtype: object
    """
    # ボリンジャーバンドの期間（基本は20）
    duration = 20
    # σの値
    sigma = 2

    # 移動平均
    df['SMA'] = df[key].rolling(window=duration).mean()
    # 標準偏差
    df['std'] = df[key].rolling(window=duration).std()

    # σ区間の境界線
    df['-' + str(sigma) + 'σ'] = df['SMA'] - sigma * df['std']
    df['+' + str(sigma) + 'σ'] = df['SMA'] + sigma * df['std']

    print('-' + str(sigma) + 'σ: ' + str(df.iloc[-1]['-' + str(sigma) + 'σ']))
    print('+' + str(sigma) + 'σ: ' + str(df.iloc[-1]['+' + str(sigma) + 'σ']))

    # 最新の値段が±xσ区間を超えているか判定
    buy_flg = df.iloc[-1][key] < df.iloc[-1]['-' + str(sigma) + 'σ']

    macd = pd.DataFrame()
    macd[key] = df[key]
    macd['ema_12'] = df[key].ewm(span=12).mean()
    macd['ema_26'] = df[key].ewm(span=26).mean()

    macd['macd'] = macd['ema_12'] - macd['ema_26']
    macd['signal'] = macd['macd'].ewm(span=9).mean()
    macd['histogram'] = macd['macd'] - macd['signal']

    print(str(macd.iloc[-2]['histogram']) +
          ' -> ' + str(macd.iloc[-1]['histogram']))

    # ヒストグラムが減少したとき（ヒストグラムがプラス状態であるときのみ）
    sell_flg = macd.iloc[-2]['histogram'] > macd.iloc[-1]['histogram'] and macd.iloc[-2]['histogram'] > 0
    return create_result(buy_flg, sell_flg)
