from db import db

class ItemTypeModel(db.Model):
    __tablename__ = "item_types"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)
    
    items = db.relationship('ItemModel', back_populates='item_type')
