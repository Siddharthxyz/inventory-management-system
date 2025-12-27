from flask import Flask
from models import db
from flask import Flask, render_template, request, redirect
from models import db, ChemicalProduct, Inventory
from flask import Flask, render_template, request, redirect
from models import db, ChemicalProduct, Inventory

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db.init_app(app)

from flask import redirect, url_for

@app.route('/')
def home():
    return render_template('index.html')


@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        name = request.form['name']
        cas = request.form['cas_number']
        unit = request.form['unit']

        # Create product
        product = ChemicalProduct(
            name=name,
            cas_number=cas,
            unit=unit
        )
        db.session.add(product)
        db.session.commit()

        # Create inventory entry
        inventory = Inventory(
            product_id=product.id,
            current_stock=0
        )
        db.session.add(inventory)
        db.session.commit()

        return redirect('/products')

    products = ChemicalProduct.query.all()
    return render_template('products.html', products=products)

@app.route('/inventory')
def inventory():
    inventory = Inventory.query.all()
    return render_template('inventory.html', inventory=inventory)

@app.route('/update-stock/<int:inventory_id>', methods=['POST'])
def update_stock(inventory_id):
    item = Inventory.query.get_or_404(inventory_id)
    quantity = float(request.form['quantity'])
    action = request.form['type']

    if quantity <= 0:
        return "Quantity must be positive"

    if action == 'IN':
        item.current_stock += quantity
    else:
        if item.current_stock < quantity:
            return "Stock cannot go below zero"
        item.current_stock -= quantity

    db.session.commit()
    return redirect('/inventory')

@app.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = ChemicalProduct.query.get_or_404(product_id)

    # Delete related inventory first (important!)
    inventory = Inventory.query.filter_by(product_id=product.id).first()
    if inventory:
        db.session.delete(inventory)

    db.session.delete(product)
    db.session.commit()

    return redirect('/products')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()   # creates tables
    app.run(debug=True)
