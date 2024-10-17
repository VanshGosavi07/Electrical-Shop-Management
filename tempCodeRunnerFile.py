@app.route('/generate_bill')
def generate_bill():
    # Query to get all inventory items
    products = [item.name for item in InventoryItem.query.all()]
    # Print the list of product names
    print(products)
    return render_template('generate_bill.html')