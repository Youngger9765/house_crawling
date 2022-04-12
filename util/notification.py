import requests


class LineWorker:
    def __init__(self, line_notify_token):
        self.line_notify_token = line_notify_token
        pass

    def send_notification(self, message):
        line_notify_token = self.line_notify_token
        print(message)
        url = "https://notify-api.line.me/api/notify"
        headers = {
            'Authorization': f"Bearer {line_notify_token}",
        }
        data = {
            "message": message,
        }
        requests.post(url, headers=headers, data=data)