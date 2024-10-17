from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Employee(db.Model):
    __tablename__ = 'employees'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile_no = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)  # Added
    password = db.Column(db.String(255), nullable=False)  # Added
    user_type = db.Column(db.String(10), default='employee')
    
    def __init__(self, name, mobile_no, email, username, password):
        self.name = name
        self.mobile_no = mobile_no
        self.email = email
        self.username = username
        self.password = password  # Hash this in production


class InventoryItem(db.Model):
    __tablename__ = 'inventory_items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)

    def __init__(self, name, quantity, price):
        self.name = name
        self.quantity = quantity
        self.price = price


class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    mobile_no = db.Column(db.String(15), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    # Make sure to hash passwords in production
    password = db.Column(db.String(255), nullable=False)
    user_type = db.Column(db.String(10), default='admin')

    def __init__(self, name, mobile_no, email, address, username, password):
        self.name = name
        self.mobile_no = mobile_no
        self.email = email
        self.address = address
        self.username = username
        self.password = password  # Hash this in production


class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_mobile = db.Column(db.String(15), nullable=False)
    customer_address = db.Column(db.String(255), nullable=False)
    product_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    total_payment = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(50), nullable=False)
    employee_name = db.Column(db.String(100), nullable=False)
    employee_id = db.Column(db.Integer, nullable=False)

    def __init__(self, customer_name, customer_mobile, customer_address, product_name,
                 quantity, price, total_payment, payment_type, employee_name, employee_id):
        self.customer_name = customer_name
        self.customer_mobile = customer_mobile
        self.customer_address = customer_address
        self.product_name = product_name
        self.quantity = quantity
        self.price = price
        self.total_payment = total_payment
        self.payment_type = payment_type
        self.employee_name = employee_name
        self.employee_id = employee_id
