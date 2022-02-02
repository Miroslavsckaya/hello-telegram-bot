import requests
import sys


def send_message(token, id, text):
    response = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', json={'chat_id': id, 'text': text})
    return response.status_code == 200


def get_message(token, offset):
    response = requests.get(f'https://api.telegram.org/bot{token}/getUpdates', params={'offset': offset,'timeout': 60})
    return response.json()


if len(sys.argv) != 2:
    print('Usage: ./hello_bot.py token')
    sys.exit(1)

token = sys.argv[1]
offset = -1

while True:
    message = get_message(token, offset)
    if message['ok'] and message['result']:
        chat_id = message['result'][0]['message']['chat']['id']
        send_message(token, chat_id, 'Hello!')
        offset = message['result'][0]['update_id'] + 1
