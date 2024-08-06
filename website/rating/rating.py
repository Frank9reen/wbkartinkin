from flask import Blueprint
from flask import render_template, session

from ..models import Rating, Balance
from ..rating.utils_rating import get_all_sales_user_per_day, plot_user_balance

rating = Blueprint('rating', __name__)


# добавить срабатывание по таймеру каждую неделю в 00-00 для записи в таблицу Rating
@rating.route('/rating', methods=['GET'])
def get_rating():
    current_user_id = session.get('user_id')
    ratings = Rating.query.order_by(Rating.rating.asc()).all()  # упорядочить по возрастанию
    Rating.update_sum_cards(current_user_id)  # обновили количество КТ за 7 дней
    Rating.update_sum_money_for_user(current_user_id)
    Rating.rank_ratings()  # обновить проставление нумерации в таблице Rating

    Rating.difference_in_sum_cards(current_user_id)

    #временно вставил - потом перенести в utils_balance и поставить срабатывание по таймеру
    selected_articles_for_user = ['pink-2', 'disney-10']
    date_start = '2024-06-20'  # потом делать вызов каждый день ночью
    day_balance_for_user = get_all_sales_user_per_day(selected_articles_for_user, date_start)
    Balance.create_balance(day_balance_for_user, current_user_id)
    # можно добавить проверку чтобы не вставлять если уже дата такая есть
    #
    graph_html = plot_user_balance(current_user_id)


    return render_template('rating/rating.html', ratings=ratings, current_user_id=current_user_id, graph_html=graph_html)
