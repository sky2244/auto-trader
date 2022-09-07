import requests


def get(url, headers):
    return requests.get(url, headers=headers)


def post(url, headers, payload):
    return requests.post(url, headers=headers, data=payload)
