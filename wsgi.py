from website import create_app, db

app = create_app()

if __name__ == '__main__':
    # app.run(debug=True)
    with app.app_context():  # создание бд
        db.create_all()
        app.run(debug=True, port=5000, host='0.0.0.0')  # заменить на конкретный IP-адрес сервера
