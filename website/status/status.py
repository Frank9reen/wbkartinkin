from flask import Blueprint
from flask import jsonify
from flask import session, redirect, url_for

from .. import db
from ..kt.utils_wb import approve_kt
from ..models import Post, Image, Comments, Balance
from ..kt.yadisk import yadisk_upload_kartinka

status = Blueprint('status', __name__)


@status.route('/posts/<int:post_id>/moderate', methods=['POST'])
def moderate_post(post_id):
    post = Post.query.get(post_id)
    user_id = session.get('user_id')
    if post:
        post.post_status = 'на модерации'
        db.session.commit()
        comment_text = 'Отправлено на модерацию'
        Comments.add_comment(comment_text, post_id, user_id)
        return redirect(url_for('kt.show_post', post_id=post_id))  # можно отсюда убрать этот редирект
    return 'Пост не найден'


@status.route('/posts/<int:post_id>/archive', methods=['POST'])
def archive_post(post_id):
    post = Post.query.get(post_id)
    user_id = session.get('user_id')
    if post:
        post.post_status = 'заархивировано'
        db.session.commit()
        comment_text = 'Заархивировано. Карточка товара будет закрыта и удалена на ВБ в течение 30 дней '
        Comments.add_comment(comment_text, post_id, user_id)
        return redirect(url_for('kt.show_post', post_id=post_id))
    return jsonify({'error': 'Post do not find'})


@status.route('/posts/<int:post_id>/delete', methods=['POST'])  # может в kt.py перенести
def delete_post(post_id):
    post = Post.query.get(post_id)
    Image.delete_images_and_folders(post.user_id, post_id)  # Удалить изображения и папки на сервере
    images = Image.query.filter_by(post_id=post_id).all()  # Найти связанные изображения
    if post:
        for image in images:  # Удалить связанные изображения
            image.delete()
        comments = Comments.query.filter_by(post_id=post_id).all()
        for comment in comments:
            comment.delete_comment()
        post.delete()   # Удалить пост в бд
        return redirect(url_for('views.admin'))
    else:
        return jsonify({'error': 'Post not found'}), 404


@status.route('/posts/<int:post_id>/approve', methods=['POST'])  # создание КТ и заливка картинок на ВБ по апи
def approve_post(post_id):
    post = Post.query.get(post_id)
    user_id = session.get('user_id')  # это будет ID админа = 2
    if post:
        post.post_status = 'опубликовано'
        db.session.commit()
        # Добавим комментарий к посту
        comment_text = 'Опубликовно на ВБ'
        Comments.add_comment(comment_text, post_id, user_id)
        # выполнение функции создания КТ и заливки картинок на ВБ
        approve_kt(post.user_id, post_id)
        # добавление картинки в Ya.disk
        yadisk_upload_kartinka(f'website/static/{post.user_id}/{post.user_id}-{post_id}/{post.user_id}-{post_id}.png')
        # добавление 50 руб. в баланс day_balance в Balance
        Balance.add_50_to_balance(user_id)
        return redirect(url_for('views.superadmin'))
    return 'Post do not find'


@status.route('/posts/<int:post_id>/reject', methods=['POST'])
def reject_post(post_id):
    post = Post.query.get(post_id)
    user_id = session.get('user_id')
    if post:
        post.post_status = 'отклонено'
        db.session.commit()
        # Добавим комментарий к посту
        comment_text = 'Отклонено. Необходимо внести изменения'
        Comments.add_comment(comment_text, post_id, user_id)
        return redirect(url_for('views.superadmin'))
    return 'Post do not find'
