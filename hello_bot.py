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


def get_username(conn, user_id):
    username = conn.execute('SELECT username FROM usernames WHERE id = ?', (user_id,)).fetchone()
    return '' if username is None else username[0]


def write_user(conn, user_id, username):
    conn.execute('INSERT INTO usernames VALUES (:id, :username) ON CONFLICT (id) DO UPDATE SET username = :username', {'id': user_id, 'username': username})


load_dotenv()

token = os.getenv('APY_KEY')
offset = -1

conn = sqlite3.connect('users.db', isolation_level=None)
conn.execute('CREATE TABLE IF NOT EXISTS usernames (id INTEGER, username TEXT, PRIMARY KEY(id))')

while True:
    updates = get_updates(token, offset)
    
    if not updates:
        continue

    for update in updates:
        chat_id = update['message']['chat']['id']
        user_id = update['message']['from']['id']
        username = get_username(conn, user_id)

        if 'text' in update['message']:
            text_words = update['message']['text'].split()
        else:
            text_words = []

        if len(text_words) > 1 and text_words[0] == '/name':
            username = text_words[1]

        if username:
            send_message(token, chat_id, f'Hello, {username}')
        else:
            send_message(token, chat_id, r'Send me your name prepended with /name command')

        write_user(conn, user_id, username)
        offset = update['update_id'] + 1
