import secrets

from flask import Blueprint
from flask import current_app
from flask import render_template, request
from flask import session, redirect, url_for
from flask_mail import Message

from .. import bcrypt
from .. import db
from ..models import User, Wallet, Rating

auth = Blueprint('auth', __name__)


@auth.route('/registration', methods=['POST', 'GET'])
def add_record():
    if request.method == 'GET':  # Логика для отображения страницы входа
        return render_template('auth/registration.html')

    elif request.method == 'POST':
        username = request.form['name']
        email = request.form['email']
        password = request.form['password']
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            error = 'Такой email уже зарегистрирован'
            return render_template('auth/registration.html', error=error)
        else:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(username=username, email=email, password=hashed_password, user_role='user')
            db.session.add(new_user)
            db.session.commit()

            # Создаем запись в таблице Rating для нового пользователя
            new_rating = Rating(sum_money=0, sum_cards=0, rating=0, k_rating=1, user_id=new_user.user_id)
            db.session.add(new_rating)
            db.session.commit()

        return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:  # Проверяем наличие пользователя в сессии
        return redirect(url_for('views.admin'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        remember_me = request.form.get('remember_me')
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):  # проверка пароля
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['user_role'] = user.user_role

            if remember_me:
                session.permanent = True  # Устанавливаем сессию как постоянную

            if user.user_role == 'admin':
                return redirect(url_for('views.superadmin'))  # переход в админку

            return redirect(url_for('views.admin'))  # Пользователь существует и пароль верен
        else:
            error = 'Неправильный email или пароль. Попробуйте еще раз.'
            return render_template('auth/login.html', error=error)
    else:
        return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    session.pop('user_id', None)  # Удаляем идентификатор пользователя из сессии
    return redirect(url_for('views.index'))  # Перенаправляем пользователя на страницу входа


@auth.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        if user:
            token = secrets.token_urlsafe(32)
            # Сохраняем токен в базе данных
            user.reset_password_token = token
            db.session.commit()
            msg = Message('Сброс пароля', sender='heroesprint@yandex.ru', recipients=[email])
            msg.body = f'Для сброса пароля перейдите по ссылке: {url_for("auth.reset_password", token=token, _external=True)}'
            mail = current_app.extensions['mail']
            mail.send(msg)
            return render_template('auth/password_reset_email_sent.html')
        error = 'Пользователь с таким email не найден.'
        return render_template('auth/forgot_password.html', error=error)
    else:
        return render_template('auth/forgot_password.html')


@auth.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    user = User.query.filter_by(reset_password_token=token).first()
    if user:
        if request.method == 'POST':
            new_password = request.form['new_password']
            user.password = bcrypt.generate_password_hash(new_password).decode('utf-8')
            user.reset_password_token = None
            db.session.commit()
            return redirect(url_for('auth.login'))
        return render_template('auth/reset_password.html')  # Форма для ввода нового пароля
    else:
        error = 'Неверный токен сброса пароля.'
        return render_template('auth/login.html', error=error)


@auth.route('/change_password', methods=['GET', 'POST'])
def change_password():
    if request.method == 'POST':
        if 'user_id' in session:
            user_id = session['user_id']
            old_password = request.form['old_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            user = User.query.get(user_id)
            user.check_password(old_password)

            if not user.check_password(old_password):
                error = 'Неверный текущий пароль'
                return render_template('auth/change_password.html', error=error)

            if new_password != confirm_password:
                error = 'Новые пароли не совпадают'
                return render_template('auth/change_password.html', error=error)

            user.change_password(new_password)
            error = 'Пароль успешно изменен'
            return render_template('auth/change_password.html', error=error)

    return render_template('auth/change_password.html')
