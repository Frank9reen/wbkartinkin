import datetime

from flask import Blueprint
from flask import render_template, session

from ..models import Rating, Balance, UserBalance
from ..rating.utils_rating import get_all_sales_user_per_day, plot_user_balance

rating = Blueprint('rating', __name__)


# добавить срабатывание по таймеру каждую неделю в 00-00 для записи в таблицу Rating
@rating.route('/rating', methods=['GET'])
def get_rating():
    current_user_id = session.get('user_id')
    ratings = Rating.query.order_by(Rating.rating.asc()).all()  # упорядочить по возрастанию
    Rating.update_sum_cards(current_user_id)  # обновили количество КТ за ВСЕ дней
    Rating.update_sum_money_for_user(current_user_id)  # обновили рейтинг за 7 дней / работает???
    Rating.rank_ratings()  # обновить проставление нумерации в таблице Rating
    # Rating.difference_in_sum_cards(current_user_id)  # работает ли? ведь ничего не возвращается

    #временно вставил - потом перенести в utils_balance и поставить срабатывание по таймеру
    selected_articles_for_user = ['fish-2', 'disney-6']
    # date_start = '2024-06-20'  # потом делать вызов каждый день ночью
    current_date = datetime.datetime.now()
    yesterday_date = current_date.date() - datetime.timedelta(days=1)
    formatted_yesterday_date = yesterday_date.strftime('%Y-%m-%d')
    day_balance_for_user = get_all_sales_user_per_day(selected_articles_for_user, formatted_yesterday_date)
    Balance.create_balance(day_balance_for_user, current_user_id)  # записали баланс вчерашнего дня для автора

    # временно вставил - запись суммы по дням и отображение суммы по дням для вывода с холдом - в таблицу UserBalance
    UserBalance.update_user_balance(current_user_id)

    # вставка графика
    graph_html = plot_user_balance(current_user_id)

    return render_template('rating/rating.html', ratings=ratings, current_user_id=current_user_id, graph_html=graph_html)
