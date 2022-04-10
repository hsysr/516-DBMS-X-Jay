from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from werkzeug.urls import url_parse
from flask_login import current_user
from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DecimalField, FormField, FieldList, TextAreaField, SelectMultipleField, RadioField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, InputRequired, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.datastructures import MultiDict

from .models.product import Product
from .models.inventory import Inventory
from .models.purchase import Purchase
from .models.user import User

import os

from flask import Blueprint
bp = Blueprint('purchase', __name__)
app = Flask(__name__)

class FulfillmentForm(FlaskForm):
    searchfield = RadioField('Search for:', choices=[('ALL', 'ALL'),
                                                     ('Fullfilled', 'Fullfilled'),
                                                     ('To be Fullfilled', 'To be Fullfilled')],
                                                default = 'ALL')
    submit = SubmitField('Search')


@bp.route('/order/fulfillment', methods = ['GET', 'POST'])
def order_fulfillment():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    fulfillmentForm = FulfillmentForm()
    if request.method == 'POST':
        if fulfillmentForm.validate_on_submit():
            if fulfillmentForm.searchfield.data == 'ALL':
                purchase_ids = Purchase.get_all_by_sid(current_user.id)
            elif fulfillmentForm.searchfield.data == 'Fullfilled':
                purchase_ids = Purchase.get_all_fullfilled_by_sid(current_user.id)
            else:
                purchase_ids = Purchase.get_all_unfullfilled_by_sid(current_user.id)
    else:
        purchase_ids = Purchase.get_all_by_sid(current_user.id)
    purchases = []
    for purchase_id in purchase_ids:
        pur = []
        pur.append(purchase_id)
        buyer = User.get_by_purchase_id(purchase_id)
        pur.append(buyer)
        purchase_time, overall_fulfill = Purchase.get_info(purchase_id)
        pur.append(purchase_time)
        pur.append(overall_fulfill)
        pur.append(Purchase.get_by_id_sid(purchase_id, current_user.id))
        products = [Product.get(p.pid) for p in pur[4]]
        pur.append(products)
        purchases.append(pur)
    return render_template('fulfillment.html', purchases = purchases, fulfillmentForm = fulfillmentForm)


@bp.route('/order/fulfill/<purchase_id>/<pid>', methods = ['GET', 'POST'])
def fulfill_order(purchase_id, pid):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    Purchase.fulfill(purchase_id, pid, current_user.id)
    return redirect(url_for('purchase.order_fulfillment'))
