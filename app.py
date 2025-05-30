# === Standard Library ===
import os

# === Third-Party Packages ===
from flask import Flask, request
from dotenv import load_dotenv
import requests
import joblib



# === Environment Setup ===
load_dotenv()
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/'
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# === prepare classifier ===
encoder = joblib.load("cv_encoder.pkl")  # Load the encoder
# Load the pre-trained model
model = joblib.load("lr_model.pkl")

# message_text = "Had your mobile 11 months or more? U R entitled to Update to the latest colour mobiles with camera for Free! Call The Mobile Update Co FREE on 08002986030"
# # run classification
# X_emb = encoder.transform([message_text])
# print(X_emb.shape)
# pred = model.predict(X_emb)
# print(pred)

# === Flask Application Setup ===

app = Flask(__name__)

# Register the startup function
with app.app_context():
    delete_webhook_url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteWebhook'
    response = requests.post(
        delete_webhook_url,
        json={'url': WEBHOOK_URL, 'drop_pending_updates': True}
    )

    # Then set the new webhook so Telegram knows where to send updates
    set_webhook_url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/setWebhook?url={WEBHOOK_URL}/webhook'

    response = requests.post(set_webhook_url, json={'url': WEBHOOK_URL})
    print(f"Webhook set: {response.json()}")


# Flask Routes ===

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
        requests.get(url + f'sendMessage?chat_id={chat_id}&text={"Send me some text: (or type /quit)"}')
        return 'OK', 200
    elif message_text.lower() == "/quit":
        requests.get(url + f'sendMessage?chat_id={chat_id}&text=Good%20Bye!')
        return 'OK', 200
    else:
        # show "typing..."
        send_action = url + f'sendChatAction?chat_id={chat_id}&action=typing'
        requests.get(send_action)

        # run classification
        X_emb = encoder.transform([message_text])
        print(X_emb.shape)
        pred = model.predict(X_emb)

        if pred=="ham":
            result = "Not Spam"
        else:
            result = "Spam"

        send_url = url + f'sendMessage?parse_mode=markdown&chat_id={chat_id}&text={result}'
        requests.get(send_url)

        requests.get(url + f'sendMessage?parse_mode=markdown&chat_id={chat_id}&text=Send me some text: (or type /quit)')
        return 'OK', 200

if __name__ == "__main__":
    app.run()