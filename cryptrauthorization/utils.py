from django.contrib.auth import authenticate

from django.conf import settings
import json
import jwt
import requests

def jwt_get_username_from_payload_handler(payload):
    username = payload.get('sub')
    authenticate(remote_user=username)
    return username

def jwt_decode_token(token):
    header = jwt.get_unverified_header(token)

    issuer = '{}/t/{}'.format(settings.CRYPTR_CONFIG['BASE_URL'], settings.CRYPTR_CONFIG['TENANT_DOMAIN']) # MUST be equivalent to settings.JWT_AUTH['JWT_ISSUER']
    audience = settings.JWT_AUTH['JWT_AUDIENCE']
    algorithm = settings.JWT_AUTH['JWT_ALGORITHM']
    jwks_uri = '{}/.well-known/jwks'.format(issuer)
    jwks = requests.get(jwks_uri).json()

    public_key = None
    for jwk in jwks['keys']:
        if jwk['kid'] == header['kid']:
            public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))
    
    if public_key is None:
        raise Exception('Public key not found')
    
    return jwt.decode(token, public_key, audience=audience, issuer=issuer, algorithms=[algorithm])


