import base64
from decimal import Decimal
import hashlib
import json
import requests
from decouple import config

public_key = config('PUBLIC_KEY')
private_key = config('PRIVATE_KEY')


def base64_encode_sha1(sgn_string):
    # Step 1: Calculate the SHA-1 hash of the input string
    sha1_hash = hashlib.sha1(sgn_string.encode('utf-8')).digest()
    # Step 2: Base64 encode the resulting hash
    base64_encoded = base64.b64encode(sha1_hash)
    # Convert the Base64 encoded bytes to a string
    base64_encoded_str = base64_encoded.decode('utf-8')

    return base64_encoded_str


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super(DecimalEncoder, self).default(obj)


def get_signature(data):
    key = private_key + data + private_key
    signature = base64_encode_sha1(key)
    return signature


def get_data_and_signature(amount, currency, description, language, order_id):
    json_string = json.dumps({
        "public_key": public_key,
        "amount": amount,
        "currency": currency,
        "description": description,
        "language": language,
        "order_id": order_id}, cls=DecimalEncoder)
    json_bytes = json_string.encode('utf-8')
    json_base64 = base64.b64encode(json_bytes)
    data = json_base64.decode('utf-8')
    signature = get_signature(data)
    return [data, signature]


def get_status_data_and_signature(transaction):
    json_string = json.dumps({
        "public_key": public_key,
        "transaction": transaction})
    json_bytes = json_string.encode('utf-8')
    json_base64 = base64.b64encode(json_bytes)
    data = json_base64.decode('utf-8')
    signature = get_signature(data)
    return [data, signature]


def get_card_reg_data_and_signature(language, refund, description,
                                    success_redirect_url='https://menu.byqr.az/az/tips-success',
                                    error_redirect_url='https://menu.byqr.az/az/tips-error'):
    json_string = json.dumps({
        "public_key": public_key,
        "language": language,
        "refund": refund,
        "description": description,
        "success_redirect_url": success_redirect_url,
        "error_redirect_url": error_redirect_url})
    json_bytes = json_string.encode('utf-8')
    json_base64 = base64.b64encode(json_bytes)
    data = json_base64.decode('utf-8')
    signature = get_signature(data)
    return [data, signature]


def get_pay_card_data_and_signature(amount, currency, description, language, order_id, card_id):
    json_string = json.dumps({
        "public_key": public_key,
        "amount": amount,
        "currency": currency,
        "description": description,
        "language": language,
        "order_id": order_id,
        "card_id": card_id}, cls=DecimalEncoder)
    json_bytes = json_string.encode('utf-8')
    json_base64 = base64.b64encode(json_bytes)
    data = json_base64.decode('utf-8')
    signature = get_signature(data)
    return [data, signature]


def get_pay_and_save_data_and_signature(amount, currency, description, language, order_id, success_redirect_url,
                                        error_redirect_url):
    json_string = json.dumps({
        "public_key": public_key,
        "amount": amount,
        "currency": currency,
        "description": description,
        "language": language,
        "order_id": order_id,
        "success_redirect_url": success_redirect_url,
        "error_redirect_url": error_redirect_url}, cls=DecimalEncoder)
    json_bytes = json_string.encode('utf-8')
    json_base64 = base64.b64encode(json_bytes)
    data = json_base64.decode('utf-8')
    signature = get_signature(data)
    return [data, signature]


def get_refund_data_and_signature(amount, currency, description, language, order_id, card_id):
    json_string = json.dumps({
        "public_key": public_key,
        "amount": amount,
        "currency": currency,
        "description": description,
        "language": language,
        "order_id": order_id,
        "card_id": card_id}, cls=DecimalEncoder)
    json_bytes = json_string.encode('utf-8')
    json_base64 = base64.b64encode(json_bytes)
    data = json_base64.decode('utf-8')
    signature = get_signature(data)
    return [data, signature]


def get_apple_session_data_signature():
    json_string = json.dumps({
        "public_key": public_key,
        "origin": "https://menu.byqr.az"
    })
    json_bytes = json_string.encode('utf-8')
    json_base64 = base64.b64encode(json_bytes)
    data = json_base64.decode('utf-8')
    signature = get_signature(data)
    return [data, signature]


def get_apple_pay_data_signature(id, token, billing_contact):
    json_string = json.dumps({
        "public_key": public_key,
        "id": id,
        "token": token,
        "billingContact": billing_contact
    })
    json_bytes = json_string.encode('utf-8')
    json_base64 = base64.b64encode(json_bytes)
    data = json_base64.decode('utf-8')
    signature = get_signature(data)
    return [data, signature]


def create_apple_payment(data, signature):
    url = "https://epoint.az/api/1/token/apple/pay"
    body = {"data": data, "signature": signature}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=body)
    return response


def create_payment(data, signature):
    url = "https://epoint.az/api/1/request"
    body = {"data": data, "signature": signature}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=body)
    return response


def create_token_payment(data, signature):
    url = "https://epoint.az/api/1/token/payment"
    body = {"data": data, "signature": signature}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=body)
    return response


def check_status(data, signature):
    url = "https://epoint.az/api/1/get-status"
    body = {"data": data, "signature": signature}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=body)
    return response


def card_register(data, signature):
    url = "https://epoint.az/api/1/card-registration"
    body = {"data": data, "signature": signature}
    headers = {'Content-Type': 'application/json'}
    print(body)
    response = requests.post(url, headers=headers, json=body)
    return response


def create_payment_with_card(data, signature):
    url = "https://epoint.az/api/1/execute-pay"
    body = {"data": data, "signature": signature}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=body)
    return response


def create_payment_and_save_card(data, signature):
    url = "https://epoint.az/api/1/card-registration-with-pay"
    body = {"data": data, "signature": signature}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=body)
    return response


def create_refund(data, signature):
    url = "https://epoint.az/api/1/refund-request"
    body = {"data": data, "signature": signature}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=body)
    return response


def apple_pay_session(data, signature):
    url = "https://epoint.az/api/1/token/apple/session"
    body = {"data": data, "signature": signature}
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, headers=headers, json=body)
    return response


def get_signature(data):
    key = private_key + data + private_key
    signature = base64_encode_sha1(key)
    return signature


def get_json(data):
    decoded_bytes = base64.b64decode(data)
    decoded_json_string = decoded_bytes.decode('utf-8')
    decoded_data = json.loads(decoded_json_string)
    return decoded_data


def generate_epoint_token(public_key, amount, order_id, description, private_key):
    payload = {
        'public_key': public_key,
        'amount': amount,
        'order_id': order_id,
        'description': description
    }

    payload_json = json.dumps(payload)
    data = base64.b64encode(payload_json.encode('utf-8')).decode('utf-8')

    signature_string = private_key + data + private_key
    signature = base64.b64encode(hashlib.sha1(signature_string.encode('utf-8')).digest()).decode('utf-8')

    url = "https://epoint.az/api/1/token/widget"
    request_data = {
        'data': data,
        'signature': signature
    }

    response = requests.post(url, json=request_data)
    return response.json()
