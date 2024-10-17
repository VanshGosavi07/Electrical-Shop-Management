from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from fpdf import FPDF
from model import db, Employee, InventoryItem, Admin, Bill
import os
from functools import wraps

app = Flask(__name__)

# Configurations for the SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '17Vansh17'  # Replace with a strong secret key

db.init_app(app)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('You need to be logged in to view this page.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_type') != 'admin':
            flash('You need to be an admin to view this page.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/admin_dashboard')
@login_required
@admin_required
def admin_dashboard():
    return render_template('Admin/Admin_dashboard.html')


@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Check if the user is logged in by verifying session
    user_id = session.get('user_id')
    user_type = session.get('user_type')

    if not user_id or not user_type:
        flash('You need to be logged in to view your profile.', 'warning')
        return redirect(url_for('login'))

    # Retrieve the user based on the user type stored in session
    if user_type == 'admin':
        user = Admin.query.get(user_id)
    elif user_type == 'employee':
        user = Employee.query.get(user_id)
    else:
        flash('Invalid user type.', 'danger')
        return redirect(url_for('login'))

    # Make sure the user exists in the database
    if not user:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    # Handle form submission
    if request.method == 'POST':
        try:
            user.name = request.form['full_name']
            user.email = request.form['email']
            user.mobile_no = request.form['phone']
            user.address = request.form['address']

            # Save the updated user information in the database
            db.session.commit()
            flash('Profile updated successfully!', 'success')
        except Exception as e:
            flash(f'Error updating profile: {e}', 'danger')

        return redirect(url_for('profile'))

    # Render the profile template with the user information
    return render_template('profiles.html', user=user)


@app.route('/employee-management', methods=['GET', 'POST'])
@login_required
@admin_required
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
@login_required
@admin_required
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
@login_required
@admin_required
def statistics():
    return render_template("Admin/statistics.html")


@app.route('/generate_bill')
@login_required
def generate_bill():
    # Query to get all inventory items
    products = [item.name for item in InventoryItem.query.all()]
    # Pass the product names to the template
    return render_template('Employee/generate_bill.html', products=products)


@app.route('/check_product/<product_name>', methods=['GET'])
@login_required
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
@login_required
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
    employee_id = session['user_id']  # Use the current logged-in employee ID
    employee = Employee.query.get(employee_id)  # Fetch employee details

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
            employee_id=employee_id  # Use the current logged-in employee ID
        )
        db.session.add(new_bill)
        db.session.commit()

        # Generate PDF
        pdf = FPDF()
        pdf.add_page()

        # Set fonts
        pdf.set_font("Arial", size=12)

        # Title
        pdf.cell(200, 10, txt="Bill Receipt", ln=True, align='C')

        # Customer Information
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 10, "Customer Information", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Name: {customer_name}", ln=True)
        pdf.cell(0, 10, f"Mobile No: {customer_mobile}", ln=True)
        pdf.cell(0, 10, f"Address: {customer_address}", ln=True)

        # Employee Information
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 10, "Employee Information", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(0, 10, f"Employee Name: {employee.name}", ln=True)
        pdf.cell(0, 10, f"Employee ID: {employee.id}", ln=True)

        # Product Details in a Table Format
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 10, "Product Details", ln=True)
        pdf.set_font("Arial", size=12)

        pdf.cell(60, 10, "Product", border=1)
        pdf.cell(30, 10, "Quantity", border=1)
        pdf.cell(30, 10, "Price", border=1)
        pdf.cell(40, 10, "Total Payment", border=1)
        pdf.cell(0, 10, "", ln=True)  # Line break

        pdf.cell(60, 10, product_name, border=1)
        pdf.cell(30, 10, str(quantity), border=1)
        pdf.cell(30, 10, f"${price:.2f}", border=1)
        pdf.cell(40, 10, f"${total_payment:.2f}", border=1)
        pdf.cell(0, 10, "", ln=True)  # Line break

        # Payment Details
        pdf.set_font("Arial", style='B', size=12)
        pdf.cell(0, 10, txt="Payment Details:", ln=True)
        pdf.set_font("Arial", size=12)
        pdf.cell(40, 10, txt=f"Payment Type: {payment_type}", ln=True)

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get form data
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['userType']  # Added userType

        # Check if the user is an Admin
        if user_type == 'admin':
            user = Admin.query.filter_by(username=username).first()
        else:  # Assume employee
            user = Employee.query.filter_by(username=username).first()

        # Verify the user
        if user and check_password_hash(user.password, password):  # Use hash check
            session['user_id'] = user.id
            session['user_type'] = user_type  # Store user type in session
            flash('Login successful!', 'success')
            if user_type == 'admin':
                return redirect(url_for('admin_dashboard'))
            else:
                return redirect(url_for('generate_bill'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')

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


@app.route('/logout')
@login_required
def logout():
    # Clear the session
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Create the database tables here
    app.run(debug=True)
