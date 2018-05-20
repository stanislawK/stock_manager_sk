from sqlite3 import IntegrityError

from flask import render_template, redirect, url_for, request, flash
from flask_login import login_user, login_required, logout_user, current_user
from main import app, login_manager, db
from forms import LoginForm, SignupForm
from models import User, Products, Customers, Invoices, Basket, Quantities
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash, check_password_hash
import datetime

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
                existing = Basket.query.filter_by(product_id=selected_product.products_id).first()
                if existing:
                    basket = Basket.query.all()
                else:
                    to_basket = Basket(product_id=selected_product.products_id, product_name=selected_product.name,
                                       product_price=selected_product.price, product_group=selected_product.group,
                                       stock_quantity=selected_product.stock_quantity)
                    db.session.add(to_basket)
                    db.session.commit()
                    basket = Basket.query.all()
                return render_template('invoicing.html', products=products, selected_customer=selected_customer,
                                           basket=basket)

            elif request.form.get('product_id_list'):
                product_id = int(request.form.get('product_id_list'))
                selected_product = Products.query.get_or_404(product_id)
                existing = Basket.query.filter_by(product_id=selected_product.products_id).first()
                if existing:
                    basket = Basket.query.all()
                else:
                    to_basket = Basket(product_id=selected_product.products_id, product_name=selected_product.name,
                                       product_price=selected_product.price, product_group=selected_product.group,
                                       stock_quantity=selected_product.stock_quantity)
                    db.session.add(to_basket)
                    db.session.commit()
                    basket = Basket.query.all()
                return render_template('invoicing.html', products=products, selected_customer=selected_customer,
                                       basket=basket)


            basket = Basket.query.all()
            return render_template('invoicing.html', products=products, selected_customer=selected_customer,
                                   basket=basket)


        #Choosing product quantity
        elif request.form.get('product_qty'):
            selected_qty = request.form.get('product_qty').split(' ')
            product_id = int(selected_qty[0])
            product_qty = int(selected_qty[1])
            current_product = Basket.query.filter_by(product_id=product_id).first()
            current_product.product_quantity = product_qty
            current_product.product_amount = current_product.product_price * current_product.product_quantity
            db.session.commit()
            basket = Basket.query.all()
            return render_template('invoicing.html', products=products, selected_customer=selected_customer,
                                   basket=basket)
            #return render_template('test.html', selected_qty=selected_qty, product_id=product_id, product_qty=product_qty, current_product=current_product)

        #Clean basket
        elif request.form.get('clean'):
            basket = Basket.query.all()
            for product in basket:
                db.session.delete(product)
            db.session.commit()
            return render_template('invoicing.html', products=products, selected_customer=selected_customer)

        #Make invoice
        elif request.form.get('make_invoice'):
            basket = Basket.query.all()
            new_invoice = Invoices(customer=selected_customer)
            net_sum = 0
            for item in basket:
                product_qty = item.product_quantity
                total_price = item.product_amount
                new_product = Products.query.get_or_404(item.product_id)
                new_invoice.invoicing.append(new_product)
                net_sum += round(float(total_price),2)
                new_quantity = Quantities(invoice=new_invoice, product=new_product, order_quantity=product_qty, total_price=total_price)
                db.session.add(new_quantity)
                db.session.delete(item)
            new_invoice.net = net_sum
            new_invoice.tax = round(float(new_invoice.net * 0.23),2)
            new_invoice.sum = round(float(new_invoice.net + new_invoice.tax),2)
            db.session.add(new_invoice)
            db.session.commit()
            new_invoice = Invoices.query.order_by("-invoices_id").first()
            payment_day = new_invoice.date + datetime.timedelta(days=selected_customer.payment)
            # quantites = Quantities.query.filter(invoice_id=new_invoice.invoices_id).all()
            #return render_template('test.html', new_invoice=new_invoice)
            return render_template('invoicing.html', products=products, selected_customer=selected_customer, new_invoice=new_invoice, payment_day=payment_day)


    return render_template('invoicing.html', products=products, selected_customer=selected_customer)

# @app.route('/invoicing/customer/<int:id>', methods=['GET','POST'])
# #@login_required
# def products_select(id):
#     products = Products.query.all()
#     selected_customer = Customers.query.get_or_404(id)
#     selected_product = 0
#     if not selected_product==0:
#         invoice_candidate = Invoices(customer=selected_customer)
#         db.session.add(invoice_candidate)
#         db.session.commit()
#     basket = Invoices.query.order_by('-invoices_id').first()
#     if request.method == 'POST':
#
#     # Choose product form:
#         if request.form.get('product_id') or request.form.get('product_name') or request.form.get(
#                 'product_id_list'):
#             if request.form.get('product_id'):
#                 product_id = int(request.form.get('product_id'))
#                 selected_product = Products.query.get_or_404(product_id)
#             elif request.form.get('product_id_list'):
#                 product_id = int(request.form.get('product_id_list'))
#                 selected_product = Products.query.get_or_404(product_id)
#             elif request.form.get('product_name'):
#                 product_name = request.form.get('product_name')
#                 selected_product = Products.query.fliter_by(name=product_name).first()
#
#             #add selceted product do db
#             basket.invoicing.append(selected_product)
#             db.session.commit()
#
#             return render_template('invoicing.html', products=products, selected_customer=selected_customer, basket=basket)
#
#         #Clean basket
#         elif request.form.get('clean'):
#             db.session.delete(basket)
#             db.session.commit()
#             return render_template('invoicing.html', products=products, selected_customer=selected_customer)
#
#     return render_template('invoicing.html', products=products, selected_customer=selected_customer)

@app.route('/test', methods=['GET','POST'])
def test():
    invoices = Invoices.query.all()
    return render_template('test.html', invoices=invoices)
