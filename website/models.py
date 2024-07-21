import os
from datetime import datetime

import bcrypt

from . import db
from .settings import UPLOAD_FOLDER


class Balance(db.Model):
    __tablename__ = 'balance'
    balance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # id в конце слова стоит всегда
    day_balance = db.Column(db.Float, nullable=False)  # суммарный баланс за день
    date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))  # связь с таблицей пользователей


class Rating(db.Model):
    __tablename__ = 'rating'
    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sum_money = db.Column(db.Integer, nullable=True)
    sum_cards = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Integer, nullable=False, index=True)  # индекс для более быстрого поиска
    k_rating = db.Column(db.Integer, nullable=False, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    @classmethod
    def update_ratings(cls):  # не нужная функция
        # Получаем все записи из таблицы Rating и сортируем их по убыванию
        ratings = cls.query.order_by(cls.sum_money.desc()).all()  # например, можно сортировать по sum_money
        # Обновляем поле rating для каждого пользователя, присваивая порядковый номер
        for index, user_rating in enumerate(ratings, start=1):
            user_rating.rating = index  # Присваиваем порядковый номер
            db.session.add(user_rating)  # Добавляем изменения в сессию
        db.session.commit()  # Сохраняем изменения в БД

    @classmethod
    def check_max_sum_cards(cls, user_id):  # no work - may be delete
        # Получаем текущее значение sum_cards для пользователя
        current_rating = cls.query.filter_by(user_id=user_id).first()
        if not current_rating:
            return ""
        # Получаем максимальное значение sum_cards среди всех записей
        max_sum_cards = cls.query.with_entities(db.func.max(cls.sum_cards)).scalar()
        # Проверяем, является ли текущее значение sum_cards максимальным
        if current_rating.sum_cards == max_sum_cards:
            return 'max среди всех'
        else:
            return ""


class Payouts_bank(db.Model):  # изменить название на стиль верблюда
    __tablename__ = 'payouts_bank'
    payout_bank_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    full_name = db.Column(db.String(50))  # ФИО
    phone_number = db.Column(db.String(15))  # Номер телефона
    card_number = db.Column(db.String(16))  # Номер банковской карты
    payout_id = db.Column(db.Integer, db.ForeignKey('payouts.payout_id'))  # Связь с таблицей Payouts
    payout = db.relationship('Payouts', backref=db.backref('bank_payouts', uselist=False))


class Payouts(db.Model):
    __tablename__ = 'payouts'
    payout_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    submission_date = db.Column(db.Date)  # Дата подачи
    processing_date = db.Column(db.Date)  # Дата обработки
    amount = db.Column(db.Float)  # Сумма
    payout_type = db.Column(db.String(50))  # Тип
    recipient = db.Column(db.String(50))  # Получатель
    status = db.Column(db.String(50))  # Статус
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))  # Связь с таблицей пользователей
    user = db.relationship('User', backref=db.backref('payouts', lazy=True))

    def change_status(self, new_status):
        self.status = new_status
        db.session.commit()

    def set_processing_date(self):
        self.processing_date = datetime.now().date()
        db.session.commit()


# class RoleUser(db.Model):
#     __tablename__ = 'roleuser'
#     role_id = db.Column(db.Integer, primary_key=True)
#     role_user = db.Column(db.String(50), unique=True, nullable=False)
#     users = db.relationship('User', backref='role', lazy=True)


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(150), unique=True, nullable=False)
    user_role = db.Column(db.String(50), nullable=False)
    # role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'), nullable=False)
    reset_password_token = db.Column(db.String(100), nullable=True)
    ratings = db.relationship('Rating', backref='user', lazy=True)  # добавил, но надо ли?

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))

    def change_password(self, new_password):
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)
        self.password = hashed_password.decode('utf-8')
        db.session.commit()


class WbPost(db.Model):
    __tablename__ = 'wbpost'
    wbpost_id = db.Column(db.Integer, primary_key=True)
    articul_wb = db.Column(db.String(50))
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    post = db.relationship('Post', backref='wb_associations')  # что это за связи такие?

    @classmethod
    def set_articul_wb(cls, articul_value, post_id):
        post = Post.query.get(post_id)
        if post:
            wbpost = WbPost(articul_wb=articul_value, post=post)
            db.session.add(wbpost)
            db.session.commit()


class Post(db.Model):
    __tablename__ = 'post'
    post_id = db.Column(db.Integer, primary_key=True)  # Добавляем столбец id
    title = db.Column(db.String(100))
    content = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    post_status = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __init__(self, title, content, user_id, post_status):
        self.title = title
        self.content = content
        self.user_id = user_id
        self.post_status = post_status

    def change_status(self, new_post_status):
        self.post_status = new_post_status

    def delete(self):  # удаление записи
        db.session.delete(self)
        db.session.commit()

    def create(self):  # создание записи
        db.session.add(self)
        db.session.commit()

    def update(self, title, content):  # обновление записи
        self.title = title
        self.content = content
        db.session.commit()

    @classmethod  # чтение всех записей ? использую ли ?
    def get_all_posts(cls):
        return cls.query.all()

    @classmethod
    def get_posts_by_status(cls, statuses):
        return cls.query.filter(Post.post_status.in_(statuses)).all()


