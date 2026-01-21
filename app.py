from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from datetime import datetime

from models import db, ChemicalProduct, Inventory, StockMovement

app = Flask(__name__)

# ---------------- CONFIG ----------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'dev-secret-key'   # REQUIRED FOR FLASH

db.init_app(app)

# ---------------- HOME ----------------
@app.route('/')
def home():
    return render_template('index.html')


# ---------------- PRODUCTS ----------------
@app.route('/products', methods=['GET', 'POST'])
def products():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        cas = request.form.get('cas_number', '').strip()
        unit = request.form.get('unit')
        initial_quantity = float(request.form.get('initial_quantity', 0))

        # ---------- VALIDATION ----------
        if not name or not cas:
            flash("Product name and CAS number are required.", "error")
            return redirect(url_for('products'))

        if initial_quantity <= 0:
            flash("Initial stock must be a positive number.", "error")
            return redirect(url_for('products'))

        # ---------- DUPLICATE CAS ----------
        existing = ChemicalProduct.query.filter_by(cas_number=cas).first()
        if existing:
            flash("CAS number already exists. Please enter a unique CAS number.", "error")
            return redirect(url_for('products'))

        try:
            product = ChemicalProduct(
                name=name,
                cas_number=cas,
                unit=unit
            )
            db.session.add(product)
            db.session.flush()  # get product.id

            inventory = Inventory(
                product_id=product.id,
                current_stock=initial_quantity
            )
            db.session.add(inventory)

            movement = StockMovement(
                product_id=product.id,
                movement_type='IN',
                quantity=initial_quantity,
                timestamp=datetime.utcnow()
            )
            db.session.add(movement)

            db.session.commit()

            flash("Product added successfully.", "success")

        except IntegrityError:
            db.session.rollback()
            flash("CAS number must be unique.", "error")

        except Exception:
            db.session.rollback()
            flash("Unexpected server error.", "error")

        return redirect(url_for('products'))

    # ---------- SEARCH ----------
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

    quantity = float(request.form.get('quantity', 0))
    action = request.form.get('type')

    if quantity <= 0:
        flash("Quantity must be a positive number.", "error")
        return redirect(url_for('inventory'))

    if action == 'IN':
        item.current_stock += quantity

    elif action == 'OUT':
        if item.current_stock - quantity < 0:
            flash("Stock cannot go below zero.", "error")
            return redirect(url_for('inventory'))
        item.current_stock -= quantity

    else:
        flash("Invalid stock operation.", "error")
        return redirect(url_for('inventory'))

    movement = StockMovement(
        product_id=item.product_id,
        movement_type=action,
        quantity=quantity,
        timestamp=datetime.utcnow()
    )
    db.session.add(movement)
    db.session.commit()

    flash("Stock updated successfully.", "success")
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

    Inventory.query.filter_by(product_id=product.id).delete()
    StockMovement.query.filter_by(product_id=product.id).delete()

    db.session.delete(product)
    db.session.commit()

    flash("Product deleted successfully.", "success")
    return redirect(url_for('products'))


# ---------------- INIT DB ----------------
with app.app_context():
    db.create_all()


# ---------------- RUN ----------------
if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
