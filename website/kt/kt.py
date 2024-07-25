import os
import shutil

from flask import Blueprint
from flask import render_template, request
from flask import session, redirect, url_for, flash
from werkzeug.utils import secure_filename

from .. import db
from ..auth.utils_auth import login_required
from ..kt.utils_pic import check_image_validity, check_images_validity, remove_files_in_folder
from ..models import Post, Image, Comments, WbPost, AdminComments
from ..settings import UPLOAD_FOLDER
from ..status.utils_status import change_moderate

kt = Blueprint('kt', __name__)


@kt.route('/post/<int:post_id>', methods=['GET', 'POST'])
# @login_required
def show_post(post_id):
    errors = []
    if 'user_id' in session:
        user_id = session.get('user_id')

    post = Post.query.get_or_404(post_id)
    image_urls = Image.get_image_urls_for_post(post_id)  # загрузка постов
    user_role = session.get('user_role')
    comments = Comments.query.filter_by(post_id=post_id).all()
    acomments = AdminComments.query.filter_by(post_id=post_id).all()
    wbpost = WbPost.query.filter_by(post_id=post_id).first()

    #  проваливаемся в страницу / как-то это прибрать лучше
    if user_role == 'admin' and post.post_status in ["на модерации", "отклонено", "опубликовано"]:  # если у нас админ
        return render_template('kt/post-admin-wb.html', post=post, image_urls=image_urls, comments=comments, wbpost=wbpost, acomments=acomments)
    if user_role == 'user' and post.post_status in ["на модерации", "опубликовано", "заархивировано"]:  # если НЕ админ
        return render_template('kt/post-wb.html', post=post, image_urls=image_urls, comments=comments, wbpost=wbpost, acomments=acomments)

    if request.method == 'POST':
        if 'edit_image' in request.form:
            image_file = request.files['image']
            # далее проверка валидности
            user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
            post_folder = os.path.join(user_folder, str(post.post_id))
            filename = secure_filename(image_file.filename)  # не меняем сначала имя у файла
            image_file.save(os.path.join(post_folder, filename))
            # Урл картинки не переименованой
            image_url = os.path.join(post_folder, filename)  # урл с website\static\\
            # проверка изображения на валидность
            valid, error = check_image_validity(str(image_url))

            if error:
                errors.extend(error)  # Добавляем ошибку в список

            if valid:
                # Удаление картинок из папки, у которых image.image_order = 0
                images_to_delete = Image.query.filter_by(post_id=post_id).filter(Image.image_order == 0).all()

                if images_to_delete:
                    for image in images_to_delete:
                        image_path = f'website/static/uploads/{user_id}/{post_id}/{image.image_url.rsplit("/", 1)[-1]}'
                        if os.path.exists(image_path):  # Проверяем, существует ли файл
                            os.remove(image_path)  # Удаляем файл из папки

                Image.add_images_and_urls(user_id, post_id, 0, image_file)  # функция сохранения урла и картинки
                image_urls = Image.get_image_urls_for_post(post_id)
                return render_template('kt/post.html', post=post, post_id=post_id, image_urls=image_urls, comments=comments, acomments=acomments, message='Исходная картинка обновлена')
            else:
                os.remove(image_url)  # удаление если картинка не подходит по валидации
                return render_template('kt/post.html', post=post, post_id=post_id, image_urls=image_urls, comments=comments, acomments=acomments, errors=errors)

        elif 'edit_multi_image' in request.form:
            image_files: list = request.files.getlist('multi_images')

            # тут вставить сохранение во временной папке /temp для проверки
            user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))
            os.makedirs(user_folder, exist_ok=True)
            post_folder = os.path.join(user_folder, str(post_id), 'temp')  # создали папку temp
            os.makedirs(post_folder, exist_ok=True)
            image_url_list = []
            mokupname_list = []
            for mokup in image_files:
                mokupname = secure_filename(mokup.filename)
                mokup.save(os.path.join(post_folder, mokupname))
                # урл мокапа сохраненного
                mokup_image_url = os.path.join(post_folder, mokupname)
                image_url_list.append(str(mokup_image_url))
                mokupname_list.append(mokupname)

            valid_files, error = check_images_validity(image_url_list)  # проверка работает

            if error:
                errors.extend(error)

            index = 1  # Начальное значение для index
            # запись провалидированных мокапов и удаление старых
            if valid_files:
                # Удаление картинок из папки, у которых image.image_order > 0
                images_to_delete = Image.query.filter_by(post_id=post_id).filter(Image.image_order > 0).all()
                if images_to_delete:
                    for image in images_to_delete:
                        image_path = f'website/static/uploads/{user_id}/{post_id}/{image.image_url.rsplit("/", 1)[-1]}'
                        if os.path.exists(image_path):  # Проверяем, существует ли файл
                            os.remove(image_path)  # Удаляем файл из папки

                Image.delete_images_with_order_greater_than(post_id, 0)  # это функция удаления урлов > 0

                # залили новые мокапы
                for image_file in image_files:
                    Image.add_images_and_urls(user_id, post_id, index,
                                              image_file)  # ошибка в сохранении картинки тут!
                    index += 1  # Увеличиваем значение index на 1 для следующего изображения

                # перенесли из папки temp норм картинки и удалили папку temp
                source_directory = f'website/static/uploads/{user_id}/{post_id}/temp'
                target_directory = f'website/static/uploads/{user_id}/{post_id}/'
                files_in_temp = os.listdir(post_folder)
                for file_name in files_in_temp:
                    source_file = os.path.join(source_directory, file_name)
                    target_file = os.path.join(target_directory, file_name)
                    shutil.copy(source_file, target_file)
                remove_files_in_folder(source_directory)  # удалили temp с мокапами

                image_urls = Image.get_image_urls_for_post(post_id)
                return render_template('kt/post.html', post=post, post_id=post_id, image_urls=image_urls, comments=comments, acomments=acomments, message='Мокапы обновлены')
            else:
                return render_template('kt/post.html', post=post, post_id=post_id, image_urls=image_urls, comments=comments, acomments=acomments, errors=errors)

        elif 'edit_title_content' in request.form:
            new_title = request.form['post_title']
            new_content = request.form['post_content']
            post.title = new_title
            post.content = new_content
            db.session.commit()
            return render_template('kt/post.html', post=post, post_id=post_id, image_urls=image_urls, comments=comments,
                                   acomments=acomments, message='Описание карточки товара изменено')

    return render_template('kt/post.html', post=post, post_id=post_id, image_urls=image_urls, comments=comments, acomments=acomments, errors=errors)


