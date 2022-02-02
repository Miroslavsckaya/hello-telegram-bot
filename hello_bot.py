import requests


def send_message(token, id, text):
    response = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', json={'chat_id': id, 'text': text})
    return response.status_code == 200


def get_message(token, offset):
    response = requests.get(f'https://api.telegram.org/bot{token}/getUpdates', params={'offset': offset,'timeout': 60})
    return response.json()


