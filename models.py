__author__ = 'Jacek Kalbarczyk'

#from flask_login import UserMixin

#from sqlalchemy import Column
#from sqlalchemy.types import Integer
#from sqlalchemy.types import String
#from sqlalchemy.types import Boolean

from main import db
from datetime import datetime

class User(db.Model):
    """
    User model for reviewers.
    """
    __tablename__ = 'users'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    active = db.Column(db.Boolean, default=True)
    username = db.Column(db.String(200), unique=True)
    email = db.Column(db.String(200), default='')
    password = db.Column(db.String(200), default='')
    admin = db.Column(db.Boolean, default=False)

    def is_active(self):
        """
        Returns if user is active.
        """
        return self.active

    def is_admin(self):
        """
        Returns if user is admin.
        """
        return self.admin

    def is_authenticated(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

class Products(db.Model):
    __tablename__ = 'products'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    group = db.Column(db.String(30), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    price = db.Column(db.Integer, default=0)

    def __repr__(self):
        return "Products(id={}, name='{}', group='{}', quantity='{}', price='{}'".format(self.id, self.name, self.group, self.quantity, self.price)

class Customers(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    nip = db.Column(db.String(30), nullable=False)
    adress = db.Column(db.String(80), nullable=False)
    payment = db.Column(db.Integer, default=0)

class Basket(db.Model):
    __tablename__ = 'basket'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, nullable=False)
    product_name = db.Column(db.String(80), nullable=False)
    product_price = db.Column(db.Integer, default=0)
    product_group = db.Column(db.String(30), nullable=False)
    product_quantity = db.Column(db.Integer, default=0)

class Invoices(db.Model):
    __tablename__ = 'invoices'
    id = db.Column(db.Integer, primary_key=True)
    net_price = db.Column(db.Integer, nullable=False)
    customer = db.Column(db.String(30), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


