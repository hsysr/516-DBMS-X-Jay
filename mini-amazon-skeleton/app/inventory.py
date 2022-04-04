from flask import Flask, render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import current_user
from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, DecimalField, FormField, FieldList, TextAreaField, SelectMultipleField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, NumberRange, InputRequired, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.datastructures import MultiDict

from .models.product import Product
from .models.inventory import Inventory

import os

from flask import Blueprint
bp = Blueprint('inventory', __name__)
app = Flask(__name__)


class InventoryForm(FlaskForm):
    quantity = IntegerField('Quantity',
                            validators=[NumberRange(min=0, max = 2147483647, message='Quantity exceeds valid range')])
    price = DecimalField('Price',
                         validators=[DataRequired(message='Price must be an number'), NumberRange(min=0, max = 2147483647, message='Price exceeds valid range')])
    descrip = TextAreaField('Description',
                            validators=[DataRequired(), Length(max=250, message="Only 250 characters allowed")],
                            render_kw={"rows": 6, "cols": 50})


class InventoryListForm(FlaskForm):
    forms = FieldList(FormField(InventoryForm))

@bp.route('/inventory', methods = ['GET'])
def inventory():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    inventories = Inventory.get_all_by_sid(current_user.id)

    names = [Product.get(invent.pid).name for invent in inventories]

    return render_template('inventory.html',
                           inventory_products=inventories,
                           names = names)
    

@bp.route('/change_inventory', methods = ['GET', 'POST'])
def change_inventory():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    inventories = Inventory.get_all_by_sid(current_user.id)

    form = InventoryListForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            for i, iform in enumerate(form.forms):
                if inventories[i].quantity != iform.quantity.data or \
                   inventories[i].price != iform.price.data or \
                   inventories[i].description != iform.descrip.data:
                    Inventory.change_inventory(inventories[i].pid,
                                               current_user.id,
                                               iform.quantity.data,
                                               iform.price.data,
                                               iform.descrip.data)
            return redirect(url_for('inventory.inventory'))
    else:
        for invent in inventories:
            form.forms.append_entry()
            form.forms[-1].quantity.data = invent.quantity
            form.forms[-1].price.data = invent.price
            form.forms[-1].descrip.data = invent.description

    names = [Product.get(invent.pid).name for invent in inventories]

    return render_template('change_inventory.html',
                           inventory_products=inventories,
                           form = form,
                           names = names)


@bp.route('/remove_from_inventory/<pid>')
def remove_from_inventory(pid):
    Inventory.remove_inventory(pid, current_user.id)
    return(redirect(url_for('inventory.inventory')))

class AddInventoryForm(FlaskForm):
    name = StringField('Product Name', validators=[DataRequired(), Length(max=50, message="Only 50 characters allowed")])

    image = FileField('Upload Product Image', validators=[FileRequired(), FileAllowed(['jpg','png'], 'Please upload an image(.jpg, .png) file')])

    quantity = IntegerField('Quantity',
                            validators=[NumberRange(min=0, max =2147483647, message='Quantity exceeds valid range')])
    price = DecimalField('Price',
                         validators=[DataRequired(message='Quantity must be an number'), NumberRange(min=0, max =2147483647, message='Price exceeds valid range')])
    descrip = TextAreaField('Description',
                            validators=[DataRequired(), Length(max=250, message="Only 250 characters allowed")],
                            render_kw={"rows": 6, "cols": 50})
    category = SelectMultipleField('Category', choices=[('art','art'),('bathroom','bathroom'),('drink','drink'),('electronics','electronics'),('food','food'),('kitchen&houseware','kitchen&houseware'),('outdoors','outdoors')],validators=[DataRequired()])


@bp.route('/add_to_inventory', methods = ['GET', 'POST'])
def add_to_inventory():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    form = AddInventoryForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            new_product = Product.add_product(form.name.data, form.category.data[0])
            result = Inventory.add_inventory(new_product.id, current_user.id, form.quantity.data, form.price.data, form.descrip.data)
            if result is None:
                flash('This product already in your inventory')
                return(redirect(url_for('inventory.inventory')))
            form.image.data.save(os.path.join(app.root_path, 'static', 'images', str(new_product.id) + '.png'))
            return(redirect(url_for('inventory.inventory')))
    return render_template('add_inventory.html',
                           form = form)



@bp.route('/add_product_to_inventory/<pid>', methods = ['GET', 'POST'])
def add_product_to_inventory(pid):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    current_product = Product.get(pid)
    form = InventoryForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            result = Inventory.add_inventory(pid, current_user.id, form.quantity.data, form.price.data, form.descrip.data)
            if result is None:
                flash('This product already in your inventory')
            else:
                flash('Successfully added product to your inventory')
            return(redirect(url_for('products.details', pid = pid)))
    return render_template('add_product_to_inventory.html',
                           current_product = current_product,
                           form = form)