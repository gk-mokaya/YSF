from flask import Flask, request, jsonify
import requests
import base64
import datetime
import hashlib
import os

app = Flask(__name__)

# Placeholder Safaricom API credentials
CONSUMER_KEY = "YOUR_CONSUMER_KEY"
CONSUMER_SECRET = "YOUR_CONSUMER_SECRET"
SHORTCODE = "YOUR_SHORTCODE"
PASSKEY = "YOUR_PASSKEY"
CALLBACK_URL = "https://yourdomain.com/callback"  # Replace with your callback URL

def get_access_token():
    """Get OAuth access token from Safaricom API"""
    auth_url = "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials"
    credentials = f"{CONSUMER_KEY}:{CONSUMER_SECRET}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()
    headers = {
        "Authorization": f"Basic {encoded_credentials}"
    }
    response = requests.get(auth_url, headers=headers)
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        return access_token
    else:
        return None

def lipa_na_mpesa_express(phone_number, amount):
    """Initiate Safaricom Express payment push"""
    access_token = get_access_token()
    if not access_token:
        return {"error": "Failed to get access token"}

    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data_to_encode = SHORTCODE + PASSKEY + timestamp
    password = base64.b64encode(data_to_encode.encode()).decode()

    api_url = "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "BusinessShortCode": SHORTCODE,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": amount,
        "PartyA": phone_number,
        "PartyB": SHORTCODE,
        "PhoneNumber": phone_number,
        "CallBackURL": CALLBACK_URL,
        "AccountReference": "YSF Donation",
        "TransactionDesc": "Donation to Youth Shield Foundation"
    }
    response = requests.post(api_url, json=payload, headers=headers)
    return response.json()

@app.route("/api/donate", methods=["POST"])
def donate():
    data = request.json
    phone_number = data.get("phone_number")
    amount = data.get("amount")
    if not phone_number or not amount:
        return jsonify({"error": "phone_number and amount are required"}), 400

    result = lipa_na_mpesa_express(phone_number, amount)
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
