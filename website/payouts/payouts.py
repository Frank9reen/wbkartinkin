import datetime

import pandas as pd
from flask import Blueprint
from flask import render_template, request
from flask import session, redirect, url_for
from flask_caching import Cache
from sqlalchemy import func

from .. import db
from ..auth.utils_auth import login_required
from ..models import Payouts, Payouts_bank

cache = Cache()

payouts = Blueprint('payouts', __name__)


@payouts.route('/payouts', methods=['GET'])
@login_required
def payouts_func():
    if 'user_id' in session:
        user_id = session.get('user_id')
        payouts_data = db.session.query(
            Payouts.payout_id,
            Payouts.submission_date,
            Payouts.processing_date,
            Payouts.amount,
            Payouts.payout_type,
            func.concat('***', func.right(Payouts_bank.card_number, 4)).label('card_number'),
            Payouts.status).join(Payouts_bank).filter(Payouts.user_id == user_id).all()

        df = pd.DataFrame(payouts_data,
                          columns=['ID заявки', 'Дата подачи', 'Дата обработки', 'Сумма', 'Тип',
                                   'Номер карты', 'Статус'])

        df = df.fillna('')
        df = df.sort_values(by='ID заявки', ascending=False)
        return render_template('payouts/payouts.html', payouts_data=df.to_html(classes='payout-table-css', index=False))
    else:
        return "Ошибка: 'user_id' отсутствует в сессии."


@payouts.route('/payouts_bank', methods=['POST'])
@login_required
def submit_form():
    full_name = request.form['full_name']
    phone_number = request.form['phone_number']
    card_number = request.form['card_number']

    # Получение даты подачи для ассоциированной записи в таблице Payouts
    submission_date = datetime.date.today()

    if 'user_id' in session:
        user_id = session.get('user_id')

        # Создание новой записи в таблице Payouts с учетом user_id
        new_payout = Payouts(submission_date=submission_date, payout_type='Банк. карта', status='в обработке', user_id=user_id)
        db.session.add(new_payout)
        db.session.commit()

        # Получение ID только что созданной записи Payouts
        new_payout_id = new_payout.payout_id

        # Создание новой записи в таблице Payouts_bank и связь с записью в таблице Payouts
        new_payout_bank = Payouts_bank(full_name=full_name, phone_number=phone_number, card_number=card_number, payout_id=new_payout_id)
        db.session.add(new_payout_bank)
        db.session.commit()

        return render_template('payouts/payouts.html')
    else:
        return "Ошибка: 'user_id' отсутствует в сессии."


@payouts.route('/payouts_data', methods=['GET'])
@login_required
def payouts_data():
    payouts_data = db.session.query(Payouts_bank, Payouts).join(Payouts).order_by(Payouts.payout_id.desc()).all()
    return render_template('payouts/payouts-admin.html', payouts_data=payouts_data)


@payouts.route('/payouts/<int:payout_id>', methods=['GET', 'POST'])
@login_required
def show_payouts(payout_id):
    payout = Payouts.query.get(payout_id)  # Получение заявки по payout_id
    bank_info = Payouts_bank.query.filter_by(payout_id=payout_id).first()  # Получение информации из таблицы payouts_bank

    if payout and bank_info:
        combined_info = {
            'payout_id': payout.payout_id,
            'full_name': bank_info.full_name,
            'phone_number': bank_info.phone_number,
            'card_number': bank_info.card_number,
            'submission_date': payout.submission_date,
            'processing_date': payout.processing_date,
            'amount': payout.amount,
            'payout_type': payout.payout_type,
            'recipient': payout.recipient,
            'status': payout.status
        }

        return render_template('payouts/payout-admin-id.html', combined_info=combined_info)
    else:
        return 'Заявка не найдена', 404


@payouts.route('/payouts/<int:payout_id>/approve', methods=['POST'])
@login_required
def change_payout_status(payout_id):
    payout = Payouts.query.get(payout_id)
    if not payout:
        return 'Payout not found'

    payout.set_processing_date()
    payout.status = 'оплачено'
    db.session.commit()
    return redirect(url_for('payouts.payouts_data'))

