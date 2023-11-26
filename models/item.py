from db import db

class ItemModel(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    priority = db.Column(db.Integer)
    id_userstory = db.Column(db.Integer, db.ForeignKey('user_story.id'), nullable=False)
    item_type_id = db.Column(db.Integer, db.ForeignKey('item_types.id'), nullable=False)
    
    user_story = db.relationship('UserStoryModel', back_populates='items')
    item_type = db.relationship('ItemTypeModel')
    
