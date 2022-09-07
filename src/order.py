

class Order:
    k = ['side', 'price', 'size', 'id', 'pair_id',
         'order_complete', 'delete_flag', 'order_time', 'commission']
    k_t = [str, int, float, str, str, int, int, str, float]

    def __init__(self, side, price, size, id, pair_id=None,
                 order_complete=False, delete_flag=False,
                 order_time=None, commission=None):
        self.side = side.lower()
        self.price = price
        self.size = size
        self.id = id
        self.pair_id = pair_id
        self.order_complete = order_complete
        self.delete_flag = delete_flag
        self.order_time = order_time
        self.retry = 0
        self.state = ''
        self.commission = commission

    def keys(self):
        return self.k

    def __str__(self):
        vals = []
        for key in self.keys():
            val = getattr(self, key)
            vals.append(f'{key}:{val}')
        return ','.join(vals)

    def is_sellable(self, sell_price, threshold, loss_cut=False):
        if self.side == 'sell':
            return False
        elif not self.order_complete:
            return False
        elif self.pair_id is not None:
            return False

        if loss_cut:
            return (sell_price/self.price) < threshold

        return (sell_price/self.price) > threshold

    def to_string(self):
        return self.__str__()

    def get_data(self):
        return [getattr(self, k) for k in self.keys()]

    def to_dict(self):
        d = {}
        for key in self.keys():
            val = getattr(self, key)
            d[key] = val
        return d

    def update_state(self, order_state):
        if self.side == 'buy':
            self.update_buy_state(order_state)
        else:
            self.update_sell_state(order_state)

    def update_buy_state(self, order_state):
        if self.order_complete:
            return

        if order_state == 'COMPLETED':
            self.order_complete = True
        elif order_state in ['REJECTED', 'EXPIRED', 'CANCELED']:
            self.delete_flag = True
        self.state = order_state

    def update_sell_state(self, order_state):
        if self.id is None:
            return

        if order_state == 'COMPLETED':
            self.order_complete = True
            self.delete_flag = True
        elif order_state in ['REJECTED', 'EXPIRED', 'CANCELED']:
            self.delete_flag = True
            self.id = None
            # request delete?
        self.state = order_state

    def reset_pair_id(self):
        self.pair_id = None
