from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

from models import db, ChemicalProduct, Inventory ,StockMovement

app = Flask(__name__)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize DB
db.init_app(app)


# ---------------- HOME PAGE ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- PRODUCTS (CREATE, READ, SEARCH) ----------------
@app.route('/products', methods=['GET', 'POST'])
def products():
    # ADD PRODUCT
    if request.method == 'POST':
        name = request.form['name']
        cas = request.form['cas_number']
        unit = request.form['unit']

        product = ChemicalProduct(
            name=name,
            cas_number=cas,
            unit=unit
        )
        db.session.add(product)
        db.session.commit()

        inventory = Inventory(
            product_id=product.id,
            current_stock=0
        )
        db.session.add(inventory)
        db.session.commit()

        return redirect('/products')

    # SEARCH LOGIC
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


# ---------------- INVENTORY LIST ----------------
@app.route('/inventory')
def inventory():
    inventory = Inventory.query.all()
    return render_template('inventory.html', inventory=inventory)


# ---------------- UPDATE STOCK (IN / OUT) ----------------
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

    # SAVE STOCK MOVEMENT HISTORY
    movement = StockMovement(
        product_id=item.product_id,
        movement_type=action,
        quantity=quantity
    )
    db.session.add(movement)

    db.session.commit()
    return redirect('/inventory')

# ---------------- STOCK MOVEMENT HISTORY ----------------
@app.route('/stock-history')
def stock_history():
    history = StockMovement.query.order_by(StockMovement.timestamp.desc()).all()
    return render_template('stock_history.html', history=history)

# ---------------- DELETE PRODUCT ----------------
@app.route('/delete-product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = ChemicalProduct.query.get_or_404(product_id)

    inventory = Inventory.query.filter_by(product_id=product.id).first()
    if inventory:
        db.session.delete(inventory)

    db.session.delete(product)
    db.session.commit()

    return redirect('/products')


# ---------------- RUN APP ----------------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run()

