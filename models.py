from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# -----------------------------
# CHEMICAL PRODUCT MODEL
# -----------------------------
class ChemicalProduct(db.Model):
    __tablename__ = 'chemical_product'

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    # UNIQUE CAS NUMBER (CRITICAL)
    cas_number = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        index=True
    )

    unit = db.Column(
        db.String(20),
        nullable=False
    )

    # One-to-one relationship with Inventory
    inventory = db.relationship(
        'Inventory',
        back_populates='product',
        uselist=False,
        cascade='all, delete-orphan'
    )

    # One-to-many relationship with StockMovement
    movements = db.relationship(
        'StockMovement',
        back_populates='product',
        cascade='all, delete-orphan',
        passive_deletes=True
    )

    def __repr__(self):
        return f"<ChemicalProduct id={self.id} name={self.name} cas={self.cas_number}>"


# -----------------------------
# INVENTORY MODEL
# -----------------------------
class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'chemical_product.id',
            ondelete='CASCADE'
        ),
        nullable=False,
        unique=True
    )

    current_stock = db.Column(
        db.Float,
        nullable=False,
        default=0.0
    )

    product = db.relationship(
        'ChemicalProduct',
        back_populates='inventory'
    )

    def __repr__(self):
        return f"<Inventory product_id={self.product_id} stock={self.current_stock}>"


# -----------------------------
# STOCK MOVEMENT HISTORY MODEL
# -----------------------------
class StockMovement(db.Model):
    __tablename__ = 'stock_movement'

    id = db.Column(db.Integer, primary_key=True)

    product_id = db.Column(
        db.Integer,
        db.ForeignKey(
            'chemical_product.id',
            ondelete='CASCADE'
        ),
        nullable=False,
        index=True
    )

    movement_type = db.Column(
        db.String(10),
        nullable=False
    )  # IN / OUT

    quantity = db.Column(
        db.Float,
        nullable=False
    )

    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.utcnow,
        index=True
    )

    product = db.relationship(
        'ChemicalProduct',
        back_populates='movements'
    )

    def __repr__(self):
        return (
            f"<StockMovement id={self.id} "
            f"product_id={self.product_id} "
            f"type={self.movement_type} "
            f"qty={self.quantity}>"
        )
