

class Algorithm:
    def __init__(self):
        self.name = ''

    def create_result(self, buy_flg, sell_flg):
        """
        アルゴリズム実行後のレスポンス
        :rtype: object
        """
        return {
            'buy_flg': buy_flg,
            'sell_flg': sell_flg
        }

    def get_result(self, candles, key):
        return self.create_result(False, False)
