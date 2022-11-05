from db import database
from candles import candles
from order import Order
from trader import bitflyer


class Runner:
    def __init__(self, conf, trade_operator, debug,
                 debug_operation, algorithm, notify):
        self.size = conf.getfloat('size')
        self.target_profit = conf.getfloat('target')
        self.dump_file_name = conf.get('Runner/dump_file', 'dump_order.txt')

        self.trade_operator = trade_operator
        self.debug = debug
        self.debug_operation = debug_operation
        self.algorithm = algorithm
        self.notify = notify

        self.candles = candles.get_init_candles()
        self.orders = self.init_server_order(debug)
        self.db = database.DB('../auto_trade.db', 'trade',
                              Order.k, Order.k_t, 'id')

    def pre_trade(self):
        current_price = candles.get_current_price(self.debug, bitflyer)
        self.candles = self.candles.append(
            {'Close': current_price}, ignore_index=True)
        self.update_order_state(self.debug or self.debug_operation)
        self.update_buy_order_state()
        self.trim_finished_order()
