import datetime
from datetime import datetime
from datetime import timedelta

from flask import Blueprint
from flask import render_template, request
from flask import session
from flask_caching import Cache

from .utils_statistics import get_all_sales_user_per_day
from .. import db
from ..auth.utils_auth import login_required
from ..models import Balance, User, Post

statistics = Blueprint('statistics', __name__)

cache = Cache()


# изменить названия роутов на более понятные / тут функция будет, а не роут
# заполнение статистки ежедневно для всех пользователей по всем их КТ
@statistics.route('/day_balance', methods=['GET', 'POST'])  # надо чтобы, включалась не по кнопке, а по времени в 00:00
# @login_required
def day_balance():
    if request.method == 'POST':
        user_id = session.get('user_id')
        # получили все user_id авторов
        all_user_ids: list = [user.user_id for user in User.query.all()]

        for user_id in all_user_ids:
            # для данного пользователя вернуть список post_id
            all_post_ids = [post.post_id for post in Post.query.filter_by(user_id=user_id).all()]
            if all_post_ids:
                # создать артикулы для пользователя
                all_articles_user: list = [f'{user_id}-{post_id}' for post_id in all_post_ids]
                current_date = datetime.now()
                day_balance = get_all_sales_user_per_day(current_date, all_articles_user)

                new_balance_record = Balance(day_balance=day_balance, date=current_date, user_id=user_id)
                db.session.add(new_balance_record)
                db.session.commit()
    else:
        return 'error'
    return render_template('statistics/statistics.html')


@statistics.route('/statistics', methods=['GET'])
# @login_required
def get_statistics():
    if request.method == 'GET':
        user_id = session.get('user_id')

        # Определяем дату начала недели (для текущей недели)
        today = datetime.now()
        start_of_week = today - timedelta(days=today.weekday())

        # Выбираем данные о балансе за текущую неделю по дням из day_balance
        balance_data_current_week = db.session.query(Balance.date, Balance.day_balance).filter(
            Balance.user_id == user_id,
            Balance.date >= start_of_week
        ).all()

        if balance_data_current_week:
            # Обрабатываем данные, например, подготавливаем их для передачи в шаблон
            return render_template('statistics/statistics.html', balance_data_current_week=balance_data_current_week)
        else:
            return render_template('statistics/statistics.html', balance_data_current_week=balance_data_current_week)
    else:
        return 'Ошибка: Недопустимый метод запроса'

