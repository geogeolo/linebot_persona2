from flask import Flask, render_template, request, redirect, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os
import time
import json

# Load persona configuration
with open('persona.json') as f:
    personas = json.load(f)

impersonated_role = personas['dream_interpreter']['content']

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# Initialize the message counter
message_counter = 0

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global message_counter
    message_counter += 1  # Increment the message counter
    text1 = event.message.text

    # Constructing a message that includes a language instruction
    instruction_message = "以下的回應請使用繁體中文。"

    
      response = openai.ChatCompletion.create(
        messages=[
            {"role": "system", "content": f"{instruction_message}, {impersonated_role}"},
            {"role": "user", "content": text1}
        ],
        model="gpt-3.5-turbo-0125",
        temperature=0.5,
    )
    try:
        ret = response['choices'][0]['message']['content'].strip()
    except:
        ret = '發生錯誤！'
    
    # Append the counter to the response
    ret_with_count = f"{ret}\n\n訊息計數: {message_counter}"  # "Message Count" in Traditional Chinese
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=ret_with_count))

if __name__ == '__main__':
    app.run()
