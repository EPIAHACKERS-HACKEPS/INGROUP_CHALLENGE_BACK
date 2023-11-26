from db import db

class UserStoryModel(db.Model):
    __tablename__ = "user_story"

    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    file_names = db.Column(db.String(512), nullable=True)

    items = db.relationship('ItemModel', cascade='all, delete', back_populates='user_story')
