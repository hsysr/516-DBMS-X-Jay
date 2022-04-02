from flask import render_template

from .models.product import Product

from flask import Blueprint
bp = Blueprint('products', __name__)


@bp.route('/productdetails/<int:pid>', methods=['GET', 'POST'])
def details(pid):# get all available products for sale:
    product = Product.get(pid)
    seller_info = Product.getSellerInfo(pid)
    return render_template('productdetails.html', avail_products = [product],seller_info = seller_info)



@bp.route('/cart', methods=['GET', 'POST'])
def cart():# get all available products for sale:
    # TODO: get products & quantities in user's cart
    return render_template('cart.html', cart = [])
    
@bp.route('/addtocart/<sid>/<pid>', methods=['GET', 'POST'])
def addToCart(sid,pid):
    #TODO: to implement an interface to add # quantities of product(pid) from the seller(sid) to cart
    return render_template('addToCart.html', sid=sid, pid=pid)