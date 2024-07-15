from flask import Blueprint
from flask import current_app
from flask import request
from flask import session
from flask_mail import Message

message = Blueprint('message', __name__)


# Письмо с обучающими материалами
@message.route('/send_learning_materials', methods=['GET', 'POST'])
def send_learning_materials():
    if request.method == 'POST':
        email = request.form['email']
        # Здесь можно добавить логику для отправки обучающих материалов по email
        msg = Message('Обучающие материалы', sender='heroesprint@yandex.ru', recipients=[email])
        msg.body = f'Привет, {session.user.username}, ознакомься с обучающими материалами, которые мы для тебя приготовили'
        mail = current_app.extensions['mail']
        mail.send(msg)
        return 'send'
    else:
        return 'no send'


# письмо после опубликованной КТ
def wb_kt_published(email: str, articul_wb: str):
    url = f'https://www.wildberries.ru/catalog/{articul_wb}/detail.aspx?targetUrl=GP'
    msg = Message('Обучающие материалы', sender='heroesprint@yandex.ru', recipients=[email])
    msg.body = f'Привет, {session.user.username}, Карточка товара опубликована на ВБ {url}'
    mail = current_app.extensions['mail']
    mail.send(msg)
    return 'send'

# Письмо после первого дохода
