import jwt
import time


def generate_apple_client_secret(key_id, team_id, client_id, private_key):
    now = int(time.time())
    payload = {
        'iss': team_id,
        'iat': now,
        'exp': now + 86400 * 180,  # 6 months
        'aud': 'https://appleid.apple.com',
        'sub': client_id,
    }
    headers = {
        'kid': key_id,
        'alg': 'ES256'
    }
    return jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
