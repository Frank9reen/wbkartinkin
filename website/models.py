import os
from datetime import datetime, timedelta

import bcrypt
from sqlalchemy import and_, func

from . import db
from .settings import UPLOAD_FOLDER


class UserBalance(db.Model):
    __tablename__ = 'userbalance'
    userbalance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)  # Убедитесь, что autoincrement=True
    totalbalance = db.Column(db.Integer, nullable=True)  # сумма дохода по всем дням для user
    curbalance = db.Column(db.Integer, nullable=True)  # разница между total_b - payouts_b
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    @classmethod
    def update_user_balance(cls, user_id):
        """Обновляет общее количество денег за все время для указанного user_id и записывает его в totalbalance"""
        # 1 Получаем сумму всех дневных балансов для указанного user_id
        total_money = db.session.query(func.sum(Balance.day_balance)).filter(
            Balance.user_id == user_id
        ).scalar() or 0

        # 2 Получаем сумму БЕЗ холда для указанного user_id, которую можно вывести - не работает правильно тк нет записи
        now = datetime.now()
        cutoff_date = now - timedelta(days=1)  # поставить 7, 14 или 30 дней
        total_money_without_hold = db.session.query(func.sum(Balance.day_balance)).filter(
            Balance.user_id == user_id,
            Balance.date < cutoff_date  # Предполагается, что поле date существует в модели Balance
        ).scalar() or 0

        # 3 суммируем все суммы выплат из модели Payouts для пользователя
        total_withdraw = db.session.query(func.sum(Payouts.amount)).filter(
            Payouts.user_id == user_id
        ).scalar() or 0

        # Текущий баланс - подсчитываем разницу между доходами без холда и выплатами
        totalbalance = round(total_money - total_withdraw)
        curbalance = round(total_money_without_hold - total_withdraw)

        user_balance_record = cls.query.filter_by(user_id=user_id).first()
        if user_balance_record:
            user_balance_record.totalbalance = totalbalance  # Обновляем totalbalance
            user_balance_record.curbalance = curbalance  # Обновляем curbalance
        else:
            user_balance_record = UserBalance(
                user_id=user_id,
                totalbalance=totalbalance,
                curbalance=curbalance
            )
            db.session.add(user_balance_record)
        db.session.commit()  # Сохраняем изменения в базе данных

    @classmethod
    def get_payouts_balance(cls, user_id):
        """Возвращает payoutsbalance для указанного user_id"""
        user_balance_record = cls.query.filter_by(user_id=user_id).first()
        if user_balance_record:
            return user_balance_record.curbalance
        return None  # Или можно вернуть 0, если запись не найдена


class Balance(db.Model):
    __tablename__ = 'balance'
    balance_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    day_balance = db.Column(db.Float, nullable=False)  # суммарный баланс за день
    date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))  # связь с таблицей пользователей

    @classmethod
    def create_balance(cls, day_balance, user_id):
        if user_id is None:  # Если user_id равен None, запись не делается
            print("User ID is None. Balance entry will not be created.")
            return None

        """Создает и сохраняет новый баланс в базе данных."""
        today = datetime.now().date()  # Получаем сегодняшнюю дату
        existing_balance = cls.query.filter(and_(cls.user_id == user_id, cls.date >= today)).first()

        if existing_balance:
            # Если запись с сегодняшней датой уже существует, возвращаем её или сообщение
            return existing_balance  # Либо можно вернуть None или сообщение о том, что запись уже существует

        new_balance = cls(day_balance=day_balance, user_id=user_id)
        db.session.add(new_balance)
        db.session.commit()
        return new_balance


