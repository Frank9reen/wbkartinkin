from PIL import Image
import os
import re
from io import BytesIO


def check_if_image(filename):
    try:
        img = Image.open(filename)
        img.verify()
        return True
    except Exception as e:
        return False


def check_jfif_format(file_path):
    try:
        img = Image.open(file_path)
        if img.format == 'JPEG' and img.format_description == 'JPEG (ISO 10918)':
            return False
        else:
            return True
    except Exception as e:
        return False, f"Ошибка: {str(e)}"


def check_dpi_from_file(file_path):
    try:
        file_name = os.path.basename(file_path)
        img = Image.open(file_path)
        dpi = img.info.get('dpi')
        if dpi is not None and all(d > 300 for d in dpi):
            return True, None
        else:
            return False, f"Ошибка: Недостаточное разрешение у {file_name} (минимум 300 dpi)."
    except Exception as e:
        return False, f"Ошибка: {str(e)}"


def check_image_size_from_file(file_path):
    try:
        img = Image.open(file_path)
        width, height = img.size
        dpi = img.info.get('dpi')

        if dpi is not None:
            width_cm = width / dpi[0] * 2.54
            height_cm = height / dpi[1] * 2.54
            width_cm_rounded = round(width_cm)
            height_cm_rounded = round(height_cm)

            if width_cm <= 35 and height_cm <= 35:
                return True, None
            else:
                return False, f"Ошибка: Размер исходника слишком большой - ({ width_cm_rounded} см, {height_cm_rounded} см)"
        else:
            return False, "Ошибка: DPI изображения не найдено."
    except Exception as e:
        return False, f"Ошибка: {str(e)}"


def check_image_validity(file_path: str) -> (bool, list):
    errors = []

    if not check_if_image(file_path):
        errors.append(f"Ошибка: Картинка исходник не является изображением или повреждена.")
        return False, errors

    if not check_jfif_format(file_path):
        errors.append("Ошибка: Формат JFIF не поддерживается.")
        return False, errors

    dpi_valid, dpi_error = check_dpi_from_file(file_path)
    if not dpi_valid:
        errors.append(dpi_error)

    size_valid, size_error = check_image_size_from_file(file_path)
    if not size_valid:
        errors.append(size_error)

    if errors:
        return False, errors
    else:
        return True, None


def check_file_size(image_url_list: list):
    max_file_size = 10 * 1024 * 1024  # Максимально допустимый размер файла (10 МБ)

    errors = []
    for image_url in image_url_list:
        try:
            file_name = os.path.basename(image_url)
            file_size = os.path.getsize(image_url)  # Получаем размер файла
            if file_size > max_file_size:
                errors.append(f"Ошибка: Размер файла {file_name} превышает 10 МБ")
        except FileNotFoundError:
            errors.append(f"Ошибка: Файл по пути не найден")

    if errors:
        return False, errors
    else:
        return True, None


def check_if_images(image_url_list: list):
    errors = []
    for image_url in image_url_list:
        if not check_if_image(image_url):
            errors.append(f"Ошибка: Мокап не является изображением или поврежден.")
            return False, errors
    if errors:
        return False, errors
    else:
        return True, None


def check_images_validity(image_url_list: list) -> (bool, list):
    errors = []

    valid, error = check_if_images(image_url_list)
    if not valid:
        errors.extend(error)
        return False, errors

    valid, error = check_file_size(image_url_list)
    if not valid:
        errors.extend(error)

    if len(image_url_list) > 5:
        errors.append(f"Ошибка: Вы пытаетесь загрузить {len(image_url_list)} мокапов. Разрешено не более 5 мокапов.")

    for image_url in image_url_list:
        file_name = os.path.basename(image_url)

        if not check_jfif_format(image_url):
            errors.append(f"Ошибка: Мокап {file_name} в формате JFIF, который не поддерживается.")

        image = Image.open(image_url)
        width, height = image.size
        if width < 700 or height < 900:
            errors.append(f"Ошибка: Размеры изображения {file_name} должны быть не меньше 700x900 пикселей.")

    if errors:
        return False, errors
    else:
        return True, None


def remove_files_in_folder(folder_path):
    # Перебираем все файлы в указанной папке и удаляем их
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"Файл {file_name} успешно удален")
        except Exception as e:
            print(f"Ошибка при удалении файла {file_name}: {str(e)}")
    os.rmdir(folder_path)  # Удаляем пустую папку
