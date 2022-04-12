import requests


class line_worker:
    def __init__(self):
        pass

    def send_notification(self, line_notify_token, message):
        print(message)
        url = "https://notify-api.line.me/api/notify"
        headers = {
            'Authorization': f"Bearer {line_notify_token}",
        }
        data = {
            "message": message,
        }
        requests.post(url, headers=headers, data=data)