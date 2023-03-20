from .runner import Runner


class Scalping(Runner):
    COMPLETE_ORDER = []

    def __init__(self, conf, trade_operator, debug,
                 debug_operation, algorithm, notify):
        super().__init__(conf['Scalping'], trade_operator,
                         debug, debug_operation, algorithm, notify)
        self.loss_profit = conf.getfloat('Scalping/loss')

        self.minute_limit = 5

    def auto_trade(self):
        self.pre_trade()
        current_price = self.candles[-1]['Close']

        if len(self.orders) == 0:
            result_flg = self.algorithm.get_result(self.candles, 'Close')
            if result_flg['buy_flg']:
                self.buy_operate(current_price, self.size, self.minute_limit)
        else:
            self._sell_operate(current_price)

        if len(self.candles) > 10000:
            self.candles = self.candles[-5000:]
        self.dump_order()

    def search_sellable_order(self, price):
        for order in self.orders:
            if not order.is_sellable(price, self.target_profit):
                continue

            if price > self.candles.iloc[-2]['Close']:
                continue
            return order
        for order in reversed(self.orders):
            if not order.is_sellable(price, self.loss_profit, loss_cut=True):
                continue

            return order
        return None

    def _sell_operate(self, current_price):
        if len(self.orders) == 0:
            return

        order = self.search_sellable_order(current_price)
        if order is not None:
            self.sell_operate(order, current_price, self.minute_limit)
        else:
            min_buy_price = self.orders[-1].price
            self.notify(
                f"Not Sell request on "
                f"the market current:{current_price}, "
                f"last buy:{min_buy_price} "
                f"{(current_price / min_buy_price):2f}")
