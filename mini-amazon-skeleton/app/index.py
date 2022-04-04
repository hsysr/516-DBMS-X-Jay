from flask import render_template
from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
import datetime

from .models.product import Product
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('index', __name__)


class SearchForm(FlaskForm):
    namekeyword = StringField('Name Keyword')
    categorykeyword = StringField('Category Keyword')
    sortfield = RadioField('Sort by:', choices=[('Products.id ASC', 'Product ID (ASC)'),
                                                ('Products.id DESC', 'Product ID (DESC)'),
                                                ('Products.name ASC', 'Product Name (ASC)'),
                                                ('Products.name DESC', 'Product Name (DESC)'),
                                                ('Products.category ASC', 'Category (ASC)'),
                                                ('Products.category DESC', 'Category (DESC)'),
                                                ('minprice ASC', 'Minimum Price (ASC)'),
                                                ('minprice DESC', 'Minimum Price (DESC)')],
                                                default = 'Products.id ASC')
    submit = SubmitField('Search')


@bp.route('/', methods=['GET', 'POST'])
def index():
    # get all available products for sale:
    products = Product.get_all(available=True)
    searchform = SearchForm()
    # find the products current user has bought:
    if current_user.is_authenticated:
        purchases = Purchase.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
    else:
        purchases = None
    # render the page by adding information to the index.html file
    if searchform.validate_on_submit():
        products = Product.get_matching_keyword(namekeyword=searchform.namekeyword.data,
                                                categorykeyword=searchform.categorykeyword.data,
                                                ordering=searchform.sortfield.data,
                                                available=True)
        return render_template('index.html',
                           avail_products=products,
                           purchase_history=purchases, 
                           searchform=searchform)
    return render_template('index.html',
                           avail_products=products,
                           purchase_history=purchases, 
                           searchform=searchform)