from flask import Flask
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging import StreamHandler

db = SQLAlchemy()
bcrypt = Bcrypt()
mail = Mail()
migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('settings.py')

    # Настройка уровня логирования
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger('sqlalchemy.engine')
    logger.setLevel(logging.INFO)

    # Создаем обработчик для вывода логов в консоль
    handler = StreamHandler()
    handler.setLevel(logging.INFO)

    # Создаём формат логов
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Добавляем обработчик в логгер приложения
    app.logger.addHandler(handler)



    db.init_app(app)
    migrate.init_app(app, db, render_as_batch=True)  # сделано у техервова м.

    mail.init_app(app)
    bcrypt.init_app(app)

    from .auth.auth import auth
    from .views import views
    from .status.status import status
    from .kt.kt import kt
    from .statistics.statistics import statistics
    from .message.errors import errors
    from .message.message import message
    from .payouts.payouts import payouts
    from .rating.rating import rating

    app.register_blueprint(auth)
    app.register_blueprint(views)
    app.register_blueprint(status)
    app.register_blueprint(kt)
    app.register_blueprint(statistics)
    app.register_blueprint(errors)
    app.register_blueprint(message)
    app.register_blueprint(payouts)
    app.register_blueprint(rating)

    app.logger.info('Flask приложение успешно создано')

    return app
