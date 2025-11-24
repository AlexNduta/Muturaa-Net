# portal/unifi_utils.py
import os
import requests
import json
import urllib3

# Disable the annoying SSL warnings that pop up when you launch a webpage without an SSL certificate
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TinyUnifiClient:
    """
    - A controller client for authorizinf clients to join a wifi network
    """
    def __init__(self):
        self.host = os.getenv('UNIFI_HOST')
        self.port = os.getenv('UNIFI_PORT')
        self.username = os.getenv('UNIFI_USER')
        self.password = os.getenv('UNIFI_PASS')
        self.base_url = f"https://{self.host}:{self.port}"
        
        # Create a session to store cookies (Login session)
        # this will kee us logged in
        self.session = requests.Session()
        self.session.verify = False # Ignore SSL Cert errors
        self.csrf_token = None

    def login(self):
        """
        - Logs into UniFi OS and gets the cookies/tokens needed
        - create the loggin url then authenticate 
        - send json data as payload 
        - make a post request to /api/auth/login
        """
        login_url = f"{self.base_url}/api/auth/login"
        payload = {'username': self.username, 'password': self.password}
        headers = {'Content-Type': 'application/json'}

        print(f"--- Logging in to {login_url} ---")
        
        try:
            r = self.session.post(login_url, json=payload, headers=headers)
            r.raise_for_status()
            
            # UniFi OS requires a CSRF token for future requests. 
            # It sends it in the headers of the login response.
            self.csrf_token = r.headers.get('x-csrf-token')
            print("--- Login Successful ---")
            return True
        except Exception as e:
            print(f"CRITICAL: Login Failed: {e}")
            raise e

    def authorize_guest(self, mac, minutes):
        """Sends the authorize command"""
        # UCG Ultra runs the Network App behind a proxy.
        # The path is /proxy/network/api/s/{site_id}/cmd/stamgr
        # stamgr is the station manager endpoint
        auth_url = f"{self.base_url}/proxy/network/api/s/default/cmd/stamgr"
        
    payload = {
            'cmd': 'authorize-guest',
            'mac': mac.lower(),
            'minutes': minutes
        }
        
        # We must include the CSRF token we got during login or the request will fail
        headers = {
            'Content-Type': 'application/json',
            'x-csrf-token': self.csrf_token
        }

        print(f"--- Authorizing {mac} ---")
        
        try:
            r = self.session.post(auth_url, json=payload, headers=headers)
            r.raise_for_status()
            print("--- Authorization Command Sent! ---")
            return True
        except Exception as e:
            print(f"Authorization Failed: {e}")
            if r is not None:
                print(f"Response: {r.text}")
            return False

# --- HELPER FUNCTION FOR VIEWS ---
def authorize_user(mac_address, minutes=60):
    """
    Wrapper function to be called by views.py
    - creates a client instace
    - logs in
    - Authorises the guest
    -
    """
    try:
        client = TinyUnifiClient()
        client.login()
        return client.authorize_guest(mac_address, minutes)
    except Exception as e:
        print(f"UniFi Error: {e}")
        return False
