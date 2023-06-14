# send_message.py
# 15-06-2023

import json
import requests

from config import ENV_PATH

def send_message(message, parse_mode='Markdown', chat_id=None, token=None, file=ENV_PATH):
    """
    Пример использования:
    message = f'Отправка сообщения из Colab: <b>[{my_id}]</b>'
    response = send_message(message, 'HTML')
    print(response)
    """
    if chat_id is None or token is None:
        with open(file) as f:
            data = json.load(f)
        token, chat_id = data.values()

    #print('\n', token, chat_id)
    #print('\n', message)
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    data = {'chat_id': chat_id, 'text': message, 'parse_mode': parse_mode}
    response = requests.post(url, json=data)
    return json.loads(response.text)
