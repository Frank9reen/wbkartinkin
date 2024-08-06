import pandas as pd
import plotly.express as px
import requests

from ..models import Balance
from ..settings import API_stat

headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_stat}


def get_all_sales_user_per_day(selected_articles_for_user: list, selected_date):  # work - перенести в баланс
    API_stat = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwMjI2djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcyNzgzNzc1MiwiaWQiOiJlMTc0ZGYwNS05NzEzLTQzMjEtYmQyMC1iMWMzZmUxZjUyNzgiLCJpaWQiOjI5NjE1NDE1LCJvaWQiOjczMDY2OCwicyI6MzIsInNpZCI6IjU1MDBlOWViLTk4MGMtNGI5Mi1hYWE0LWUyOWY4NzQzYjYxNCIsInQiOmZhbHNlLCJ1aWQiOjI5NjE1NDE1fQ.hJQL4g07o9GuCnfVIzVttamdtNu9Zoexu3tTmtQHg3jwpk8WBCr7oy4IlWY-3E_uNOs80NYZtiXv7b2JRfgcwg'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_stat}
    date_start = '2024-08-03'  # Заказы считаются накопительным итогом с текущей даты
    param = {'dateFrom': date_start}
    response_1 = requests.get('https://statistics-api.wildberries.ru/api/v1/supplier/sales', headers=headers,
                              params=param)
    orders_data = response_1.json()
    print(orders_data[:1])
    total_for_pay = 0

    total_forPay = sum(item['forPay'] for item in orders_data if item['supplierArticle'] in selected_articles_for_user)
    print(total_forPay)
    return total_forPay  # вот это в таблицу записывать потом


def plot_user_balance(user_id):  # work / перенести в баланс или статистику (нужна ли она?)
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


# get_all_sales_user_per_day('2024-06-24')
