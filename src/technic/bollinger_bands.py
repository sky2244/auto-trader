from .algorithm import Algorithm


# bollinger_bands


class BB(Algorithm):
    def __init__(self, duration=20, sigma=2, is_output=False):
        # ボリンジャーバンドの期間（基本は20）
        self.duration = duration
        # σの値
        self.sigma = sigma

        self.is_output = is_output

    def difference(self, df, key):
        """
        上昇下降トレンドによる判定
        :rtype: object
        """
        df['diff'] = df[key].diff()

        # 下降→上昇
        buy_flg = df.iloc[-2]['diff'] < 0 < df.iloc[-1]['diff']
        # 上昇→下降
        sell_flg = df.iloc[-2]['diff'] > 0 > df.iloc[-1]['diff']

        print(str(df.iloc[-2]['diff']) + ' -> ' + str(df.iloc[-1]['diff']))

        return self.create_result(buy_flg, sell_flg)

    def get_result(self, df, key):
        """
        ボリンジャーバンドによる判定
        :rtype: object
        """

        # 移動平均
        df['SMA'] = df[key].rolling(window=self.duration).mean()
        # 標準偏差
        df['std'] = df[key].rolling(window=self.duration).std()

        # σ区間の境界線
        df['-' + str(self.sigma) + 'σ'] = df['SMA'] - self.sigma * df['std']
        df['+' + str(self.sigma) + 'σ'] = df['SMA'] + self.sigma * df['std']

        if self.is_output:
            print('-' + str(self.sigma) + 'σ: ' +
                  str(df.iloc[-1]['-' + str(self.sigma) + 'σ']))
            print('+' + str(self.sigma) + 'σ: ' +
                  str(df.iloc[-1]['+' + str(self.sigma) + 'σ']))

        # 最新の値段が±xσ区間を超えているか判定
        buy_flg = df.iloc[-1][key] < df.iloc[-1]['-' + str(self.sigma) + 'σ']
        sell_flg = df.iloc[-1][key] > df.iloc[-1]['+' + str(self.sigma) + 'σ']
        return self.create_result(buy_flg, sell_flg)
