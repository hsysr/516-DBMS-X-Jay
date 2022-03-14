from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user
from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DecimalField, FormField, FieldList
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, InputRequired
from werkzeug.datastructures import MultiDict

from .models.product import Product
from .models.inventory import Inventory

from flask import Blueprint
bp = Blueprint('inventory', __name__)

class InventoryForm(FlaskForm):
    quantity = IntegerField('Quantity',
                            validators=[NumberRange(min=0, message='Quantity cannot be negative')], default = 1)
    price = DecimalField('Price',
                         validators=[DataRequired(message='Quantity must be an number'), NumberRange(min=0, message='Price cannot be negative')], default = 1)

class InventoryListForm(FlaskForm):
	forms = FieldList(FormField(InventoryForm))

@bp.route('/inventory', methods = ['GET', 'POST'])
def inventory():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    inventories = Inventory.get_all_by_sid(current_user.id)

    form = InventoryListForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            for i, iform in enumerate(form.forms):
                if (inventories[i].quantity != iform.quantity.data):
                    Inventory.change_quantity(inventories[i].pid, current_user.id, iform.quantity.data)
                if (inventories[i].price != iform.price.data):
                    Inventory.change_price(inventories[i].pid, current_user.id, iform.price.data)
    else:
        for invent in inventories:
            form.forms.append_entry()
            form.forms[-1].quantity.data = invent.quantity
            form.forms[-1].price.data = invent.price

    names = [Product.get(invent.pid).name for invent in inventories]

    return render_template('inventory.html',
                           inventory_products=inventories,
                           form = form,
                           names = names)

@bp.route('/remove_from_inventory/<id>')
def remove_from_inventory(id):
    global products
    for i in range(len(products)):
        if (products[i].id == int(id)):
            products.pop(i)
            return(redirect(url_for('inventory.inventory')))
