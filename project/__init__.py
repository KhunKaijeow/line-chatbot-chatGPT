from flask import Flask,request,abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import requests
import json
from project.Config import *
from flask_allowedhosts import limit_hosts
from openai import OpenAI
from project.Config import *



app = Flask(__name__)

ALLOWED_HOST= ['localhost', '127.0.0.1']


client = OpenAI(api_key=api_key)


def get_btc_price():
    """
    Get the current price of Bitcoin
    :return:
    """
    response = requests.get('https://api.coindesk.com/v1/bpi/currentprice.json')
    data = response.json()
    price = data['bpi']['USD']['rate']
    message = f'Bitcoin price is {price} USD '
    return message


@app.route('/', methods=['GET'])
@limit_hosts(allowed_hosts=ALLOWED_HOST)
def hello():
    return 'Hello, World!'

@app.route('/webhook', methods=['POST','GET'])
@limit_hosts(allowed_hosts=ALLOWED_HOST)
def webhook():
    """
    Get the message from the user and reply back
    :return:
    """
    if request.method == 'POST':
        payload = request.json
        print(f'Payload: {payload}')
        Reply_token = payload['events'][0]['replyToken']
        print(f'Reply_token: {Reply_token}')
        message = payload['events'][0]['message']['text']
        print(f'Message: {message}')

        # Check if the message contains the word 'btc' or 'bitcoin' and get the current price of Bitcoin
        if 'btc' in message or 'BTC' in message or 'Bitcoin' in message or 'bitcoin' in message or 'BITCOIN' in message:
            price = get_btc_price()
            ReplyMessage(Reply_token, price, channel_access_token)
        elif 'course' in message or 'Course' in message:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": f"Give me for a popular of {message}"},
                    {"role": "user",
                     "content": f'{message}'},
                ],
                max_tokens=350,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            print(completion.choices[0].message.content)
            ReplyMessage(Reply_token, completion.choices[0].message.content, channel_access_token)
        else:
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system",
                     "content": f"{message}"},
                    {"role": "user",
                     "content": f'{message}'},
                ],
                max_tokens=350,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            print(completion.choices[0].message.content)
            ReplyMessage(Reply_token, completion.choices[0].message.content, channel_access_token)

        return request.json, 200
    
    elif request.method == 'GET':
        return 'This is method GET!!!', 200
    
    else:
        abort(400)

def ReplyMessage(Reply_token, TextMessage, line_Acees_Token):
    """
    Reply to the user with the message
    :param Reply_token:
    :param TextMessage:
    :param line_Acees_Token:
    :return:
    """
    LINE_API = 'https://api.line.me/v2/bot/message/reply'

    Authorization = 'Bearer {}'.format(line_Acees_Token)
    print(Authorization)
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': Authorization
    }

    data = {
        "replyToken": Reply_token,
        "messages": [{"type": "text", "text": TextMessage}]
    }

    data = json.dumps(data)
    print(f'data: {data}')
    r = requests.post(LINE_API, headers=headers, data=data)
    return 200