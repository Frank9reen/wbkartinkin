import os
from dotenv import load_dotenv

# для переменных окружения - сейчас не использую
basedir = os.path.abspath(os.path.dirname(__name__))
load_dotenv(os.path.join(basedir, 'blog/.env'))


SECRET_KEY = os.urandom(36)
# SQLALCHEMY_DATABASE_URI = 'mysql://db2:*O3eJ&6wiDnc@guefoogekik.beget.app/db2'  work
# SQLALCHEMY_DATABASE_URI = 'mysql://root:020188@localhost/db2'  # подключение к MySQL через SQLAlchemy
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')  # если мы вписываем в файл .env
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')  # добавил

PERMANENT_SESSION_LIFETIME = 3600  # Установка времени жизни сессии в 1 час (3600 секунд)
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

MAIL_SERVER = 'smtp.yandex.ru'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'heroesprint@yandex.ru'
MAIL_PASSWORD = 'qauleebdqyygazkv'

basedir = os.path.abspath(os.path.dirname(__name__))
UPLOAD_FOLDER = os.path.join('website', 'static', 'uploads')  # для сохранения картинки используется в папку

# heroes print
API_stat = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwMjI2djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcyNjM0NTQzNywiaWQiOiIwMGRiNGY1ZS00MmVhLTQ0MDUtOTA3My1iZTI3YjYzYTVhNzYiLCJpaWQiOjI5NjE1NDE1LCJvaWQiOjczMDY2OCwicyI6Miwic2lkIjoiNTUwMGU5ZWItOTgwYy00YjkyLWFhYTQtZTI5Zjg3NDNiNjE0IiwidCI6ZmFsc2UsInVpZCI6Mjk2MTU0MTV9.c48Q8Itn6j7bpEpJn37SCthtmqVZHMVtVguLFO9yrbGaCwJ_p8kXoofJMsW0nS2BJk8xcWe0QyodtRXRXQMviw'

# Ya.Disk
YADISK_TOKEN = 'y0_AgAAAAB2MMm-AAwWlQAAAAEKJb9SAAAahHB98ExJLbZtFW_ppmbOnp8zDw'
