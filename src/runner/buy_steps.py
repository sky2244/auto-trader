from .runner import Runner


class BuySteps(Runner):
    COMPLETE_ORDER = []

    def __init__(self, conf, trade_operator, debug,
                 debug_operation, algorithm, notify):
        super().__init__(conf['Steps'], trade_operator,
                         debug, debug_operation, algorithm, notify)
        self.max_buy = conf.getint('Steps/max_buy')
        self.buy_max_price = 6000000

    def auto_trade(self):
        self.pre_trade()
        current_price = self.candles[-1]['Close']

        result_flg = self.algorithm.get_result(self.candles, 'Close')
        if result_flg['buy_flg']:
            if self.is_buy(self.orders, current_price):
                self.buy_operate(current_price, self.size)
        elif result_flg['sell_flg']:
            self._sell_operate(current_price)

        if len(self.candles) > 3000:
            self.candles = self.candles[-1000:]
        self.dump_order()

    def search_sellable_order(self, price, target_profit):
        for order in self.orders:
            if not order.is_sellable(price, target_profit):
                continue

            return order
        return None

    def is_buy(self, buy_order, price):
        if len(buy_order) <= 2:
            return True

        if buy_order[0].price < price:
            return False
        if len(buy_order) >= self.max_buy:
            return False
        if price >= self.buy_max_price:
            return False

        return True

    def _sell_operate(self, current_price):
        if len(self.orders) == 0:
            return

        order = self.search_sellable_order(
            current_price, self.target_profit)
        if order is not None:
            self.sell_operate(order, current_price)
        else:
            min_buy_price = self.orders[-1].price
            self.notify(
                f"Not Sell request on "
                f"the market current:{current_price}, "
                f"last buy:{min_buy_price} "
                f"{(current_price / min_buy_price):2f}")
