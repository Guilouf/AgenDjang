# AgenDjang
![Travis](https://img.shields.io/badge/Python%20-3.6-brightgreen.svg?style=plastic) ![Travis](https://img.shields.io/badge/Django%20-1.11-brightgreen.svg?style=plastic)
Django app for task scheduling


# TODO
- [X] Add the javascript calendar, full calendar
- [X] Use DRF for AJAX
- [ ] Add FullCalendar as a git submodule, a dependency
    > Bad idea, better use a dependency manager for js, like bower, webpack, yarn
- [ ] Make patches for all project related files
- [ ] Markdown support for TextFields
- [ ] Calendar export, e.g as VCS
- [ ] Interaction with the [google calendar API](https://developers.google.com/google-apps/calendar/quickstart/python)

## Install
- Create project
    - Linux `django startproject name_project`
    - Windows `django-admin.exe startproject name_project`
- Create app: `manage.py startapp AgenDjang`
