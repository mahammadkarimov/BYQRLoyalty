import requests
from django.conf import settings
from dotenv import load_dotenv
import os

load_dotenv()

ACCESS_TOKEN = None


def get_access_token():
    """
    Fetches a new access token from the API if one doesn't exist.
    """
    global ACCESS_TOKEN
    if ACCESS_TOKEN:
        return ACCESS_TOKEN

    url = f"{os.getenv('IIKO_BASE_URL')}/access_token"
    payload = {
        "apiLogin": os.getenv('API_LOGIN_FOR_IIKO')
    }

    response = requests.post(url, json=payload)
    print(payload)
    # print(response.json().get("errorDescription"))
    print(response.text)
    if response.status_code == 200:
        ACCESS_TOKEN = response.json().get("token")
        return ACCESS_TOKEN
    else:
        raise Exception("Failed to obtain access token. Please check your API login credentials.")


def make_request(endpoint, method="POST", payload=None):
    """
    Makes an API request with automatic token refresh handling on 401 errors.
    """
    global ACCESS_TOKEN
    url = f"{os.getenv('IIKO_BASE_URL')}/{endpoint}"
    print("Request URL:", url)

    token = get_access_token()
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = None
    if method == "POST":
        response = requests.post(url, json=payload, headers=headers)
    elif method == "GET":
        response = requests.get(url, headers=headers, params=payload)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    if response.status_code == 401:
        print("Token expired, refreshing...")
        ACCESS_TOKEN = None  # Reset token
        token = get_access_token()
        headers["Authorization"] = f"Bearer {token}"

        if method == "POST":
            response = requests.post(url, json=payload, headers=headers)
        elif method == "GET":
            response = requests.get(url, headers=headers, params=payload)

    response.raise_for_status()
    return response.json()
