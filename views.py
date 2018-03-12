from sqlite3 import IntegrityError

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from main import app, login_manager, db
from forms import LoginForm, SignupForm
from models import User, Products, Customers, Invoices, Basket
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash

baseTemplate = 'index.html'
loginTemplate = 'login.html'
signupTemplate = 'signup.html'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/navitem1', methods=['GET'])
@login_required
def navitem1():
    return None

@app.route('/navitem2', methods=['GET'])
def navitem2():
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return render_template(baseTemplate, loggingMessage='Logged in successfully as '+current_user.username)

        return render_template(loginTemplate, form=form, error=True)

    return render_template(loginTemplate, form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignupForm()
    if form.validate_on_submit():
        try:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return render_template(signupTemplate, form=form, success=True)
        except IntegrityError as e:
            return render_template(signupTemplate, form=form, error=e)

    return render_template(signupTemplate, form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template(baseTemplate, loggingMessage='Logged out successfully')

#Making invoice
#Choosing customer

@app.route('/invoicing', methods=['GET','POST'])
#@login_required
def customer_select():
    products = Products.query.all()
    customers = Customers.query.all()

    if request.method == 'POST':
        #Choose customer form:
        if request.form.get('customer_id') or request.form.get('customer_name') or request.form.get('customer_id_list'):
            if request.form.get('customer_id'):
                id = int(request.form.get('customer_id'))
                return redirect(url_for('products_select', id=id))
            elif request.method == 'POST' and request.form.get('customer_name'):
                name = request.form.get('customer_name')
                selected_customer = Customers.query.filter_by(name=name).first()
                id = int(selected_customer.id)
                return redirect(url_for('products_select', id=id))
            elif request.method == 'POST' and request.form.get('customer_id_list'):
                id = int(request.form.get('customer_id_list'))
                return redirect(url_for('products_select', id=id))
            else:
                flash('No such customer in db, try again', 'error')
                return render_template('invoicing.html', customers=customers)
    return render_template('invoicing.html',customers=customers)

@app.route('/invoicing/customer/<int:id>', methods=['GET','POST'])
#@login_required
def products_select(id):
    products = Products.query.all()
    selected_customer = Customers.query.get_or_404(id)
    if request.method == 'POST':

    # Choose product form:
        if request.form.get('product_id') or request.form.get('product_name') or request.form.get(
                'product_id_list'):
            if request.form.get('product_id'):
                product_id = int(request.form.get('product_id'))
                selected_product = Products.query.get_or_404(product_id)
            elif request.form.get('product_id_list'):
                product_id = int(request.form.get('product_id_list'))
                selected_product = Products.query.get_or_404(product_id)
            elif request.form.get('product_name'):
                product_name = request.form.get('product_name')
                selected_product = Products.query.fliter_by(name=product_name).first()
            to_basket = Basket(product_id=selected_product.id, product_name=selected_product.name,
                               product_price=selected_product.price, product_group=selected_product.group)
            db.session.add(to_basket)
            db.session.commit()
            basket = Basket.query.all()
            return render_template('invoicing.html', products=products, selected_customer=selected_customer, basket=basket)

        #Clean basket
        elif request.form.get('clean'):
            basket = Basket.query.all()
            for product in basket:
                db.session.delete(product)
            db.session.commit()
            return render_template('invoicing.html', products=products, selected_customer=selected_customer)

    return render_template('invoicing.html', products=products, selected_customer=selected_customer)