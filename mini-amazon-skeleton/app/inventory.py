from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DecimalField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, InputRequired
from werkzeug.datastructures import MultiDict

from .models.product import Product

from flask import Blueprint
bp = Blueprint('inventory', __name__)
products = []

class InventoryForm(FlaskForm):
    quantity = IntegerField('Quantity',
                            validators=[NumberRange(min=0, message='Quantity cannot be negative')], default = 1)
    price = DecimalField('Price',
                         validators=[DataRequired(message='Quantity must be an number'), NumberRange(min=0, message='Price cannot be negative')], default = 1)
    submit = SubmitField('Change')

@bp.route('/inventory', methods = ['GET', 'POST'])
def inventory():
    global products
    if (len(products) == 0):
        products = Product.get_all(True)
    # get all available products for sale:
    forms = []
    for product in products:
        prefix = 'form' + str(product.id)
        if request.method == 'GET':
            form = InventoryForm(prefix = prefix, formdata=MultiDict({prefix + '-quantity': product.quantity, prefix + '-price': product.price}))
        else:
            form = InventoryForm(prefix = prefix)
            if not form.submit.data:
                form = InventoryForm(prefix = prefix, formdata=MultiDict({prefix + '-quantity': product.quantity, prefix + '-price': product.price}))
        forms.append(form)
    for i, form in enumerate(forms):
        if form.validate_on_submit():
            print("data change:", form.quantity.data, form.price.data)
            products[i].quantity = form.quantity.data
            products[i].price = form.price.data

    return render_template('inventory.html',
                           inventory_products=products,
                           forms = forms)

@bp.route('/remove_from_inventory/<id>')
def remove_from_inventory(id):
    global products
    for i in range(len(products)):
        if (products[i].id == int(id)):
            products.pop(i)
            return(redirect(url_for('inventory.inventory')))
