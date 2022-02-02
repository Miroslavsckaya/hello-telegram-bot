from turtle import update
from unittest import expectedFailure
import requests
import sys


def send_message(token, id, text):
    response = requests.post(f'https://api.telegram.org/bot{token}/sendMessage', json={'chat_id': id, 'text': text})
    return response.status_code == 200


def get_updates(token, offset):
    response = requests.get(f'https://api.telegram.org/bot{token}/getUpdates', params={'offset': offset,'timeout': 60})

    if response.status_code != 200:
        print(f'Status code: {response.status_code}')
        return False

    try:
        updates = response.json()
    except requests.exceptions.JSONDecodeError:
        print('JSONDecodeError')
        return False
    
    if 'result' not in updates:
        print("'result' key don't exists'")
        return False

    return updates['result']




if len(sys.argv) != 2:
    print('Usage: ./hello_bot.py token')
    sys.exit(1)

token = sys.argv[1]
offset = -1

while True:
    updates = get_updates(token, offset)
    if updates:
        for update in updates:
            chat_id = update['message']['chat']['id']
            send_message(token, chat_id, 'Hello!')
        offset = updates[-1]['update_id'] + 1
