from db import db

class SessionTokenModel(db.Model):
    __tablename__ = "session_token"
    
    id = db.Column(db.String(32), primary_key=True)
    jti = db.Column(db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), unique=False, nullable=False)
    user = db.relationship('UserModel', back_populates='tokens')