import datetime

import pandas as pd
from flask import Blueprint
from flask import render_template, request
from flask import session, redirect, url_for
from flask_caching import Cache
from sqlalchemy import func

from . import db
from .auth.utils_auth import login_required
from .models import Post, Image, User, Payouts, Payouts_bank, Balance, WbPost, Rating

cache = Cache()

views = Blueprint('views', __name__)


@views.route('/')
def index():
    return render_template('index.html')


def post_with_images(user_id):
    # логика для нумерации на странице
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Количество элементов на странице
    # images_per_post = 1  # Количество изображений на пост
    offset = (page - 1) * per_page

    posts_with_images = db.session.query(Post, Image).join(Image).filter(Post.user_id == user_id,
                                                                         Image.image_order == 0).order_by(
        Post.post_id.desc()).offset(
        offset).limit(per_page).all()

    # --
    posts = Post.get_all_posts()
    posts_3status = Post.get_posts_by_status(['на модерации', 'опубликовано', 'отклонено', 'черновик', 'заархивировано'])
    status = request.args.get('status', 'all')  # Получаем параметр "status" из URL

    status_counts = {
        'черновик': len([post for post in posts if post.post_status == 'черновик']),
        'на модерации': len([post for post in posts if post.post_status == 'на модерации']),
        'опубликовано': len([post for post in posts if post.post_status == 'опубликовано']),
        'отклонено': len([post for post in posts if post.post_status == 'отклонено']),
        'заархивировано': len([post for post in posts if post.post_status == 'заархивировано'])
    }

    if status == 'на модерации':
        filtered_posts = [post for post in posts if post.post_status == 'на модерации']
    elif status == 'черновик':
        filtered_posts = [post for post in posts if post.post_status == 'черновик']
    elif status == 'опубликовано':
        filtered_posts = [post for post in posts if post.post_status == 'опубликовано']
    elif status == 'отклонено':
        filtered_posts = [post for post in posts if post.post_status == 'отклонено']
    elif status == 'заархивировано':
        filtered_posts = [post for post in posts if post.post_status == 'заархивировано']
    else:
        filtered_posts = posts_3status
    # Сортировка по Id в порядке убывания
    filtered_posts_sorted = sorted(filtered_posts, key=lambda x: x.post_id, reverse=True)

    return posts_with_images, filtered_posts_sorted, page, status, status_counts


def rating_user(user_id):
    user_rating = Rating.query.filter_by(user_id=user_id).first()
    if user_rating is None:
        return {
            'sum_money': 0,
            'sum_cards': 0,
            'rating': 0
        }
    return user_rating.sum_money, user_rating.sum_cards, user_rating.rating  # возврат на главной инфо


@views.route('/admin', methods=['GET'])  # работа с админкой
@login_required
def admin():
    if 'user_id' in session:
        user_id = session.get('user_id')
        posts_with_images, filtered_posts_sorted, page, status, status_counts = post_with_images(user_id)
        sum_money, sum_cards, rating = rating_user(user_id)
        # check
        check_max_cards = Rating.check_max_sum_cards(user_id)
        # разница между карточками по неделям (или это лучше вообще в отдельную таблицу запулить и не вызывать)
        difference_in_cards = Rating.difference_in_sum_cards(user_id)
        difference_in_money = Rating.difference_in_sum_money(user_id)

        return render_template('admin.html', posts_images=posts_with_images, posts=filtered_posts_sorted, page=page, selected_status=status, status_counts=status_counts, sum_money=sum_money, sum_cards=sum_cards, rating=rating, check_max_cards=check_max_cards, difference_in_cards=difference_in_cards, difference_in_money=difference_in_money)
    else:
        return redirect(url_for('views.index'))


@views.route('/superadmin', methods=['GET'])
# @login_required
def superadmin():
    posts = Post.get_all_posts()
    posts_3status = Post.get_posts_by_status(
        ['на модерации', 'опубликовано', 'отклонено',  'заархивировано'])
    status = request.args.get('status', 'all')  # Получаем параметр "status" из URL

    status_counts = {
        'на модерации': len([post for post in posts if post.post_status == 'на модерации']),
        'опубликовано': len([post for post in posts if post.post_status == 'опубликовано']),
        'отклонено': len([post for post in posts if post.post_status == 'отклонено']),
        'заархивировано': len([post for post in posts if post.post_status == 'заархивировано'])
    }
    status = request.args.get('status', 'all')  # Получаем параметр "status" из URL
    # Выводим отладочную информацию
    print(f"Received status from URL: {status}")

    if status == 'на модерации':
        filtered_posts = [post for post in posts if post.post_status == 'на модерации']
    elif status == 'опубликовано':
        filtered_posts = [post for post in posts if post.post_status == 'опубликовано']
    elif status == 'отклонено':
        filtered_posts = [post for post in posts if post.post_status == 'отклонено']
    elif status == 'заархивировано':
        filtered_posts = [post for post in posts if post.post_status == 'заархивировано']
    else:
        filtered_posts = posts_3status

    # Сортировка по Id в порядке убывания
    filtered_posts_sorted = sorted(filtered_posts, key=lambda x: x.post_id, reverse=True)

    return render_template('superadmin.html', posts=filtered_posts_sorted, selected_status=status, status_counts=status_counts)


@views.route('/get_settings', methods=['GET'])
# @login_required
def get_settings():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    return render_template('auth/settings.html', username=user.username, email=user.email)


@views.route('/education', methods=['GET'])
def education():
    return render_template('static_page/education.html')


@views.route('/oferta', methods=['GET'])
def oferta():
    return render_template('static_page/oferta.html')


@views.route('/confident', methods=['GET'])
def confident():
    return render_template('static_page/confident.html')
