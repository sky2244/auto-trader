from technic.algorithm import Algorithm


import pandas as pd
import operator


class Sma(Algorithm):
    def __init__(self, short_num=5, long_num=18, continue_num=3):
        self.name = 'sma'
        self.short_num = short_num
        self.long_num = long_num
        self.continue_num = continue_num

    def get_result(self, candles, key):
        short_sma = self.make_sma(candles, self.short_num, key)  # 短期移動平均線を作成
        long_sma = self.make_sma(candles, self.long_num, key)  # 長期移動平均線を作成
        golden_cross = self.is_golden_cross(
            short_sma, long_sma)
        dead_cross = self.is_dead_cross(short_sma, long_sma)

        return self.create_result(golden_cross, dead_cross)

    def make_sma(self, candles, span, key):
        return pd.Series(candles[key]).rolling(window=span).mean()

    def is_cross(self, short_sma, long_sma, op):
        if self.continue_num < 1:
            raise Exception('use continue_num >= 1.')

        if len(short_sma) < self.continue_num + 1:
            return False

        elif len(long_sma) < self.continue_num + 1:
            return False

        for i in range(1, self.continue_num+1):
            if not op(short_sma.iloc[-i], long_sma.iloc[-i]):
                return False

        if op(short_sma.iloc[-(self.continue_num+1)], long_sma.iloc[-(self.continue_num+1)]):
            return False

        return True

    def is_golden_cross(self, short_sma, long_sma):
        return self.is_cross(short_sma, long_sma, operator.gt)

    def is_dead_cross(self, short_sma, long_sma):
        return self.is_cross(short_sma, long_sma, operator.lt)
