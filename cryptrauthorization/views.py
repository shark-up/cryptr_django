from functools import wraps
from django.http import JsonResponse
import jwt

def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.META.get("HTTP_AUTHORIZATION", None)
    if auth is None:
      return False
    parts = auth.split()
    token = parts[1]

    return token

def requires_scope(required_scope):
    """Determines if the required scope is present in the Access Token
    Args:
        required_scope (str): The scope required to access the resource
    """
    def require_scope(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = get_token_auth_header(args[0])
            if token is False:
              null_token_response = JsonResponse({'message': 'No Authorization header provided'})
              null_token_response.status_code = 403
              return null_token_response
            decoded = jwt.decode(token, verify=False)
            token_scopes = decoded["scp"]
            if token_scopes:
                for token_scope in token_scopes:
                    if token_scope == required_scope:
                        return f(*args, **kwargs)
            response = JsonResponse({'message': 'You don\'t have access to this resource'})
            response.status_code = 403
            return response
        return decorated
    return require_scope