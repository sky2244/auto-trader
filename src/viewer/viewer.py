from flask import Flask, jsonify, request
import threading

app = Flask(__name__, static_folder='.', static_url_path='')

runner = None


def set_runner(r):
    global runner
    runner = r


def run():
    view_thread = threading.Thread(target=server_run)
    view_thread.start()


@app.route('/')
def index():
    return 'hello world'


@app.route('/view-all', methods=['GET'])
def view_all():
    res = {
        'data': [order.to_dict() for order in runner.orders],
        'count': len(runner.orders),
    }
    return jsonify(res)


@app.route('/order/<order_id>', methods=['GET'])
def view_order(order_id):
    target = filter(lambda x: order_id in [x.buy_id, x.sell_id], runner.orders)

    res = {
        'data': [order.to_dict() for order in target]
    }
    code = 200
    if len(res['data']) == 0:
        res['msg'] = f'not found order: {order_id}'
        code = 400
    return jsonify(res), code


@app.route('/set_profit')
def set_profit():
    profit = request.args.get('profit')

    if profit is None:
        res = {
            'msg': f'invalid parameter profit:{profit}'
        }
        return jsonify(res), 400

    bef_profit = runner.target_profit
    runner.target_profit = float(profit)
    res = {
        'msg': f'change profit {bef_profit}->{profit}'
    }
    return jsonify(res)


@app.route('/buy_order')
def buy_order():
    price = request.args.get('price')
    size = request.args.get('size')

    if price is None:
        res = {
            'msg': f'invalid parameter price:{price}'
        }
        return jsonify(res), 400
    if size is None:
        size = runner.size

    price = int(price)
    size = float(size)
    buy_res = runner.buy_operate(price, size)
    if not buy_res:
        res = {
            'msg': 'buy request error'
        }
        return jsonify(res), 400
    res = {
        'msg': f'buy request price:{price}, size:{size}'
    }
    return jsonify(res)


@app.route('/sell_order')
def sell_order():
    order_id = request.args.get('order_id')
    price = request.args.get('price')

    if order_id is None or price is None:
        res = {
            'msg': f'invalid parameter order_id:{order_id}, price:{price}'
        }
        return jsonify(res), 400
    target = list(filter(lambda x: order_id == x.buy_id, runner.orders))
    if len(target) != 1:
        res = {
            'data': [order.to_dict() for order in target],
            'msg': f'not found or find some order: {order_id}'
        }
        return jsonify(res), 400

    price = int(price)
    sell_res = runner.sell_operate(target[0], price)
    if not sell_res:
        res = {
            'msg': 'sell request error'
        }
        return jsonify(res), 400

    res = {
        'data': [order.to_dict() for order in target],
        'msg': f'sell request {price}'
    }
    return jsonify(res)


def server_run(port=8000, debug=False):
    app.run(host='0.0.0.0', port=port, debug=debug)
