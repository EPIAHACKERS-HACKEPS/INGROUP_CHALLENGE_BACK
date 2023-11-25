from db import db

class UserModel(db.Model):
    __tablename__ = "user"
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=False)
    
    tokens = db.relationship('SessionTokenModel', back_populates='user', lazy='dynamic', cascade="all, delete")
