# Implement Cryptr Auth in a Django API project

## 01 - Create Project

### Initialization

First, ensure to install Django (and python if not)

```bash
pip install Django
```

Then initialize base of project

```bash
django-admin startproject cryptr_django
cd cryptr_django
python manage.py startapp cryptrauthorization
```

You should now have a folder tree similar to

```bash
├── cryptr_django
│   ├── __init__.py
│   ├── __pycache__
│   │   ├── __init__.cpython-39.pyc
│   │   └── settings.cpython-39.pyc
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── cryptrauthorization
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── migrations
│   │   └── __init__.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
└── manage.py
```

### Install requirements

Wed use `virtualenv` to handle our local environment

Follow these steps

```bash
virtualenv env -p python3
. env/bin/activate
```

Now it's time to install requirements

```bash
echo "Django~=2.2.4
cryptography~=2.8
djangorestframework~=3.12.4
django-cors-headers~=3.1.1
drf-jwt~=1.13.3
pyjwt~=1.7.1
requests~=2.22.0" >> requirements.txt
```

to run requirements installation:

```bash
pip install -r requirements.txt
```

## First run of your server

you can run the following command to test your app

```bash
python manage.py runserver 8081 # 8081 is the part that we'll use in the react app
```

:warning: If you're facing the following error

```bash
File "manage.py", line 16
    ) from exc
         ^
SyntaxError: invalid syntax
````

just remove `from exc` and rerun the command

You may also need to run `python manage.py migrate` before a working run

The following [link](http://localhost:8081/) should display the django sample code

## 2 Setup application

Add `'django.contrib.auth.middleware.RemoteUserMiddleware'` in `MIDDLEWARE` in settings file

```python
# cryptr_django/settings.py

MIDDLEWARE = [
  # ...
  'django.contrib.auth.middleware.RemoteUserMiddleware'
]
```

Add `AUTHENTICATION_BACKENDS` with `ModelBackend` and `RemoteUserBackend`

```python
# cryptr_django/settings.py

MIDDLEWARE = [
  # ...
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django.contrib.auth.backends.RemoteUserBackend',
]
```

Create cryptrauthorization/utils.py file as follow

```bash
echo "from django.contrib.auth import authenticate

def jwt_get_username_from_payload_handler(payload):
    username = payload.get('sub')
    authenticate(remote_user=username)
    return username" >> cryptrauthorization/utlis.py
```

### Configure REST framework

Add `'rest_framework'` to `INSTALLED_APPS` in settings.py

```python
# cryptr_django/settings.py

INSTALLED_APPS = [
    # ...
    'rest_framework'
]
```

Add `REST_FRAMEWORK` in `settings.py`

```python
# cryptr_django/settings.py

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}
```

### Add JWT Config for cryptr

Add Following code to `settings.py`

```python
# cryptr_django/settings.py

AUTHENTICATION_BACKENDS = [
  # ...
]

CRYPTR_CONFIG = {
    'AUDIENCE': 'AUDIENCE', # in your test may be http://localhost:3000
    'TENANT_DOMAIN': 'YOUR_DOMAIN',
    'BASE_URL': 'https://auth.cryptr.eu'
}

JWT_AUTH = {
    'JWT_PAYLOAD_GET_USERNAME_HANDLER':
        'auth0authorization.utils.jwt_get_username_from_payload_handler',
    'JWT_DECODE_HANDLER':
        'auth0authorization.utils.jwt_decode_token',
    'JWT_ALGORITHM': 'RS256',
    'JWT_AUDIENCE': 'AUDIENCE', # in your test may be http://localhost:3000
    'JWT_ISSUER': 'YOUR_ISSUER', # see below for more info
    'JWT_AUTH_HEADER_PREFIX': 'Bearer',
}
```

Here is how to build `YOUR_AUDIENCE` :

```python
{BASE_URL}/t/{TENANT_DOMAIN}
```

Your setup is now ready for token decoding and endpoint protection (in next chapters)

## 03 Validate Access Token

First, you need to write `jwt_decode_token` definition in aim to check if provided token is a right one

This needs to be written in `utils.py` file

```python
# cryptrauthorization/utlis.py

# ...
from django.conf import settings
import json
import jwt
import requests

def jwt_get_username_from_payload_handler(payload):
  # ...

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

```

### Add scope validation support

Now, we can add a decorator to easily add support for scopes, with steps below each request can be validated if token provided has a specific scope

Paste the code below in `cryptrauthorization/views.py` file

```python
# cryptrauthorization/views.py

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
```

## 4 - Protect API endpoints

In this section we'll add the final code lines to protect your api endpoints depending on token provided in the request.

We will use two rest framework decorators : `@api_view` and `@permission_classes`

The use of `@api_view` decorator indicates that method requires an authentication

`@permission_classes([AllowAny])` indicates that the method is in public access

This final part is related to our [Cryptr React example](https://github.com/cryptr-examples/cryptr-react-sample). This React sample targets a backend API, in this case this Django API, and calls `/api/v1/courses` to list the current user's courses.

### create courses method

We need to create `courses`method at end of `view.py` file

```python
# cryptrauthorization/views.py

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

# ...

# require authentication

@api_view(['GET'])
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
```

If you want to precise a required scope to access to this resource just add

```python
@requires_scope('some:scope')
```

Final steps are to update Urls mappings to handle this route.

```bash
echo "from django.urls import path

from . import views

urlpatterns = [
  path('', views.courses, name ='courses')
]" >> cryptrauthorization/urls.py
```

Last step add `path('api/v1/courses', include('cryptrauthorization.urls'))`to root urls.py file

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/courses', include('cryptrauthorization.urls'))
]
```