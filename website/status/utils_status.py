from ..models import Post, Comments
from .. import db
from flask import session, url_for, redirect


def change_moderate(post_id):  # работае ли эта функция? или закрыть
    post = Post.query.get(post_id)
    user_id = session.get('user_id')
    if post:
        post.post_status = 'на модерации'
        db.session.commit()
        comment_text = 'Отправлено на модерацию'
        Comments.add_comment(comment_text, post_id, user_id)

    return 'обновили на Отправлено на модерацию'
