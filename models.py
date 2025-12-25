from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ChemicalProduct(db.Model):
    __tablename__ = 'chemical_product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    cas_number = db.Column(db.String(50), unique=True, nullable=False)
    unit = db.Column(db.String(20), nullable=False)

    inventory = db.relationship('Inventory', backref='product', uselist=False)


class Inventory(db.Model):
    __tablename__ = 'inventory'

    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('chemical_product.id'))
    current_stock = db.Column(db.Float, default=0)
