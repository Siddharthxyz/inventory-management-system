from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


# -----------------------------
# CHEMICAL PRODUCT MODEL
# -----------------------------
class ChemicalProduct(db.Model):
    __tablename__ = 'chemical_product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cas_number = db.Column(db.String(50), unique=True, nullable=False)
    unit = db.Column(db.String(20), nullable=False)

    # One-to-one relationship with Inventory
    inventory = db.relationship(
        'Inventory',
        backref='product',
        uselist=False,
        cascade='all, delete'
    )

    # One-to-many relationship with StockMovement
    movements = db.relationship(
        'StockMovement',
        backref='product',
        cascade='all, delete'
    )

    def __repr__(self):
        return f"<ChemicalProduct {self.name} ({self.cas_number})>"


# -----------------------------
# INVENTORY MODEL
# -----------------------------
class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('chemical_product.id'),
        nullable=False
    )
    current_stock = db.Column(db.Float, default=0)

    def __repr__(self):
        return f"<Inventory ProductID={self.product_id} Stock={self.current_stock}>"


# -----------------------------
# STOCK MOVEMENT HISTORY MODEL
# -----------------------------
class StockMovement(db.Model):
    __tablename__ = 'stock_movement'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(
        db.Integer,
        db.ForeignKey('chemical_product.id'),
        nullable=False
    )
    movement_type = db.Column(db.String(10), nullable=False)  # IN / OUT
    quantity = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return (
            f"<StockMovement ProductID={self.product_id} "
            f"Type={self.movement_type} Qty={self.quantity}>"
        )
