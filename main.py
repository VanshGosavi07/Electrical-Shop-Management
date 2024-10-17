from flask import make_response, request, Flask
from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify
from model import db, Employee, InventoryItem, Admin, Bill
from werkzeug.security import generate_password_hash
from fpdf import FPDF
import os

app = Flask(__name__)

# Configurations for the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('Admin/Admin_dashboard.html')


@app.route('/profile')
def profile():
    return render_template('profiles.html')


@app.route('/employee-management', methods=['GET', 'POST'])
def employee_management():
    if request.method == 'POST':
        # Get form data
        name = request.form['employeeName']
        mobile_no = request.form['mobileNo']
        email = request.form['email']
        username = request.form['username']  # New field for username
        password = request.form['password']  # New field for password

        # Create a new employee record
        new_employee = Employee(
            name=name,
            mobile_no=mobile_no,
            email=email,
            username=username,
            password=generate_password_hash(password)  # Hash the password
        )
        db.session.add(new_employee)
        db.session.commit()

        return redirect(url_for('employee_management'))

    # Get all employees from the database
    employees = Employee.query.all()
    return render_template('Admin/employee_management.html', employees=employees)


@app.route('/inventory-management', methods=['GET', 'POST'])
def inventory_management():
    if request.method == 'POST':
        name = request.form['itemName']
        quantity = request.form['itemQuantity']
        price = request.form['itemPrice']
        item_id = request.form.get('itemId')  # Get the item ID if it's an edit

        if item_id:  # If an item ID is provided, update the item
            item = InventoryItem.query.get(item_id)
            item.name = name
            item.quantity = quantity
            item.price = price
        else:  # Otherwise, create a new item
            item = InventoryItem(name=name, quantity=quantity, price=price)
            db.session.add(item)

        db.session.commit()
        return redirect(url_for('inventory_management'))

    # Fetch all inventory items to display in the table
    items = InventoryItem.query.all()
    return render_template('Admin/inventory_management.html', items=items)


@app.route('/statistics')
def statistics():
    return render_template("Admin/statistics.html")


@app.route('/generate_bill')
def generate_bill():
    # Query to get all inventory items
    products = [item.name for item in InventoryItem.query.all()]
    # Pass the product names to the template
    return render_template('Employee/generate_bill.html', products=products)


@app.route('/check_product/<product_name>', methods=['GET'])
def check_product(product_name):
    # Query the database to find the product
    product = InventoryItem.query.filter_by(name=product_name).first()

    if product:
        return jsonify({
            'available': 'yes',
            'quantity': product.quantity,
            'price': product.price
        })
    else:
        return jsonify({'available': 'no'})


@app.route('/submit_bill', methods=['POST'])
def submit_bill():
    data = request.get_json()

    # Extract data from the JSON
    customer_name = data['customerName']
    customer_mobile = data['customerMobile']
    customer_address = data['customerAddress']
    product_name = data['productName']
    quantity = int(data['productQuantity'])
    price = float(data['productPrice'])
    total_payment = float(data['totalPayment'])
    payment_type = data['paymentType']

    # Find the product in the inventory
    product = InventoryItem.query.filter_by(name=product_name).first()
    if product and product.quantity >= quantity:
        # Update product quantity
        product.quantity -= quantity
        db.session.commit()

        # Create a new bill record
        new_bill = Bill(
            customer_name=customer_name,
            customer_mobile=customer_mobile,
            customer_address=customer_address,
            product_name=product_name,
            quantity=quantity,
            price=price,
            total_payment=total_payment,
            payment_type=payment_type,
            employee_name='Employee Name',  # Replace with actual employee name
            employee_id=1  # Replace with actual employee ID
        )
        db.session.add(new_bill)
        db.session.commit()

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()

        # Set fonts
        pdf.set_font("Arial", size=12)

        # Add content to the PDF
        pdf.cell(200, 10, txt="Bill Receipt", ln=True, align='C')

        pdf.cell(200, 10, txt=f"Customer Name: {customer_name}", ln=True)
        pdf.cell(200, 10, txt=f"Mobile No: {customer_mobile}", ln=True)
        pdf.cell(200, 10, txt=f"Address: {customer_address}", ln=True)

        pdf.cell(200, 10, txt="Product Details:", ln=True)
        pdf.cell(200, 10, txt=f"Product: {product_name}", ln=True)
        pdf.cell(200, 10, txt=f"Quantity: {quantity}", ln=True)
        pdf.cell(200, 10, txt=f"Price per unit: ${price}", ln=True)
        pdf.cell(200, 10, txt=f"Total Payment: ${total_payment}", ln=True)
        pdf.cell(200, 10, txt=f"Payment Type: {payment_type}", ln=True)

        # Create the PDF in memory
        pdf_output = pdf.output(dest='S').encode('latin1')

        # Return PDF as downloadable file
        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=bill_receipt_{
            customer_name}.pdf'
        return response

    else:
        return jsonify({'status': 'error', 'message': 'Insufficient stock or product not found.'}), 400


@app.route('/login')
def login():
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Get form data
        name = request.form['name']
        mobile_no = request.form['mobile']
        email = request.form['email']
        address = request.form['address']
        username = request.form['username']
        password = request.form['password']

        # Create a new admin record
        new_admin = Admin(name=name, mobile_no=mobile_no, email=email,
                          address=address, username=username,
                          password=generate_password_hash(password))
        db.session.add(new_admin)
        db.session.commit()

        # Redirect to login or admin dashboard
        return redirect(url_for('login'))

    return render_template('Admin/register.html')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables here
    app.run(debug=True)
