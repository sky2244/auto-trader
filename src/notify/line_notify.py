import requests
import os


class LineNotify:
    def __init__(self, token=None, toke_file=None):
        if token is not None:
            self.line_notify_token = token
        else:
            if toke_file is None:
                toke_file = os.path.join(os.environ['HOME'], '.line_token')
            self.line_notify_token = open(toke_file).read().strip()
        self.line_notify_api = "https://notify-api.line.me/api/notify"
        self.headers = {
            "Authorization": f"Bearer {self.line_notify_token}"
        }

    def send(self, msg):
        msg = {"message": f" {msg}"}
        requests.post(self.line_notify_api, headers=self.headers, data=msg)
