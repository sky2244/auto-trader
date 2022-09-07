

def debug_output(COMPLETE_ORDER, orders):
    buy_orders = list(filter(lambda x: x.side == 'buy', COMPLETE_ORDER))
    sell_orders = list(filter(lambda x: x.side == 'sell', COMPLETE_ORDER))
    buy_price = sum(
        map(lambda x: x.price * x.size, buy_orders))
    sell_price = sum(
        map(lambda x: x.price * x.size, sell_orders))
    win_count = 0
    lose_count = 0
    for buy_order in buy_orders:
        sell_order = [x for x in sell_orders if x.pair_id == buy_order.id][0]
        if sell_order.price > buy_order.price:
            win_count += 1
        else:
            lose_count += 1
    # order_str = json.dumps([x.to_dict() for x in orders])
    # logging.debug('last buy orders %s', order_str)
    print(f'order count:{len(COMPLETE_ORDER)}')
    print(f'remaining order count:{len(orders)}')
    print(f'total_buy_price:{buy_price}')
    print(f'total_sell_price:{sell_price}')
    print(f'rate:{sell_price/buy_price}')
    print(f'win_count:{win_count}')
    print(f'lose_count:{lose_count}')
