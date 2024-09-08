import os
import time

import pandas as pd
import requests

from ..message.message import wb_kt_published
from ..models import WbPost, User
from ..settings import API_stat

headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_stat}


def add_new_card_on_wb(vendorcode: str):  # создает КТ, но картинки не добавляются
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer ' + API_stat}
    payload = [
        {
            'subjectID': 192,
            'subjectName': 'Футболки',
            'variants': [
                {
                    'vendorCode': vendorcode,  # артикул товара
                    'title': 'Футболка с принтом',
                    'description': 'Футболка с принтом',
                    'brand': '[ЧБ]',
                    'dimensions': {
                        'length': 30,
                        'width': 23,
                        'height': 2
                    },
                    'characteristics': [{'id': 204557, 'name': 'Пол', 'value': ['Женский']},
                                        {'id': 165482, 'name': 'Рост модели на фото', 'value': 170},
                                        {'id': 14177451, 'name': 'Страна производства', 'value': ['Россия']},
                                        {'id': 14177449, 'name': 'Цвет', 'value': ['белый']},
                                        {'id': 14177450, 'name': 'Состав', 'value': ['хлопок']},
                                        {'id': 23771, 'name': 'Особенности модели', 'value': ['дышащий материал']},
                                        {'id': 23796, 'name': 'Назначение',
                                         'value': ['повседневная', 'большие размеры']},
                                        {'id': 11, 'name': 'Покрой', 'value': ['свободный']},
                                        {'id': 6, 'name': 'Вырез горловины', 'value': ['округлый']},
                                        {'id': 213929, 'name': 'Тип ростовки', 'value': ['для среднего роста']},
                                        {'id': 48, 'name': 'Тип карманов', 'value': ['без карманов']},
                                        {'id': 12, 'name': 'Рисунок', 'value': ['печатный рисунок']},
                                        {'id': 50, 'name': 'Декоративные элементы', 'value': ['принт']},
                                        {'id': 11892, 'name': 'Уход за вещами',
                                         'value': ['бережная стирка при 30 градусах', 'выкручивание запрещено']},
                                        {'id': 246961, 'name': 'Размер на модели', 'value': ['48']},
                                        {'id': 15000001, 'name': 'ТНВЭД', 'value': ['6109100000']}],
                    'sizes': [
                        {"techSize": "XS", "wbSize": "44", "price": 1290},
                        {"techSize": "S", "wbSize": "46", "price": 1290},
                        {"techSize": "M", "wbSize": "48", "price": 1290},
                        {"techSize": "L", "wbSize": "50", "price": 1290},
                        {"techSize": "XL", "wbSize": "52", "price": 1290}
                    ]
                }
            ]
        }
    ]

    response = requests.post('https://suppliers-api.wildberries.ru/content/v2/cards/upload', headers=headers,
                             json=payload)
    response_data = response.json()
    return print(response_data)


def take_list_nomenclatur_2():
    params = {
        'settings': {
            'cursor': {
                'limit': 100
            },
            'filter': {
                'withPhoto': -1
            }
        }
    }
    response = requests.post('https://suppliers-api.wildberries.ru/content/v2/get/cards/list', json=params, headers=headers)
    response_data = response.json()
    cursor = response_data.get('cursor', {})
    nmID = cursor.get('nmID')
    updatedAt = cursor.get('updatedAt')

    # создание объекта пандас первого
    data = response_data['cards']
    df_all = pd.DataFrame(data)

    total = 10000  # просто переборщик не особо правильная логика тут
    while total >= 100:
        payload2 = {
          'settings': {
            'filter': {
              'textSearch': "",

              'tagIDs': [],
              'objectIDs': [],
              'brands': [],
              'imtID': 0,
              'withPhoto': -1
            },
            'cursor': {
              'updatedAt': str(updatedAt),
              'nmID': nmID,
              'limit': 100
            }
          }
        }

        response = requests.post('https://suppliers-api.wildberries.ru/content/v2/get/cards/list', json=payload2, headers=headers)
        response_data = response.json()

        # получение курсора для повторного запроса
        cursor = response_data.get('cursor', {})
        nmID = cursor.get('nmID')
        updatedAt = cursor.get('updatedAt')
        total = cursor.get('total')

        # добавление по 100 к объекту пандас
        data = response_data['cards']
        df2 = pd.DataFrame(data)
        df_all = pd.concat([df_all, df2], ignore_index=True)  # тут не выходит варнингов

    df_mini = df_all[['nmID', 'sizes', 'title', 'description', 'vendorCode']]
    df_mini_sorted = df_mini.sort_values('vendorCode')
    return df_mini_sorted


def take_list_nomenclatur_4(articul: str):
    params = {
        'settings': {
            'cursor': {
                'limit': 100
            },
            'filter': {'withPhoto': -1, 'textSearch': articul}
        }
    }
    response = requests.post('https://suppliers-api.wildberries.ru/content/v2/get/cards/list', json=params, headers=headers)
    response_data = response.json()
    # print(response_data, '4')
    nmID_value = response_data['cursor']['nmID']
    # print(nmID_value)
    return nmID_value


def articul_to_articul_wb(articul: str, list_nomenklatur: pd.DataFrame) -> str:  # получили весь список номенклатур где есть артикул и артикулВБ
    df_filtered = list_nomenklatur[list_nomenklatur['vendorCode'] == articul]
    nmID_values = df_filtered['nmID'].unique()[0]
    return nmID_values


def paste_images_in_card_wb(userid: str, postid: str, articul_wb: str, file: str, xphotonumber: str):
    headers = {
        'Authorization': API_stat,
        'X-Nm-Id': str(articul_wb),
        'X-Photo-Number': str(xphotonumber)
    }
    files = {'uploadfile': open(f'website/static/uploads/{userid}/{postid}/{file}', 'rb')}
    resonse = requests.post('https://suppliers-api.wildberries.ru/content/v3/media/file', headers=headers, files=files)
    print(file, resonse.json())
    # time.sleep(5)
    return


def approve_kt(userid: str, postid: str):  # одобрение и автоматическая публикация КТ
    user = User.query.filter_by(user_id=userid).first()
    email = user.email

    path = f'website/static/uploads/{userid}/{postid}'
    add_new_card_on_wb(f'{userid}-{postid}')  # создает КТ без картинок
    articul = f'{userid}-{postid}'
    time.sleep(10)  # необходимое время чтобы КТ добавилась

    try:
        # articul_wb = articul_to_articul_wb(articul, take_list_nomenclatur_2())  # работает получение articul_wb
        articul_wb = take_list_nomenclatur_4(articul)  # тоже работает получение articul_wb
        # тут возможно нужно добавить создание
        WbPost.set_articul_wb(articul_wb, articul, postid, userid)  # добавили ссылку на страницу на ВБ и сам артикул!

        wb_kt_published(email, articul_wb)
    except Exception as ex:
        print(ex)

    list_images = os.listdir(path)      # загрузка картинок артикула на ВБ
    print(list_images)
    images_count = 0
    for image in list_images:
        images_count = images_count + 1  # Номер медиафайла на загрузку, начинается с 1
        try:
            paste_images_in_card_wb(userid, postid,  articul_wb, image, images_count)
        except Exception as ex:
            print(ex)
    return
