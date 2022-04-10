from flask import render_template, redirect, url_for, flash, request
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms.fields.html5 import DateField
from wtforms import StringField, IntegerField,PasswordField, BooleanField, SubmitField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo,NumberRange

from .models.user import User, SellerFeedback
from .models.purchase import Purchase, PurchaseSum
from .models.purchase import FilteredItem
from werkzeug.datastructures import MultiDict
import datetime

from flask import Blueprint
bp = Blueprint('users', __name__)


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.get_by_auth(form.email.data, form.password.data)
        if user is None:
            flash('Invalid email or password')
            return redirect(url_for('users.login'))
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index.index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


class RegistrationForm(FlaskForm):
    firstname = StringField('First Name', validators=[DataRequired()])
    lastname = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    password2 = PasswordField(
        'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
    address = StringField('Address', validators=[DataRequired()])
    balance = IntegerField('Balance', validators=[NumberRange(min=0, max=10000)])
    submit = SubmitField('Register')

    def validate_email(self, email):
        if User.email_exists(email.data):
            raise ValidationError('Already a user with this email～')

def buildEditProfileForm(id,Pemail,Pfirstname,Plastname,Paddress):
    class EditProfileForm(FlaskForm):
        firstname = StringField('First Name',default=Pfirstname, validators=[DataRequired()])
        lastname = StringField('Last Name', default=Plastname,validators=[DataRequired()])
        email = StringField('Email', default=Pemail,validators=[DataRequired(), Email()])
        password = PasswordField('Password', validators=[DataRequired()])
        password2 = PasswordField(
            'Repeat Password', validators=[DataRequired(),
                                       EqualTo('password')])
        address = StringField('Address',default=Paddress, validators=[DataRequired()])
        submit = SubmitField('Update')

        def validate_email(self, email):
            if User.email_exists_for_edit_profile(id, email.data):
                raise ValidationError('Already a user with this email.')
    return EditProfileForm()

class BalanceTopupForm(FlaskForm):
    topup = IntegerField('Topup(0-10000)', default=10,validators=[NumberRange(min=0, max=10000)])
    submit = SubmitField('Process')

def buildBalanceWithdrawForm(balance):
    class balanceWithdrawForm(FlaskForm):
        fieldStr = 'Withdraw(0-'+str(balance)+')'
        withdraw = IntegerField(fieldStr, default=0,validators=[NumberRange(min=0, max=balance)])
        submit = SubmitField('Process')
    return balanceWithdrawForm()
        
        
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.register(form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data, form.address.data,form.balance.data):
            flash('Congratulations, you are now a registered user!')
            return redirect(url_for('users.login'))
    return render_template('register.html', title='Register', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index.index'))
    
# for searching purchase history
class SearchForm(FlaskForm):
    productNameKeyword = StringField('Product Name Keyword:')
    sellerLastNameKeyword = StringField('Seller Last Name Keyword: ')
    sellerFirstNameKeyword = StringField('Seller First Name Keyword: ')
    date = DateField('Time purchased', validators=[DataRequired()] )
    submit = SubmitField('Search')

@bp.route('/profile', methods=['GET', 'POST'])
def profile():
    info = User.get(current_user.id)
    if info is None:
        return redirect(url_for('users.login'))
        
    purchases = PurchaseSum.get_all_by_uid_since(
            current_user.id, datetime.datetime(1980, 9, 14, 0, 0, 0))
            
    searchForm = SearchForm()

    if searchForm.validate_on_submit():
        newfiltered = FilteredItem.getFilteredItem(searchForm.productNameKeyword.data, searchForm.sellerLastNameKeyword.data, searchForm.sellerFirstNameKeyword.data, searchForm.date.data, current_user.id)
        return render_template('profile.html',title='profile_title',userinfo=info, purchase_history=purchases, searchform=searchForm, filteredItems=newfiltered)
    return render_template('profile.html',title='profile_title',userinfo=info, purchase_history=purchases, searchform=searchForm, filteredItems=[])
    
        
@bp.route('/editprofile', methods=['GET', 'POST'])
def editProfile():
    info = User.get(current_user.id)
    if info is None:
        return redirect(url_for('users.login'))
    form = buildEditProfileForm(info.id,info.email, info.firstname, info.lastname, info.address)
    if form.validate_on_submit():
        if User.editProfile(current_user.id, form.email.data,
                         form.password.data,
                         form.firstname.data,
                         form.lastname.data, form.address.data):
            flash('Edit success!')
            return redirect(url_for('users.profile'))
    
    return render_template('editProfile.html',title='edit profile_title',userinfo=info,form=form)
 
@bp.route('/profileFeedback',methods = ['GET', 'POST'])
def profileFeedback():
    info = User.get(current_user.id)
    if info is None:
        return redirect(url_for('users.login'))

    feedbackReceived = SellerFeedback.getFeedback(current_user.id)
    return render_template('profileFeedback.html', feedbackReceived=feedbackReceived)

@bp.route('/balancetopup', methods=['GET','POST'])
def balanceTopup():
    info = User.get(current_user.id)
    if info is None:
        return redirect(url_for('users.login'))
    form = BalanceTopupForm()
    if form.validate_on_submit():
        if User.balanceTopup(info.id, info.balance, form.topup.data):
            flash('Topup succeed!')
            return redirect(url_for('users.profile'))
    return render_template('balanceTopup.html',title='balance topup',form=form)
    
@bp.route('/balancewithdraw', methods=['GET','POST'])
def balanceWithdraw():
    info = User.get(current_user.id)
    if info is None:
        return redirect(url_for('users.login'))
    form = buildBalanceWithdrawForm(info.balance)
    if form.validate_on_submit():
        if User.balanceWithdraw(info.id, info.balance, form.withdraw.data):
            flash('Withdraw succeed!')
            return redirect(url_for('users.profile'))
    return render_template('balanceWithdraw.html',title='balance withdraw',form=form)
        

@bp.route('/<variable>/publicProfile', methods=['GET','POST'])
def publicProfile(variable):
    isSeller, info = User.getPublicView(variable)
    feedbacks = SellerFeedback.getFeedback(info.id)
    if info is None:
        flash('The user does not exist!')
        return
    return render_template('publicProfile.html',title='publicProfile',isSeller=isSeller, info=info, feedbacks=feedbacks)
