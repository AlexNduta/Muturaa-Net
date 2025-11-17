import os
import requests
import base64
from requests.auth import HTTPBasicAuth
from datetime import datetime

# Sandbox URL for testing
SANDBOX_URL= "https://sandbox.safaricom.co.ke"

def get_daraja_token():
    """
    - fetches an Oauth access token from the safaricom Daraja API
    """
    print("Getting Daraja token..")

    consumer_key = os.getenv('DARAJA_CONSUMER_KEY')
    consumer_secret = os.getenv('DARAJA_CONSUMER_SECRET')


    if not consumer_key or not consumer_secret:
        raise Exception("M-Pesa Consumer Key or consumer secret is missing from the .env file")
    auth_url = f"{SANDBOX_URL}/oauth/v1/generate?grant_type=client_credentials"

    try:
        # make the request to safaricom
        response = requests.get(
                auth_url,
                auth=HTTPBasicAuth(consumer_key, consumer_secret)
                )
         # raise an error if the request failed
        response.raise_for_status()
        json_data = response.json()
        access_token = json_data['access_token']

        print("Successfully received Daraja token.")
        return access_token
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        print(f"Response content: {err.response.text}")
        raise
    except Exception as e:
        print(f"An error occurred: {e}")
        raise


def trigger_stk_push(phone_number, amount,  session_id):
    """
    - Initiates an Mpesa STK push to the user's phone
    """
    print(f"Triggering an STK push for {phone_number}....")
    # get a fresh access token
    access_token = get_daraja_token()

    shortcode = os.getenv('DARAJA_SHORTCODE')
    passkey = os.getenv('DARAJA_PASSKEY')
    callback_url = os.getenv('DARAJA_CALLBACK_URL')

    if not all([shortcode, passkey, callback_url]):
        raise Exception("M-Pesa Shortcode, Passkey or Callback URL is missing")
    # Generate a timestamp(YYYYMMDDHHMMSS)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    # Get an MPesa password: base64 encoding of (shortcode + Passkey + timestamp)
    password_data = f"{shortcode}{passkey}{timestamp}"
    password = base64.b64encode(password_data.encode()).decode('utf-8')

    # Define an API endpoint and header
    stk_push_url = f"{SANDBOX_URL}/mpesa/stkpush/v1/processrequest"
    headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
            }

    # The request payload- This is what we will send as data
    payload = {
            "BusinessShortCode": shortcode,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline", # Or CustomerBuyGoodsOnline 
            "Amount": str(amount),
            "PartyA": phone_number, # The user's phone number
            "PartyB": shortcode, # the business shortcode
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": "Hostspot", # A reference for the transaction
            "TransactionDesc": f"Wifi Access {session_id}" # A description
            }

    # Make the post Request
    try:
        response = requests.post(stk_push_url, json=payload, headers=headers)
        response.raise_for_status() #Raise an error in the case of a bad status

        json_data = response.json()
        print("STK Push initiated succesfully")


        # check if the request was accepted 
        if json_data.get('ResponseCode') == '0':
            return json_data.get('CheckoutRequestID')
        else:
            raise Exception(f"M-pesa error: {json_data.get(Responsedescription)}")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP Error: {err}")
        print(f"Response content: {err.response.text}")
        raise
    except Exception as e:
        print(f"An error occured: {e}")
        raise
