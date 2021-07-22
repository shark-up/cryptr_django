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
