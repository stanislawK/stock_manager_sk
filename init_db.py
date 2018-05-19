__author__ = 'Jacek Kalbarczyk'

from sqlalchemy import create_engine
from main import db
from models import User, Products, Customers, Invoices
from werkzeug.security import generate_password_hash

def db_start():
    create_engine('sqlite:///test.db', convert_unicode=True)
    db.create_all()
    db.session.commit()

    user = User()
    user.username = "admin"
    user.password = generate_password_hash('admin', method='sha256')
    user.email = 'admin@gmail.com'
    user.admin = True
    user.poweruser = True
    db.session.add(user)
    db.session.commit()

    #dodanie przykładowych produktów i klientów
    product1 = Products(
        name='Car tire A',
        group='Tires',
        stock_quantity=1,
        price=50
    )
    product2 = Products(
        name='Car tire B',
        group='Tires',
        stock_quantity=3,
        price=60
    )
    product3 = Products(
        name='Car piston A',
        group='Pistons',
        stock_quantity=1,
        price=150
    )
    customer1 = Customers(
        name='Kowalex',
        nip='111-333-222',
        adress='66-500 Poznan, ul.Niczyja 1',
        payment=30
    )
    customer2 = Customers(
        name='Nowatex',
        nip='111-444-555',
        adress='66-500 Poznan, ul.Niczyja 2',
        payment=21
    )

    db.session.add(product1)
    db.session.add(product2)
    db.session.add(product3)
    db.session.add(customer1)
    db.session.add(customer2)
    db.session.commit()
    invoice1 = Invoices(
        customer=customer1
    )
    invoice2 = Invoices(
        customer=customer2
    )
    db.session.add(invoice1)
    db.session.add(invoice2)
    db.session.commit()
    invoice1.invoicing.append(product1)
    invoice1.invoicing.append(product2)
    invoice1.invoicing.append(product3)
    db.session.commit()

if __name__ == '__main__':
    db_start()
