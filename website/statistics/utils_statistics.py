import os

# from .settings import API_stat
import pandas as pd
import plotly.express as px
import requests
from ..settings import API_stat

# API_stat = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwMjI2djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcyNjM0NTQzNywiaWQiOiIwMGRiNGY1ZS00MmVhLTQ0MDUtOTA3My1iZTI3YjYzYTVhNzYiLCJpaWQiOjI5NjE1NDE1LCJvaWQiOjczMDY2OCwicyI6Miwic2lkIjoiNTUwMGU5ZWItOTgwYy00YjkyLWFhYTQtZTI5Zjg3NDNiNjE0IiwidCI6ZmFsc2UsInVpZCI6Mjk2MTU0MTV9.c48Q8Itn6j7bpEpJn37SCthtmqVZHMVtVguLFO9yrbGaCwJ_p8kXoofJMsW0nS2BJk8xcWe0QyodtRXRXQMviw'
headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_stat}


# получили все продажи work в .views  // дублирует ниже стаоящую функцию
def get_sales(selected_date):
    # all_articles_user = get_all_articles_user(userid)
    # API_stat = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwMjI2djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcyNzgzNzc1MiwiaWQiOiJlMTc0ZGYwNS05NzEzLTQzMjEtYmQyMC1iMWMzZmUxZjUyNzgiLCJpaWQiOjI5NjE1NDE1LCJvaWQiOjczMDY2OCwicyI6MzIsInNpZCI6IjU1MDBlOWViLTk4MGMtNGI5Mi1hYWE0LWUyOWY4NzQzYjYxNCIsInQiOmZhbHNlLCJ1aWQiOjI5NjE1NDE1fQ.hJQL4g07o9GuCnfVIzVttamdtNu9Zoexu3tTmtQHg3jwpk8WBCr7oy4IlWY-3E_uNOs80NYZtiXv7b2JRfgcwg'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_stat}
    date_start = selected_date  # Заказы считаются накопительным итогом с текущей даты
    param = {'dateFrom': date_start}
    response_1 = requests.get('https://statistics-api.wildberries.ru/api/v1/supplier/sales', headers=headers,
                              params=param)
    orders_data = response_1.json()

    all_articles_user = ['tomjerry-13', 'banksi-1', 'tomjerry-7', 'disney-6']  # это потом заменить (!)
    total_forPay_all = 0

    # Проход по каждому артикулу из списка all_articles_user
    for target_supplier_article in all_articles_user:
        total_forPay = 0
        # Проход по каждому словарю
        for data_dict in orders_data:
            if data_dict['supplierArticle'] == target_supplier_article:
                total_forPay += data_dict['forPay']
        print(f"Сумма 'forPay' для {target_supplier_article}: {total_forPay}")
        total_forPay_all += total_forPay
    print(f"Суммарная 'forPay' для всех артикулов: {total_forPay_all}")
    return total_forPay_all


def get_image_sales(selected_date):  # в .views выводится - возможно дубль с предыдущей функцией
    # all_articles_user = get_all_articles_user(userid)
    API_stat = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwMjI2djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcyNzgzNzc1MiwiaWQiOiJlMTc0ZGYwNS05NzEzLTQzMjEtYmQyMC1iMWMzZmUxZjUyNzgiLCJpaWQiOjI5NjE1NDE1LCJvaWQiOjczMDY2OCwicyI6MzIsInNpZCI6IjU1MDBlOWViLTk4MGMtNGI5Mi1hYWE0LWUyOWY4NzQzYjYxNCIsInQiOmZhbHNlLCJ1aWQiOjI5NjE1NDE1fQ.hJQL4g07o9GuCnfVIzVttamdtNu9Zoexu3tTmtQHg3jwpk8WBCr7oy4IlWY-3E_uNOs80NYZtiXv7b2JRfgcwg'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_stat}
    date_start = selected_date  # Заказы считаются накопительным итогом с текущей даты
    param = {'dateFrom': date_start}
    response_1 = requests.get('https://statistics-api.wildberries.ru/api/v1/supplier/sales', headers=headers,
                              params=param)
    orders_data = response_1.json()

    # Проверяем тип данных в orders_data
    if isinstance(orders_data, dict):
        # Если JSON содержит один объект, преобразуем его в список списков
        orders_data = [orders_data.values()]
    elif isinstance(orders_data, list):
        # Если JSON уже является списком, оставляем его без изменений
        pass

    df = pd.DataFrame(orders_data)  # ВАЖНЫЙ ДФ тк с него потом вся графика делаться будет!
    print(df)
    # Преобразуйте столбец с датой в формат datetime
    df['date'] = pd.to_datetime(df['date'])
    # Группируем данные по дням и подсчитываем сумму 'forPay'
    daily_sales: pd = df.groupby(df['date'].dt.date)['forPay'].sum().reset_index()
    print(daily_sales)

    # Создаем интерактивный график с использованием Plotly
    fig = px.line(daily_sales, x='date', y='forPay', title='Сумма продаж по дням')
    # Сохраняем график в формате HTML
    graph_html = fig.to_html(full_html=False)
    return graph_html


# добавить еще user_id пользователя (!)
def get_all_sales_user_per_day(selected_date, all_articles_user):
    # API_stat = 'eyJhbGciOiJFUzI1NiIsImtpZCI6IjIwMjQwMjI2djEiLCJ0eXAiOiJKV1QifQ.eyJlbnQiOjEsImV4cCI6MTcyNzgzNzc1MiwiaWQiOiJlMTc0ZGYwNS05NzEzLTQzMjEtYmQyMC1iMWMzZmUxZjUyNzgiLCJpaWQiOjI5NjE1NDE1LCJvaWQiOjczMDY2OCwicyI6MzIsInNpZCI6IjU1MDBlOWViLTk4MGMtNGI5Mi1hYWE0LWUyOWY4NzQzYjYxNCIsInQiOmZhbHNlLCJ1aWQiOjI5NjE1NDE1fQ.hJQL4g07o9GuCnfVIzVttamdtNu9Zoexu3tTmtQHg3jwpk8WBCr7oy4IlWY-3E_uNOs80NYZtiXv7b2JRfgcwg'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_stat}

    date_start = selected_date  # Заказы считаются накопительным итогом с текущей даты
    param = {'dateFrom': date_start}
    response_1 = requests.get('https://statistics-api.wildberries.ru/api/v1/supplier/sales', headers=headers,
                              params=param)
    orders_data = response_1.json()

    # all_articles_user = ['tomjerry-13', 'banksi-1', 'tomjerry-7', 'disney-6']  # это потом заменить (!)
    total_forPay_all = 0

    # Проход по каждому артикулу из списка all_articles_user
    for target_supplier_article in all_articles_user:
        total_forPay = 0
        for data_dict in orders_data:
            if data_dict['supplierArticle'] == target_supplier_article:
                total_forPay += data_dict['forPay']
        # print(f"Сумма 'forPay' для {target_supplier_article}: {total_forPay}")
        total_forPay_all += total_forPay
    print(f"Суммарная 'forPay' для всех артикулов: {total_forPay_all}")
    return total_forPay_all  # вот это в таблицу записывать потом


# get_all_sales_user_per_day('2024-06-24')

# get_image_sales('2024-06-24')
