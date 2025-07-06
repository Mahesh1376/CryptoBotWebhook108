from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv
import hmac
import hashlib
import time

load_dotenv()
app = Flask(__name__)

# Delta Exchange API credentials
API_KEY = os.getenv("p0nZmlwl5XjNBo5XktEiu3DVhaSq5N")
API_SECRET = os.getenv("DPlwkY0t5uriMNQ44uIwImytDyFJXL3jSbOj2VOcyH76gXGfkykvN3jLFCyq")

BASE_URL = "https://api.delta.exchange"

# Function to create signature
def get_signature(api_secret, request_path, body, timestamp):
    message = f'{timestamp}{request_path}{body}'
    signature = hmac.new(api_secret.encode(), message.encode(), hashlib.sha256).hexdigest()
    return signature

# Send order to Delta
def send_order_to_delta(symbol, side, size):
    url_path = "/v2/orders"
    url = BASE_URL + url_path
    timestamp = str(int(time.time() * 1000))

    body = {
        "product_id": symbol,
        "size": size,
        "side": side,
        "order_type": "market",
        "post_only": False
    }

    body_str = str(body).replace("'", '"')  # proper JSON format
    signature = get_signature(API_SECRET, url_path, body_str, timestamp)

    headers = {
        "api-key": API_KEY,
        "timestamp": timestamp,
        "signature": signature,
        "Content-Type": "application/json"
    }

    response = requests.post(url, json=body, headers=headers)
    return response.json()

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received alert:", data)

    if "LONG" in data['message']:
        response = send_order_to_delta(symbol="BTCUSDT", side="buy", size=1)
    elif "SHORT" in data['message']:
        response = send_order_to_delta(symbol="BTCUSDT", side="sell", size=1)
    else:
        response = {"status": "ignored"}

    return jsonify(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
