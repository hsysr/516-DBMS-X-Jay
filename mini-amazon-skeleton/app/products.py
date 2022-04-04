from flask import render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from .models.product import Product
from .models.cart import Cart
from wtforms.validators import ValidationError, DataRequired, NumberRange
from flask_login import current_user

from flask import Blueprint
bp = Blueprint('products', __name__)


class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantity',
                            validators=[DataRequired(), NumberRange(min=1, max = 100, message='Quantity exceeds valid range')])
    submit = SubmitField('Add')

@bp.route('/productdetails/<int:pid>', methods=['GET', 'POST'])
def details(pid):# get all available products for sale:
    product = Product.get(pid)
    seller_info = Product.getSellerInfo(pid)
    return render_template('productdetails.html', avail_products = [product],seller_info = seller_info)


@bp.route('/cart', methods=['GET', 'POST'])
def cart():# get all available products for sale:
    # TODO: get products & quantities in user's cart
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    cart = Cart.get(current_user.id)
    return render_template('cart.html', cart = cart)
    
@bp.route('/addtocart/<sid>/<pid>', methods=['GET', 'POST'])
def addToCart(sid,pid):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    form = AddToCartForm()
    if form.validate_on_submit():
        if Product.addToCart(current_user.id, int(pid), int(sid), form.quantity.data):
            flash('~~Added to cart~~')
            return redirect(url_for('products.details',pid=pid))
    return render_template('addToCart.html',title='Add to cart',form=form)
    
@bp.route('/checkoutCart', methods=['GET', 'POST'])
def checkoutCart():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
        
    result = Cart.checkout(current_user.id)
    if result=='success':
        # TODO change flash message & add DB logic
        flash('~Purchase success~')
    else:
        flash(result)
    cart = Cart.get(current_user.id)
    return render_template('cart.html',cart=cart)
    


    
