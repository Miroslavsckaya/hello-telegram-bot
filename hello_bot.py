import requests
import csv
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



if len(sys.argv) < 2:
    print('Usage: ./hello_bot.py token')
    sys.exit(1)

token = sys.argv[1]
offset = -1

while True:
    updates = get_updates(token, offset)
    if updates:
        with open('usernames.csv', 'a+', encoding='utf-8', newline='') as file:
            for update in updates:
                chat_id = update['message']['chat']['id']
                user_id = update['message']['from']['id']
                
                f = csv.DictWriter(file, fieldnames=['user_id', 'name'])
                if not file.tell():
                    f.writeheader()

                text_words = update['message']['text'].split()
                if '/name' in text_words and text_words[-1] != '/name':
                    index = text_words.index('/name')
                    username = text_words[index +  1]
                    send_message(token, chat_id, f'Hello, {username}')

                    f.writerow({'user_id': user_id, 'name': username})
                else:
                    send_message(token, chat_id, "What's your name?")
    
        offset = updates[-1]['update_id'] + 1
