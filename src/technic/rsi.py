from .algorithm import Algorithm


class Rsi(Algorithm):
    def __init__(self, duration=14, rsi_low=30, rsi_up=70, is_output=False):
        # RSIの期間（基本は14）
        self.duration = 14

        self.rsi_low = rsi_low
        self.rsi_up = rsi_up

        self.is_output = is_output

    def get_result(self, df, key):
        """
        RSIによる判定
        :rtype: object
        """
        # http://www.algo-fx-blog.com/rsi-python-ml-features/

        df['diff'] = df[key].diff()
        # 最初の欠損レコードを切り落とす
        diff = df['diff'][1:]

        # 値上がり幅、値下がり幅をシリーズへ切り分け
        up, down = diff.copy(), diff.copy()
        up[up < 0] = 0
        down[down > 0] = 0

        # 値上がり幅/値下がり幅の単純移動平均（14)を処理
        up_sma = up.rolling(window=self.duration, center=False).mean()
        down_sma = down.abs().rolling(window=self.duration, center=False).mean()

        # RSIの計算
        df['rs'] = up_sma / down_sma
        df['rsi'] = 100.0 - (100.0 / (1.0 + df['rs']))
        if self.is_output:
            print('RSI: ' + str(df['rsi'].iloc[-1]))

        buy_flg = float(df['rsi'].iloc[-1]) < self.rsi_low
        sell_flg = float(df['rsi'].iloc[-1]) > self.rsi_up
        return self.create_result(buy_flg, sell_flg)