# это функция заметь !
def add_post(title, content, user_id, post_status):
    errors = []
    new_post = Post(title=title, content=content, user_id=user_id, post_status=post_status)
    db.session.add(new_post)
    db.session.commit()

    if 'file' in request.files:
        file = request.files['file']
        user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))  # тут берется из конфига app.config['UPLOAD_FOLDER']
        os.makedirs(user_folder, exist_ok=True)
        post_folder = os.path.join(user_folder, str(new_post.post_id))
        os.makedirs(post_folder, exist_ok=True)

        filename = secure_filename(file.filename)  # не меняем сначала имя у файла
        file.save(os.path.join(post_folder, filename))

        # Урл картинки не переименованой
        image_url = os.path.join(post_folder, filename)  # урл с website\static\\

        valid, error = check_image_validity(str(image_url))

        if error:
            errors.extend(error)

        if 'files' in request.files:
            files: list = request.files.getlist('files')
            print(files)
            image_url_list = []
            for idx, mokup in enumerate(files):
                mokupname = secure_filename(mokup.filename)
                mokup.save(os.path.join(post_folder, mokupname))
                # урл мокапа сохраненного
                mokup_image_url = os.path.join(post_folder, mokupname)

                # Добавляем запись об изображении в таблицу Image БЕЗ website/static
                new_image_url = mokup_image_url.replace('website\static\\', '').replace('\\', '/')
                new_image = Image(image_url=new_image_url, user_id=user_id, post_id=new_post.post_id,
                                  image_order=idx + 1)
                db.session.add(new_image)
                db.session.commit()
                image_url_list.append(str(mokup_image_url))

            valid_files, error = check_images_validity(image_url_list)  # надо возвращать тут list а не значение просто

            if error:
                errors.extend(error)  # Добавляем ошибку в список / исправить на extend с листом

            if valid and valid_files:
                # работаем тут после валидации с исходником
                filename = secure_filename(file.filename)
                file_extension = filename.split(".")[-1]
                new_filename = f"{user_id}-{new_post.post_id}.{file_extension}"  # тут имя и поверх записали filename
                os.rename(os.path.join(post_folder, filename), os.path.join(post_folder, new_filename))

                image_url = os.path.join(post_folder, new_filename)  # взяли урл переименованой картинки
                # запись в таблицу Image  БЕЗ website/static
                new_image_url = image_url.replace('website\static\\', '').replace('\\', '/')
                new_image = Image(image_url=new_image_url, user_id=user_id, post_id=new_post.post_id, image_order=0)
                db.session.add(new_image)
                db.session.commit()

                # работаем с мокапами после валидации - нет и не нужно

                # отправляем на модерацию
                errors = 'Карточка товара с картинкой отправлена на модерацию'
                if post_status == 'на модерации':
                    # добавить отправку на модерацию - при нажатии на кнопку не отправляет
                    change_moderate(new_post.post_id)
                return True, errors
            else:
                Image.delete_images_and_folders(user_id, new_post.post_id)  # удаление из папки всех картинок и саму папку
                Image.delete_image_by_user_post_id(user_id, new_post.post_id)  # удаление из таблицы Image
                new_post.delete()  # удаление поста из таблицы Post
                print(errors)
                return False, errors
    return render_template('kt/create_post.html', errors=errors)


@kt.route('/create_post', methods=['GET', 'POST'])
# @login_required
def create_post():
    if request.method == 'GET':
        if 'user_id' in session:
            return render_template('kt/create_post.html')

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        user_id = session.get('user_id')
        if 'draft' in request.form:  # Проверяем, была ли нажата кнопка "Сохранить как черновик"
            post_status = 'черновик'
            valid, errors = add_post(title, content, user_id, post_status)
            if valid:
                return redirect(url_for('views.admin'))

        elif 'moderation' in request.form:  # Проверяем, была ли нажата кнопка "Отправить на модерацию"
            post_status = 'на модерации'
            valid, errors = add_post(title, content, user_id, post_status)
            if valid:
                return redirect(url_for('views.admin'))
    else:
        return 'Error create post'

    return render_template('kt/create_post.html', errors=errors)


# Маршрут для обработки отправленного комментария
@kt.route('/add_comment', methods=['POST'])
# @login_required
def add_comment():
    if 'user_id' in session:
        user_id = session.get('user_id')

    comment_content = request.form.get('comment_text')
    post_id = request.form.get('post_id')  # Получаем post_id из формы
    user_id = session.get('user_id')
    AdminComments.add_comment(comment_content, post_id, user_id)
    flash('Комментарий к карточке товара добавлен')
    return redirect(url_for('kt.show_post', post_id=post_id))
