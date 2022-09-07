from mock import response

import uuid


class Operator:
    def __init__(self, trader, DEBUG):
        self.debug = DEBUG
        self.trader = trader

    def make_dummy_response(self):
        return response.MockResponse({
            "child_order_acceptance_id": "dummy-responce-"+str(uuid.uuid4())
        }, 200)

    def buy_operate(self, price, size, minute_limit=300):
        if self.debug:
            return self.make_dummy_response()
        return self.trader.send_order(side='BUY', child_order_type='LIMIT',
                                      price=price, size=size,
                                      minute_limit=minute_limit)

    def sell_operate(self, price, size, minute_limit=300):
        if self.debug:
            return self.make_dummy_response()
        return self.trader.send_order(side='SELL', child_order_type='LIMIT',
                                      price=price, size=size,
                                      minute_limit=minute_limit)
