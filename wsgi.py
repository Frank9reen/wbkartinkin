from website import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():  # создание бд
        db.create_all()
        app.run(debug=True)
        # app.run(debug=True, port=5000, host='0.0.0.0')  # было раньше так
