from functools import wraps
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

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

@api_view(['GET'])
# @requires_scope('read:courses')
def courses(request):
    return JsonResponse([
        {
            "id": 1,
                "user_id": "eba25511-afce-4c8e-8cab-f82822434648",
                "title": "learn git",
                "tags": ["colaborate", "git" ,"cli", "commit", "versionning"],
                "img": "https://carlchenet.com/wp-content/uploads/2019/04/git-logo.png",
                "desc": "Learn how to create, manage, fork, and collaborate on a project. Git stays a major part of all companies projects. Learning git is learning how to make your project better everyday",
                "date": '5 Nov',
                "timestamp": 1604577600000,
                "teacher": {
                    "name": "Max",
                    "picture": "https://images.unsplash.com/photo-1558531304-a4773b7e3a9c?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=634&q=80"
                }
        }
    ], safe=False)
