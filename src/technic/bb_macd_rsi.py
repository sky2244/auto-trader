from technic.algorithm import Algorithm
from technic import macd, rsi, bollinger_bands


class BB_Macd_Rsi(Algorithm):
    def __init__(self):
        self.bb = bollinger_bands.BB()
        self.macd = macd.Macd()
        self.rsi = rsi.Rsi()
        pass

    def get_result(self, df, key):
        """
        ボリンジャーバンド・MACD・RSIによる判定
        :rtype: object
        """
        # ボリンジャーバンド
        bollinger_bands_result = self.bb.get_result(df, key)
        # MACD
        macd_result = self.macd.get_result(df, key)
        # RSI
        rsi_result = self.rsi.get_result(df, key)

        buy_flg_count = 0
        sell_flg_count = 0

        if bollinger_bands_result['buy_flg']:
            buy_flg_count += 1
        if bollinger_bands_result['sell_flg']:
            sell_flg_count += 1
        if macd_result['buy_flg']:
            buy_flg_count += 1
        if macd_result['sell_flg']:
            sell_flg_count += 1
        if rsi_result['buy_flg']:
            buy_flg_count += 1
        if rsi_result['sell_flg']:
            sell_flg_count += 1

        buy_flg = buy_flg_count >= 2
        sell_flg = sell_flg_count >= 2

        return self.create_result(buy_flg, sell_flg)
