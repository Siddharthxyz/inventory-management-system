from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from datetime import datetime

from models import db, ChemicalProduct, Inventory, StockMovement

app = Flask(__name__)

# ---------------- CONFIG ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- PRODUCTS ----------------
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        name = request.form['name']
        cas = request.form['cas_number']
        unit = request.form['unit']
        initial_quantity = float(request.form['initial_quantity'])

        # VALIDATION
        if initial_quantity <= 0:
            return "Initial stock must be greater than zero", 400

        # CREATE PRODUCT
        product = ChemicalProduct(
            name=name,
            cas_number=cas,
            unit=unit
        )
        db.session.add(product)
        db.session.commit()

        # CREATE INVENTORY
        inventory = Inventory(
            product_id=product.id,
            current_stock=initial_quantity
        )
        db.session.add(inventory)

        # LOG INITIAL STOCK (IN)
        movement = StockMovement(
            product_id=product.id,
            movement_type='IN',
            quantity=initial_quantity
        )
        db.session.add(movement)

        db.session.commit()
        return redirect(url_for('products'))

    # SEARCH
    search = request.args.get('search')
    if search:
        products = ChemicalProduct.query.filter(
            or_(
                ChemicalProduct.name.ilike(f"%{search}%"),
                ChemicalProduct.cas_number.ilike(f"%{search}%")
            )
        ).all()
    else:
        products = ChemicalProduct.query.all()

    return render_template('products.html', products=products)


# ---------------- INVENTORY ----------------
@app.route('/inventory')
def inventory():
    inventory = Inventory.query.all()
    return render_template('inventory.html', inventory=inventory)


# ---------------- UPDATE STOCK ----------------
@app.route('/update-stock/<int:inventory_id>', methods=['POST'])
def update_stock(inventory_id):
    item = Inventory.query.get_or_404(inventory_id)
    quantity = float(request.form['quantity'])
    action = request.form['type']

    if quantity <= 0:
        return "Quantity must be greater than zero", 400

    if action == 'IN':
        item.current_stock += quantity
    else:
        if item.current_stock - quantity < 0:
            return "Stock cannot go below zero", 400
        item.current_stock -= quantity

    # LOG STOCK MOVEMENT
    movement = StockMovement(
        product_id=item.product_id,
        movement_type=action,
        quantity=quantity
    )
    db.session.add(movement)

    db.session.commit()
    return redirect(url_for('inventory'))


# ---------------- STOCK HISTORY ----------------
@app.route('/stock-history')
def stock_history():
    history = StockMovement.query.order_by(
        StockMovement.timestamp.desc()
    ).all()
    return render_template('stock_history.html', history=history)


# ---------------- DELETE PRODUCT ----------------
@app.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = ChemicalProduct.query.get_or_404(product_id)

    inventory = Inventory.query.filter_by(product_id=product.id).first()
    if inventory:
        db.session.delete(inventory)

    StockMovement.query.filter_by(product_id=product.id).delete()

    db.session.delete(product)
    db.session.commit()

    return redirect(url_for('products'))


# ---------------- INIT DB ----------------
with app.app_context():
    db.create_all()


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True)
