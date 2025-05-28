# === Standard Library ===
import os

# === Third-Party Packages ===
from flask import Flask, request
from dotenv import load_dotenv
import requests
import joblib

# === Environment Setup ===
load_dotenv()
TELEGRAM_BERT_API_KEY = os.getenv('TELEGRAM_BERT_API_KEY')
url = f'https://api.telegram.org/bot{TELEGRAM_BERT_API_KEY}/'

# === prepare classifier ===
model = joblib.load("model.pkl")
from sentence_transformers import SentenceTransformer
encoder = SentenceTransformer('bert-base-nli-mean-tokens')


app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    return 'Flask is running...'

@app.route('/webhook', methods=['POST'])
def telegram_webhook():
    data = request.get_json()  # Parse JSON payload
    message = data.get('message')
    
    chat_id = message['chat']['id']
    message_text = message.get('text', '')

    if message_text.lower() == '/start':
        requests.get(url + f'sendMessage?chat_id={chat_id}&text={"Send me some text: (or type quit)"}')
        return 'OK', 200
    elif message_text.lower() == "/quit":
        requests.get(url + f'sendMessage?chat_id={chat_id}&text=Good%20Bye!')
        return 'OK', 200
    else:
        # show "typing..."
        send_action = url + f'sendChatAction?chat_id={chat_id}&action=typing'
        requests.get(send_action)

        # run classification
        X_emb = encoder.encode(message_text)
        pred = model.predict([X_emb])
        if pred=="ham":
            result = "Not Spam"
        else:
            result = "Spam"

        send_url = url + f'sendMessage?parse_mode=markdown&chat_id={chat_id}&text={result}'
        requests.get(send_url)

        requests.get(url + f'sendMessage?parse_mode=markdown&chat_id={chat_id}&text=Send me some text: (or type quit)')
        return 'OK', 200
