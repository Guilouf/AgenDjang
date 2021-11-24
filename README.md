# AgenDjang
![Travis](https://img.shields.io/badge/Python%20-3.8-brightgreen.svg?style=plastic) ![Travis](https://img.shields.io/badge/Django%20-3.2.9-brightgreen.svg?style=plastic)
Django app for task scheduling


# TODO
- [X] Add the javascript calendar, full calendar
- [X] Use DRF for AJAX
- [ ] Handle js dependencies
- [ ] Markdown support for TextFields
- [ ] Calendar export, e.g as VCS
- [ ] Interaction with the [google calendar API](https://developers.google.com/google-apps/calendar/quickstart/python)

## Install
- `pip install -r requirements.txt`
- `python manage.py makemigrations` 
- `python manage.py migrate`

# Build
- Be sure to have `wheel` package installed, if not pip will use an egg install (old)
- `pip install .`

# Install in another project
- Put `agendjang` in `INSTALLED_APPS`
- include urls ` path('your_path', include('agendjang.urls'))`

# Security
- CSRF protection is enabled if `'rest_framework.authentication.SessionAuthentication',` is used. 
 `CSRF_USE_SESSIONS` and `CSRF_COOKIE_HTTPONLY` should be at default "False" value.
 - If no user is logged, it still works but there is no `CSRF` protection indeed. 
