from db import db

class UserStoryModel(db.Model):
    __tablename__ = "user_story"

    id_userstory = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    titulo = db.Column(db.String(255), nullable=False)

    items = db.relationship('ItemModel', back_populates='user_story')
