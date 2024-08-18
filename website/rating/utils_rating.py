import pandas as pd
import plotly.graph_objects as go
import requests
from plotly.subplots import make_subplots

from ..models import Balance, User
from ..settings import API_stat

headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_stat}


def get_all_sales_user_per_day(selected_articles_for_user: list, date_start):  # work - перенести в баланс
    API_stat = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwMjI2djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcyNzgzNzc1MiwiaWQiOiJlMTc0ZGYwNS05NzEzLTQzMjEtYmQyMC1iMWMzZmUxZjUyNzgiLCJpaWQiOjI5NjE1NDE1LCJvaWQiOjczMDY2OCwicyI6MzIsInNpZCI6IjU1MDBlOWViLTk4MGMtNGI5Mi1hYWE0LWUyOWY4NzQzYjYxNCIsInQiOmZhbHNlLCJ1aWQiOjI5NjE1NDE1fQ.hJQL4g07o9GuCnfVIzVttamdtNu9Zoexu3tTmtQHg3jwpk8WBCr7oy4IlWY-3E_uNOs80NYZtiXv7b2JRfgcwg'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_stat}
    # date_start = '2024-08-03'  # Заказы считаются накопительным итогом с текущей даты
    param = {'dateFrom': date_start}
    response_1 = requests.get('https://statistics-api.wildberries.ru/api/v1/supplier/sales', headers=headers,
                              params=param)
    orders_data = response_1.json()
    # print(orders_data[:1])
    total_for_pay = 0
    total_forPay = sum(item['forPay'] for item in orders_data if item['supplierArticle'] in selected_articles_for_user)
    print(date_start, total_forPay)
    return total_forPay  # вот это в таблицу записывать потом


def plot_user_balance(user_id):  # work / перенести в баланс или статистику (нужна ли она?)
    # Получаем пользователя из базы данных
    user = User.query.get(user_id)
    if not user:
        print(f"Пользователь с ID-{user_id} не найден.")
        return

    username = user.username
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
    # print(daily_balance)

    # Используем Plotly для создания интерактивного графика - было раньше
    # fig = px.line(daily_balance, x='date', y='day_balance',
    #               title=f'Баланс по дням для {user.username}',
    #               labels={'day_balance': 'Суммарный баланс', 'date': 'Дата'})

    # Создаем интерактивный график с улучшенным форматированием
    fig = make_subplots(rows=1, cols=1)

    line = go.Scatter(
        x=daily_balance['date'],
        y=daily_balance['day_balance'],
        mode='lines+markers',
        name='Суммарный баланс',
        line=dict(color='royalblue', width=4),
        marker=dict(size=10, color='red', symbol='circle')
    )

    fig.add_trace(line, row=1, col=1)

    # Настройка макета графика
    fig.update_layout(
        title={
            'text': f'Баланс по дням для {username} (ID-{user_id})',
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='Дата',
        yaxis_title='Суммарный баланс',
        font=dict(
            family="ubuntu-medium",
            size=12,
            color="black"
        ),
        paper_bgcolor='white',
        plot_bgcolor='white',
        xaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        ),
        yaxis=dict(
            showgrid=True,
            gridwidth=1,
            gridcolor='lightgray'
        )
    )

    # Сохраняем график в формате HTML
    graph_html = fig.to_html(full_html=False)
    return graph_html


# get_all_sales_user_per_day('2024-06-24')
