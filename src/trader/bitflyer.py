from . import api_requester
import time
import json
import hmac
import hashlib
import requests
import urllib

API_KEY = ''
API_SECRET = ''

base_url = 'https://api.bitflyer.com'


def set_api_key_secret(api_key, api_secret):
    global API_KEY, API_SECRET
    API_KEY = api_key
    API_SECRET = api_secret


def set_api_key_secret_file(fname):
    api_key, api_secret = open(fname).read().split('\n')[0:2]
    global API_KEY, API_SECRET
    API_KEY = api_key
    API_SECRET = api_secret


def send_request(method, endpoint, body=None):
    url = base_url + endpoint
    if method.lower() == 'get':
        if body is not None:
            d_qs = urllib.parse.urlencode(body)
            endpoint += f'?{d_qs}'
            url = base_url + endpoint
        headers = get_header(method, endpoint, None)
        response = api_requester.get(url, headers)
    elif method.lower() == 'post':
        headers = get_header(method, endpoint, body)
        if body is not None:
            body = json.dumps(body)
        response = api_requester.post(url, headers, body)
    else:
        raise Exception('unsupport method %s' % method)
    return response


def get_sign(timestamp, method, endpoint, body=None):
    if body is None:
        message = timestamp + method + endpoint
    else:
        message = timestamp + method + endpoint + json.dumps(body)
    signature = hmac.new(bytes(API_SECRET.encode('ascii')), bytes(message.encode('ascii')),
                         digestmod=hashlib.sha256).hexdigest()
    return signature


def get_header(method: str, endpoint: str, body: dict) -> dict:
    timestamp = str(time.time())
    signature = get_sign(timestamp, method, endpoint, body)
    # headers = {
    #     'Content-Type': 'application/json',
    #     'ACCESS-KEY': settings.api_key,
    #     'ACCESS-TIMESTAMP': timestamp,
    #     'ACCESS-SIGN': signature
    # }
    headers = {
        'Content-Type': 'application/json',
        'ACCESS-KEY': API_KEY,
        'ACCESS-TIMESTAMP': timestamp,
        'ACCESS-SIGN': signature
    }
    return headers


def get_balance():
    endpoint = '/v1/me/getbalance'

    return send_request('GET', endpoint)


def get_board(market='BTC_JPY'):
    endpoint = '/v1/getboard'
    body = {
        'product_code': market
    }
    return send_request('GET', endpoint, body)


def get_executions(**body):
    endpoint = '/v1/getexecutions'
    return send_request('GET', endpoint, body)


def get_parentorder(market='BTC_JPY'):
    endpoint = '/v1/me/getparentorders'
    body = {
        'product_code': market
    }
    return send_request('GET', endpoint, body)


def get_childorder(market='BTC_JPY', child_order_acceptance_id=None, **kargs):
    endpoint = '/v1/me/getchildorders'
    body = {
        'product_code': market
    }
    body.update(kargs)
    if child_order_acceptance_id is not None:
        body['child_order_acceptance_id'] = child_order_acceptance_id
    return send_request('GET', endpoint, body)


def get_tradding_comission(market='BTC_JPY'):
    endpoint = '/v1/me/gettradingcommission'
    body = {
        'product_code': market
    }
    return send_request('GET', endpoint, body)


def send_order(product_code='BTC_JPY', side=None, child_order_type='LIMIT', price=None, size=None,  minute_limit=300):
    if price is None or size is None or side is None:
        return {}

    endpoint = '/v1/me/sendchildorder'
    body = {
        "product_code": product_code,
        "child_order_type": child_order_type,
        "side": side,
        "price": price,
        "size": size,
        "minute_to_expire": minute_limit,
        "time_in_force": "GTC"
    }
    return send_request('POST', endpoint, body)


class PrivateApi:
    def __init__(self, api_key, api_secret, api_endpoint):
        self.api_key = api_key
        self.api_secret = api_secret
        self.api_endpoint = api_endpoint

    def post_api_call(self, path, body):
        body = json.dumps(body)
        method = 'POST'
        timestamp = str(time.time())
        text = timestamp + method + path + body
        sign = hmac.new(bytes(self.api_secret.encode('ascii')), bytes(
            text.encode('ascii')), hashlib.sha256).hexdigest()

        request_data = requests.post(
            self.api_endpoint+path, data=body, headers={
                'ACCESS-KEY': self.api_key,
                'ACCESS-TIMESTAMP': timestamp,
                'ACCESS-SIGN': sign,
                'Content-Type': 'application/json'
            }
        )

        return request_data


if __name__ == '__main__':
    body = {
        "product_code": 'BTC_JPY',
        "child_order_type": 'LIMIT',
        "side": 'BUY',
        "price": 10,
        "size": 0.01,
        "minute_to_expire": 1,
        "time_in_force": "GTC"
    }
    api = PrivateApi(format(API_KEY), format(
        API_SECRET), 'https://api.bitflyer.jp')
    result = api.post_api_call('/v1/me/sendchildorder', body).json()
    print(result)
    # print(get_tradding_comission())
