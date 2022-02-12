from dotenv import load_dotenv
import requests
import os
import sqlite3


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


load_dotenv()

token = os.getenv('APY_KEY')
offset = -1

open('users.db', 'a').close()
conn = sqlite3.connect('users.db', isolation_level=None)

try:
    conn.execute('SELECT * FROM usernames')
except sqlite3.OperationalError:
    conn.execute('CREATE TABLE usernames (id INTEGER, username TEXT, PRIMARY KEY(id))')

while True:
    updates = get_updates(token, offset)
    
    if not updates:
        continue

    for update in updates:
        chat_id = update['message']['chat']['id']
        user_id = update['message']['from']['id']
        username = conn.execute('SELECT username FROM usernames WHERE id = ?', (user_id,)).fetchone()

        if 'text' in update['message']:
            text_words = update['message']['text'].split()
        else:
            text_words = []

        if len(text_words) > 1 and text_words[0] == '/name':
            username = text_words[1]

            conn.execute('INSERT INTO usernames VALUES (?, ?) ON CONFLICT (id) DO UPDATE SET username = ?', (user_id, username, username))

        if username:
            username = str(username).strip("(),'")
            send_message(token, chat_id, f'Hello, {username}')
        else:
            send_message(token, chat_id, r'Send me your name prepended with /name command')

        offset = update['update_id'] + 1
