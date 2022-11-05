from candles import candles
from db import database
from order import Order
from .runner import Runner
from trader import bitflyer

import logging
import json
import os


class Scalping(Runner):
    COMPLETE_ORDER = []

    def __init__(self, conf, trade_operator, debug,
                 debug_operation, algorithm, notify):
        self.target_profit = conf.getfloat('Scalping/target')
        self.loss_profit = conf.getfloat('Scalping/loss')
        self.size = conf.getfloat('Scalping/size')
        self.dump_file_name = conf.get('Runner/dump_file', 'dump_order.txt')

        self.minute_limit = 5

        self.trade_operator = trade_operator
        self.debug = debug
        self.debug_operation = debug_operation
        self.algorithm = algorithm
        self.notify = notify

        self.candles = candles.get_init_candles()
        self.orders = self.init_server_order(debug)
        self.db = database.DB('../auto_trade.db', 'trade',
                              Order.k, Order.k_t, 'id')

    def auto_trade(self):
        current_price = candles.get_current_price(self.debug, bitflyer)
        self.candles = self.candles.append(
            {'Close': current_price}, ignore_index=True)
        self.update_order_state(self.debug or self.debug_operation)
        self.update_buy_order_state()
        self.trim_finished_order()

        if len(self.orders) == 0:
            result_flg = self.algorithm.get_result(self.candles, 'Close')
            if result_flg['buy_flg']:
                self.buy_operate(current_price, self.size)
        else:
            order = self.search_sellable_order(current_price)
            if order is None:
                if len(self.orders) > 0:
                    min_buy_price = self.orders[-1].price
                    logging.debug(
                        f"Not Sell request on the market current:{current_price}, last buy:{min_buy_price} {(current_price / min_buy_price):2f}")
            else:
                self.sell_operate(order, current_price)

        if len(self.candles) > 10000:
            self.candles = self.candles[-5000:]
        self.dump_order()

    def trim_finished_order(self):
        finished_order = list(
            filter(lambda x: x.delete_flag and x.order_complete, self.orders))
        for order in finished_order:
            self.db.insert(order.get_data())

            self.COMPLETE_ORDER.append(order)
        self.orders = list(filter(lambda x: not x.delete_flag, self.orders))

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

    def buy_operate(self, price, size):
        operate = self.trade_operator.buy_operate(
            price, size, self.minute_limit)
        if operate.status_code != 200:
            self.notify(
                f"Buy request error price: {price}, {operate.text}")
            return False

        child_order_acceptance_id = operate.json()['child_order_acceptance_id']
        buy_order = Order('buy', price, size, child_order_acceptance_id)
        self.orders.append(buy_order)
        self.orders = sorted(self.orders, key=lambda x: x.price, reverse=True)
        self.notify(
            f"Buy request on the market {price}, {len(self.orders)}")
        return True

    def sell_operate(self, order, price):
        operate = self.trade_operator.sell_operate(
            price, order.size, self.minute_limit)
        if operate.status_code != 200:
            self.notify(f"Sell request error {operate.text}")
            return False

        self.notify(
            f"Sell request on the market {price} buy {order.price}")
        sell_order = Order('sell', price, order.size,
                           operate.json()['child_order_acceptance_id'])
        sell_order.pair_id = order.id
        order.pair_id = sell_order.id
        self.orders.append(sell_order)
        return True

    def close(self):
        self.db.close()

    def init_server_order(self, debug=False):
        res = []
        if os.path.exists(self.dump_file_name):
            load_json = json.load(open(self.dump_file_name))
            for order in load_json:
                res.append(Order(**order))
            self.remove_no_exist_pair_id(res)
            return res
        elif debug:
            return res

        return res
        child_order = bitflyer.get_childorder()
        for order in child_order.json():
            price = order['price']
            size = order['size']
            child_order_acceptance_id = order['child_order_acceptance_id']
            o = Order(price, size,  child_order_acceptance_id)
            if order['side'] == 'BUY':
                if order['child_order_state'] == 'COMPLETED':
                    o.buy_complete = True
            else:
                o.buy_complete = True
                o.send_sell_request = True
            res.append(o)
        return res

    def remove_no_exist_pair_id(self, orders):
        buy_orders = list(
            filter(lambda x: x.side == 'buy' and (x.pair_id is not None), orders))
        sell_orders = list(filter(lambda x: x.side == 'sell', orders))
        for order in buy_orders:
            target_orders = [x for x in sell_orders if x.id == order.pair_id]
            if len(target_orders) == 0:
                order.pair_id = None

    def update_order_state(self, debug):
        if len(self.orders) == 0:
            return

        if debug:
            for order in self.orders:
                order.update_state('COMPLETED')
            return

        MAX_RETRY = 3
        child_order = bitflyer.get_childorder(count=1000)
        id_key = 'child_order_acceptance_id'
        id_maps = {x[id_key]: x for x in child_order.json()}
        for order in self.orders:
            if order.order_complete:
                continue

            if order.id not in id_maps:
                self.notify(f"not found {order.id} order:{order}")
                order.retry += 1
                if order.retry >= MAX_RETRY:
                    self.notify(f"remove {order.side} order:{order}")
                    order.update_state('CANCELED')
            else:
                order_state = id_maps[order.id]['child_order_state']
                order.update_state(order_state)
                order.order_time = id_maps[order.id]['child_order_date']
                order.commission = id_maps[order.id]['total_commission']

    def update_buy_order_state(self):
        buy_orders = list(filter(lambda x: x.side == 'buy', self.orders))
        sell_orders = list(
            filter(lambda x: x.side == 'sell' and x.delete_flag, self.orders))
        for sell_order in sell_orders:
            buy_order = [x for x in buy_orders if x.pair_id == sell_order.id]
            if len(buy_order) == 0:
                self.notify('buy order not found')
                continue

            buy_order = buy_order[0]
            if sell_order.order_complete:
                buy_order.delete_flag = True
                profit = (sell_order.price - buy_order.price) * sell_order.size
                profit_rate = sell_order.price / buy_order.price
                self.notify(
                    f"Sell request complete {sell_order.price}"
                    f"buy {buy_order.price} profit:{profit:2f} {profit_rate:2f}")
            else:
                buy_order.reset_pair_id()

    def dump_order(self):
        if self.debug or self.debug_operation:
            return

        order_dicts = [x.to_dict() for x in self.orders]
        with open(self.dump_file_name, 'w') as fout:
            fout.write(json.dumps(order_dicts))
