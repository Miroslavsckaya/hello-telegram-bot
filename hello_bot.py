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


def get_users(filename):
    with open(filename, 'a+', encoding='utf-8') as file:
        file.seek(0)
        return list(csv.DictReader(file, fieldnames=['user_id', 'name']))


def write_users(filename, users):
    with open(filename, 'w', encoding='utf-8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=['user_id', 'name'])
        for user in users:
            writer.writerow(user)


if len(sys.argv) < 2:
    print('Usage: ./hello_bot.py token')
    sys.exit(1)

token = sys.argv[1]
offset = -1

users = get_users('usernames.csv')

while True:
    updates = get_updates(token, offset)
    if updates:
        for update in updates:
            chat_id = update['message']['chat']['id']
            user_id = str(update['message']['from']['id'])
            username = ''
            index = -1

            for index, user in enumerate(users):
                if user['user_id'] == user_id:
                    username = user['name']
                    break

            text_words = update['message']['text'].split()
            if text_words[0] == '/name' and len(text_words) > 1:
                username = text_words[1]

                if index != -1:
                    users[index]['name'] = username
                else:
                    users.append({'user_id': user_id, 'name': username})
                           
            if username:
                send_message(token, chat_id, f'Hello, {username}')
            else:
                send_message(token, chat_id, r'Send me your name prepended with /name command')
    
            offset = update['update_id'] + 1

        write_users('usernames.csv', users)

