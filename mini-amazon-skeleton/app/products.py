from flask import render_template, redirect, url_for, flash
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField, StringField
from .models.product import Product
from .models.cart import Cart
from .models.purchase import OrderDetail
from wtforms.validators import ValidationError, DataRequired, NumberRange, Required
from flask_login import current_user

from flask import Blueprint
bp = Blueprint('products', __name__)

class EditQuantityForm(FlaskForm):
    quantity = IntegerField('Quantity')
    submit = SubmitField('Edit Quantity')

class EditProductDetailsForm(FlaskForm):
    description = StringField('Description')
    submit = SubmitField('Edit Details')

class AddToCartForm(FlaskForm):
    quantity = IntegerField('Quantity',
                            validators=[DataRequired(), NumberRange(min=1, max = 100, message='Quantity exceeds valid range')])
    submit = SubmitField('Add')

@bp.route('/productdetails/<int:pid>', methods=['GET', 'POST'])
def details(pid):
    product = Product.get(pid)
    products = Product.set_avgratings([product])
    seller_info = Product.getSellerInfo(pid)
    ratings_and_reviews = Product.get_product_ratings_and_reviews(pid)
    return render_template('productdetails.html', avail_products = products, seller_info = seller_info,
     ratings_and_reviews = ratings_and_reviews)

@bp.route('/editproductdetails/<int:pid>/<int:sid>', methods=['GET', 'POST'])
def editproductdetails(pid, sid):# get all available products for sale:
    updateform = EditProductDetailsForm()
    if updateform.validate_on_submit():
        Product.update_product_description(pid, sid, updateform.description.data)
        product = Product.get(pid)
        seller_info = Product.getSellerInfo(pid)
        return render_template('productdetails.html', avail_products = [product],seller_info = seller_info)
    return render_template('edit_productdetails.html', pid=pid, sid=sid, updateform=updateform)

@bp.route('/cart', methods=['GET', 'POST'])
def cart():
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
    
@bp.route('/editquantity/<sid>/<pid>', methods=['GET', 'POST'])
def editQuantity(sid,pid):
    quantityform = EditQuantityForm()
    if quantityform.validate_on_submit():
        if quantityform.quantity.data <= 0:
            Product.removeFromCart(current_user.id, int(pid), int(sid))  
        else:
            Product.update_quantity_in_cart(current_user.id, pid, sid, quantityform.quantity.data)
        cart = Cart.get(current_user.id)
        return render_template('cart.html', cart = cart)
    return render_template('edit_product_quantity.html', pid=pid, sid=sid, quantityform=quantityform)
    
@bp.route('/removefromcart/<sid>/<pid>', methods=['GET', 'POST'])
def removeFromCart(sid,pid):
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
    Product.removeFromCart(current_user.id, int(pid), int(sid))  
    cart = Cart.get(current_user.id)
    return render_template('cart.html', cart = cart)

@bp.route('/checkoutCart', methods=['GET', 'POST'])
def checkoutCart():
    if not current_user.is_authenticated:
        return redirect(url_for('users.login'))
        
    result = Cart.checkout(current_user.id)
    if result=='success':
        flash('~Purchase success~')
    else:
        flash(result)
    cart = Cart.get(current_user.id)
    return render_template('cart.html',cart=cart)
    
@bp.route('/orderdetail/<orderid>', methods=['GET', 'POST'])
def orderDetail(orderid):
    uid, orderDetail = OrderDetail.getOrderDetail(orderid)
    
    if current_user.id != uid:
        flash("Sorry, you don't have access to this order")
        return redirect(url_for('index.index'))
    return render_template('orderDetail.html',title='Order Detail', orderid=orderid, orderDetail=orderDetail)
    