class Wallet(db.Model):
    __tablename__ = 'wallet'
    wallet_id = db.Column(db.Integer, primary_key=True)
    balance = db.Column(db.Numeric(10, 2), default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    def get_card_number(self):
        return self.card_number


class Comments(db.Model):
    __tablename__ = 'comments'
    comment_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    comment_date = db.Column(db.DateTime, default=datetime.now, nullable=False)

    # Метод для добавления комментария
    @classmethod
    def add_comment(cls, content, post_id, user_id):
        name_content = content
        new_comment = Comments(content=name_content, post_id=post_id, user_id=user_id)
        db.session.add(new_comment)
        db.session.commit()

    # Метод для удаления комментария
    def delete_comment(self):
        db.session.delete(self)
        db.session.commit()

    # Метод для изменения комментария
    def edit_comment(self, new_content):
        self.content = new_content
        db.session.commit()


class Image(db.Model):  # все методы рабочие
    image_id = db.Column(db.Integer, primary_key=True)
    image_url = db.Column(db.String(255), nullable=False)
    image_order = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))

    @staticmethod
    def delete_images_with_order_greater_than(post_id, order):  # функция удаления урлов > 0 index
        images_to_delete = Image.query.filter_by(post_id=post_id).filter(Image.image_order > order).all()
        if images_to_delete:
            for image in images_to_delete:
                db.session.delete(image)
            try:
                db.session.commit()
                return f"Успешно удалено {len(images_to_delete)} изображений для поста с post_id {post_id} и image_order > {order}."
            except Exception as e:
                return f"Произошла ошибка при удалении изображений: {str(e)}"
        else:
            return f"Изображения для поста с post_id {post_id} и image_order > {order} не найдены."

    @staticmethod
    def add_images_and_urls(user_id, post_id, image_order, file):  # лучше на 2 функции разбивать / криво работает
        folder = f'website/static/uploads/{user_id}/{post_id}/'
        if not os.path.exists(folder):
            os.makedirs(folder)

        # получение 0 данных файла
        existing_image = Image.query.filter_by(post_id=post_id, image_order=image_order).first()
        if existing_image:
            if image_order == 0:
                file_path_old = folder + file.filename
                file_extension = file.filename.split(".")[-1]
                new_file_path = os.path.join(folder, f'{user_id}-{post_id}.{file_extension}')
                os.rename(file_path_old, new_file_path)  # Переименовываем файл

                image_url = f'uploads/{user_id}/{post_id}/{user_id}-{post_id}.{file_extension}'
            else:
                # вообще в этой функции ошибки надо ее разбить и почистить
                image_url = f'uploads/{user_id}/{post_id}/{file.filename}'
                # Обновляем существующее изображение
                file_path = os.path.join(folder, file.filename)
                file.save(file_path)

            # Обновляем URL изображения в базе данных
            existing_image.image_url = image_url
            db.session.commit()
        else:
            # Создаем новое изображение
            file_path = os.path.join(folder, file.filename)
            file.save(file_path)
            image_url = f'uploads/{user_id}/{post_id}/{file.filename}'

            new_image = Image(user_id=user_id, post_id=post_id, image_order=image_order, image_url=image_url)
            db.session.add(new_image)
            db.session.commit()

    @staticmethod
    def get_image_urls_for_post(post_id):
        image_urls = Image.query.filter_by(post_id=post_id).with_entities(Image.image_url).all()
        cleaned_urls = [url[0].replace('static/', '').replace('\\', '/') for url in image_urls]
        return cleaned_urls

    @staticmethod
    def delete_images_and_folders(user_id, post_id):  # Добавляем метод удаления картинок и соответствующих папок
        folder = f'{UPLOAD_FOLDER}/{user_id}/{post_id}/'
        if os.path.exists(folder):
            for file_name in os.listdir(folder):
                file_path = os.path.join(folder, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            os.rmdir(folder)  # Удаляем пустую папку
            print('Images and folder deleted successfully.')
        else:
            print('Folder not found for deletion.')

    @staticmethod
    def delete_images(user_id, post_id):  # Метод удаления изображений из папки
        folder = f'{UPLOAD_FOLDER}/{user_id}/{post_id}/'
        if os.path.exists(folder):
            for file_name in os.listdir(folder):
                file_path = os.path.join(folder, file_name)
                if os.path.isfile(file_path):
                    os.remove(file_path)
            print('Images deleted successfully.')
        else:
            print('Folder not found for image deletion.')

    def delete(self):  # удаление записей в таблице Image
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def delete_image_by_user_post_id(user_id, post_id):
        images_to_delete = Image.query.filter_by(user_id=user_id, post_id=post_id).all()
        if images_to_delete:
            for image in images_to_delete:
                db.session.delete(image)
            try:
                db.session.commit()
                return f"Успешно удалено {len(images_to_delete)} изображений для user_id={user_id} и post_id={post_id}."
            except Exception as e:
                return f"Ошибка при удалении изображений: {str(e)}"
        else:
            return f"Изображения для user_id={user_id} и post_id={post_id} не найдены для удаления."



