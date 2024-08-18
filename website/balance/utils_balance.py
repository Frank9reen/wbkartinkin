import matplotlib.pyplot as plt
import pandas as pd
from flask import session
import io
import base64
from ..models import Balance
from ..rating.utils_rating import get_all_sales_user_per_day
import plotly.express as px


# добавить срабатывание по таймеру КАЖДЫЙ ДЕНЬ в 00-00 для записи в таблицу Balance
# надо добавить в Balance функцию для записи дневных доходов для ВСЕХ пользователе по ВСЕМ карточкам
#  поставить срабатывание по таймеру
# current_user_id = session.get('user_id')
# selected_articles_for_user = ['pink-2', 'disney-10']
# date_start = '2024-06-20'  # потом делать вызов каждый день ночью
# day_balance_for_user = get_all_sales_user_per_day(selected_articles_for_user, date_start)
# Balance.create_balance(day_balance_for_user, current_user_id)
# можно добавить проверку чтобы не вставлять если уже дата такая есть
#

def plot_user_balance(user_id):
    # Получаем все записи баланса для текущего пользователя
    balances = Balance.query.filter(Balance.user_id == user_id).all()
    # Преобразуем данные в формате, удобном для обработки
    data = [(balance.date, balance.day_balance) for balance in balances]
    if not data:
        print("Нет записей о балансе для этого пользователя.")
        return
    # Создаем DataFrame из полученных данных
    df = pd.DataFrame(data, columns=['date', 'day_balance'])
    df['date'] = pd.to_datetime(df['date'])  # Приводим к типу datetime
    # Сортируем данные по дате
    df = df.sort_values('date')

    # Группируем данные по дням и подсчитываем сумму 'day_balance'
    daily_balance = df.groupby(df['date'].dt.date)['day_balance'].sum().reset_index()

    # Печатаем DataFrame
    print(daily_balance)

    # Используем Plotly для создания интерактивного графика
    fig = px.line(daily_balance, x='date', y='day_balance',
                  title=f'Баланс по дням для пользователя ID {user_id}',
                  labels={'day_balance': 'Суммарный баланс', 'date': 'Дата'})

    # Сохраняем график в формате HTML
    graph_html = fig.to_html(full_html=False)
    return graph_html

