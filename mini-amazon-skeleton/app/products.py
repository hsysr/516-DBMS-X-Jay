from flask import render_template

from .models.product import Product

from flask import Blueprint
bp = Blueprint('products', __name__)


@bp.route('/productdetails/<int:pid>', methods=['GET', 'POST'])
def details(pid):# get all available products for sale:
    product = Product.get(pid)
    return render_template('productdetails.html', avail_products = [product])