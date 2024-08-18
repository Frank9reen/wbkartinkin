import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__name__))
load_dotenv(os.path.join(basedir, '.env'))

SECRET_KEY = os.urandom(36)
# SQLALCHEMY_DATABASE_URI = 'mysql://db2:*O3eJ&6wiDnc@guefoogekik.beget.app/db2'  work
# SQLALCHEMY_DATABASE_URI = 'mysql://root:020188@localhost/db2'  # подключение к MySQL через SQLAlchemy
SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI')  # если мы вписываем в файл .env
SQLALCHEMY_TRACK_MODIFICATIONS = os.environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')  # добавил

PERMANENT_SESSION_LIFETIME = 3600  # Установка времени жизни сессии в 1 час (3600 секунд)
MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100 MB

basedir = os.path.abspath(os.path.dirname(__name__))
UPLOAD_FOLDER = os.path.join('website', 'static', 'uploads')

MAIL_SERVER = 'smtp.yandex.ru'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
MAIL_USERNAME = 'heroesprint@yandex.ru'
# Yandex mail password connection
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

# WB API TOKEN
API_stat = os.environ.get('API_stat')

# Yandex disk token
YADISK_TOKEN = os.environ.get('YADISK_TOKEN')
# YADISK_TOKEN = 'y0_AgAAAAB2MMm-AAwWlQAAAAEKJb9SAAAahHB98ExJLbZtFW_ppmbOnp8zDw'

# time update
TIME_UPDATE = os.environ.get('TIME_UPDATE')
