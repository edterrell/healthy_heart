# token_manager
import requests
import json
import time
import os

# --- Configuration ---
CLIENT_ID = 167221
CLIENT_SECRET = 'f4df8e0dec7d9d8e725707eaf05037fcc845989d'
TOKEN_FILE = 'tokens.json'

def load_tokens():
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    else:
        raise FileNotFoundError("tokens.json not found. You need to do initial auth first.")

def save_tokens(tokens):
    with open(TOKEN_FILE, 'w') as f:
        json.dump(tokens, f)

def refresh_tokens(refresh_token):
    response = requests.post(
        'https://www.strava.com/api/v3/oauth/token',
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
    )
    if response.status_code == 200:
        new_tokens = response.json()
        save_tokens(new_tokens)
        return new_tokens
    else:
        raise Exception(f"Failed to refresh token: {response.status_code} - {response.text}")

def get_valid_access_token():
    tokens = load_tokens()
    if time.time() >= tokens['expires_at']:
        print("Access token expired. Refreshing...")
        tokens = refresh_tokens(tokens['refresh_token'])
    return tokens['access_token']
