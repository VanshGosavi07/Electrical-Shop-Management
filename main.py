from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    return render_template('Admin/Admin_dashboard.html')


@app.route('/profile')
def profile():
    return render_template('profiles.html')


@app.route('/customer-management')
def customer_management():
    return "Customer Management Page"


@app.route('/employee-management')
def employee_management():
    return render_template('Admin/employee_management.html')


@app.route('/inventory-management')
def inventory_management():
    return render_template('Admin/inventory_management.html')


@app.route('/statistics')
def statistics():
    return render_template("Admin/statistics.html")


@app.route('/generate_bill')
def generate_bill():
    return render_template('Employee/generate_bill.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('Admin/register.html')

if __name__ == '__main__':
    app.run(debug=True)
