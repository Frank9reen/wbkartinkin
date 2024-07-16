import os

import requests
from ..settings import YADISK_TOKEN


headers = {'Authorization': 'OAuth ' + YADISK_TOKEN}


def yadisk_upload_kartinka(kartinka_path):  # тут наверное лучше только path к картинке исходнику давать
    if os.path.exists(kartinka_path):
        kartinka_name = os.path.basename(kartinka_path)
        response = requests.get('https://cloud-api.yandex.net/v1/disk/resources/upload',
                                params={'path': f'kartinkin/{kartinka_name}', 'overwrite': True},
                                headers={
                                    'Authorization': 'OAuth ' + YADISK_TOKEN})  # вот тут путь указывается на Я.диске     # Запрос на получение URL для загрузки файла
        upload_data = response.json()
        with open(f'{kartinka_path}', 'rb') as file:  # путь к картинке на нашем сервере - вот тут поправить надо
            response = requests.put(upload_data['href'], headers=headers, data=file)
        if response.status_code == 201:
            print('Файл успешно загружен на Яндекс.Диск')
        else:
            print('Ошибка при загрузке файла на Яндекс.Диск. Код ошибки:', response.status_code)
    else:
        print(f'Картинка не найдена по указанному пути {kartinka_path}')
