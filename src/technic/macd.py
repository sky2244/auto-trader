from .algorithm import Algorithm

import pandas as pd


class Macd(Algorithm):
    def __init__(self, short_span=12, long_span=26, mid_span=9, is_output=False):
        self.name = 'macd'
        self.mid_span = mid_span
        self.short_span = short_span
        self.long_span = long_span
        self.is_output = is_output

    def get_result(self, df, key):
        """
        MACDによる判定
        :rtype: object
        """
        # http://www.algo-fx-blog.com/macd-python-technical-indicators/

        macd = pd.DataFrame()
        macd[key] = df[key]
        macd['ema_12'] = df[key].ewm(span=self.short_span).mean()
        macd['ema_26'] = df[key].ewm(span=self.long_span).mean()

        macd['macd'] = macd['ema_12'] - macd['ema_26']
        macd['signal'] = macd['macd'].ewm(span=self.mid_span).mean()
        macd['histogram'] = macd['macd'] - macd['signal']

        if self.is_output:
            print(str(macd.iloc[-2]['histogram']) +
                  ' -> ' + str(macd.iloc[-1]['histogram']))

        # ヒストグラムが負から正になったとき（MACDがシグナルを下から上に抜けるとき）
        buy_flg = macd.iloc[-2]['histogram'] < 0 < macd.iloc[-1]['histogram']
        # ヒストグラムが正の状態で減少したとき
        sell_flg = macd.iloc[-2]['histogram'] > 0 and macd.iloc[-2]['histogram'] > macd.iloc[-1]['histogram']
        return self.create_result(buy_flg, sell_flg)