class Rating(db.Model):  # данные по рейтингу за неделю, сумма КТ за все время, а деньги за неделю (!)
    __tablename__ = 'rating'
    rating_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sum_money = db.Column(db.Integer, nullable=True)
    sum_cards = db.Column(db.Integer, nullable=True)
    rating = db.Column(db.Integer, nullable=True, index=True)  # индекс для более быстрого поиска
    k_rating = db.Column(db.Integer, nullable=False, default=1)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    @classmethod
    def update_sum_cards(cls, user_id):
        # Получаем количество записей WbPost за последние 7 дней для указанного user_id
        # count = WbPost.count_user_posts_last_7_days(user_id)  # эта функция из WbPost за 7 дней
        count = WbPost.count_user_posts_all_time(user_id)  # за все время КТ сумма
        rating = cls.query.filter_by(user_id=user_id).first()
        if rating:
            rating.sum_cards = count  # Обновляем sum_cards
            db.session.commit()  # Сохраняем изменения в базе данных
        else:
            # Если рейтинга нет, можно создать новый
            rating = Rating(user_id=user_id, sum_cards=count)
            db.session.add(rating)
            db.session.commit()

    @classmethod
    def check_max_sum_cards(cls, user_id):
        current_rating = cls.query.filter_by(user_id=user_id).first()
        if not current_rating:
            return ""
        max_sum_cards = cls.query.with_entities(db.func.max(cls.sum_cards)).scalar()
        if current_rating.sum_cards == max_sum_cards and current_rating.sum_cards != 0:
            return 'max сделано карточек среди всех'
        else:
            return ""

    @classmethod
    def rank_ratings(cls):  # Получаем все записи рейтинга, отсортированные по sum_money
        ratings = cls.query.order_by(cls.sum_money.desc()).all()
        # Присваиваем ранг каждой записи
        for index, rating in enumerate(ratings, start=1):
            rating.rating = index
        # Сохраняем изменения в базе данных
        db.session.commit()

    @classmethod
    def update_sum_money_for_user(cls, user_id):
        """Обновляет сумму money за последние 7 дней для указанного user_id"""
        seven_days_ago = datetime.now() - timedelta(days=14)  # изменил! с 7 (оставить потом 7)!
        total_money = db.session.query(db.func.sum(Balance.day_balance)).filter(
            Balance.user_id == user_id,
            Balance.date >= seven_days_ago
        ).scalar() or 0  # Считаем сумму day_balance
        rating = cls.query.filter_by(user_id=user_id).first()
        if rating:
            rating.sum_money = total_money  # Обновляем sum_money
        else:
            # Если рейтинга нет, можно создать новый
            rating = Rating(user_id=user_id, sum_money=total_money)
            db.session.add(rating)
        db.session.commit()  # Сохраняем изменения в базе данных

    @classmethod
    def count_user_cards_in_period(cls, user_id, start_date, end_date):
        """Считает количество карточек пользователя в заданном периоде."""
        count = WbPost.query.filter(
            WbPost.user_id == user_id,
            WbPost.create_date >= start_date,
            WbPost.create_date < end_date
        ).count()  # Предполагается, что у WbPost есть поле date
        return count

    @classmethod
    def difference_in_sum_cards(cls, user_id):
        """Находит разницу между количеством карточек в течение последних 7 дней и предыдущих 7 дней."""
        today = datetime.now()
        # Период для последних 7 дней
        start_last_7_days = today - timedelta(days=7)
        end_last_7_days = today
        # Период для предыдущих 7 дней
        start_previous_7_days = today - timedelta(days=14)
        end_previous_7_days = today - timedelta(days=7)
        # Получаем количество карточек за оба периода
        last_7_days_count = cls.count_user_cards_in_period(user_id, start_last_7_days, end_last_7_days)
        previous_7_days_count = cls.count_user_cards_in_period(user_id, start_previous_7_days, end_previous_7_days)
        # Вычисляем разницу
        difference = last_7_days_count - previous_7_days_count
        return difference

    @classmethod
    def difference_in_sum_money(cls, user_id):
        """Находит разницу между доходом за последние 7 дней и предыдущими 7 днями."""
        today = datetime.now()
        # Период для последних 7 дней
        start_last_7_days = today - timedelta(days=7)
        end_last_7_days = today
        # Период для предыдущих 7 дней
        start_previous_7_days = today - timedelta(days=14)
        end_previous_7_days = today - timedelta(days=7)
        # Получаем сумму дохода за оба периода
        last_7_days_income = db.session.query(db.func.sum(Balance.day_balance)).filter(
            Balance.user_id == user_id,
            Balance.date >= start_last_7_days,
            Balance.date < end_last_7_days
        ).scalar() or 0
        previous_7_days_income = db.session.query(db.func.sum(Balance.day_balance)).filter(
            Balance.user_id == user_id,
            Balance.date >= start_previous_7_days,
            Balance.date < end_previous_7_days
        ).scalar() or 0
        # Вычисляем разницу
        difference = last_7_days_income - previous_7_days_income
        return round(difference)


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
    articul = db.Column(db.String(50))  # Добавленный столбец
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))  # зачем нужен?
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    create_date = db.Column(db.DateTime, default=datetime.now, nullable=False)
    post = db.relationship('Post', backref='wb_associations')  # что это за связи?

    @classmethod
    def set_articul_wb(cls, articul_wb, articul, post_id, user_id):
        post = Post.query.get(post_id)
        if post:
            wbpost = WbPost(articul_wb=articul_wb, articul=articul, post=post, user_id=user_id)
            db.session.add(wbpost)
            db.session.commit()

    # @classmethod
    # def count_user_posts_last_7_days(cls, user_id):  # количество опубликованных КТ за 7 дней
    #     seven_days_ago = datetime.now() - timedelta(days=7)  # Определяем дату 7 дней назад
    #     # Подсчитываем количество записей для указанного user_id за последние 7 дней
    #     return cls.query.filter(cls.user_id == user_id, cls.create_date >= seven_days_ago).count()

    @classmethod
    def count_user_posts_all_time(cls, user_id):   # количество опубликованных КТ за все время
        # Подсчитываем общее количество записей для указанного user_id
        return cls.query.filter(cls.user_id == user_id).count()


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


class AdminComments(db.Model):
    __tablename__ = 'admincomments'
    acomment_id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    post_id = db.Column(db.Integer, db.ForeignKey('post.post_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    comment_date = db.Column(db.DateTime, default=datetime.now, nullable=False)

    @classmethod
    def add_comment(cls, content, post_id, user_id):
        name_content = content
        new_comment = AdminComments(content=name_content, post_id=post_id, user_id=user_id)
        db.session.add(new_comment)
        db.session.commit()


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
    def delete_comment(self):  # используется - вроде нет?
        db.session.delete(self)
        db.session.commit()

    # Метод для изменения комментария
    def edit_comment(self, new_content):  # используется - вроде нет?
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
        image_urls = (
            Image.query.filter_by(post_id=post_id)
            .order_by(Image.image_order)  # Сортировка по image_order
            .with_entities(Image.image_url)
            .all()
        )
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
