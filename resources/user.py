import traceback
from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity, decode_token

import uuid
import datetime

from models import UserModel, SessionTokenModel
from schema import UserSchema, UserTokensSchema

from db import db, addAndCommit, deleteAndCommit

from globals import DEBUG

blp = Blueprint('users', __name__, description='User access')

def generateTokens(userId, access_token = False, refresh_token = True, claims = {}, expire_refresh = datetime.timedelta(days=30), expire_access = datetime.timedelta(minutes=5)):
    
    token_fresh = None
    token_refresh = None
    
    saveToken = []
       
    if access_token:
        tokenId = uuid.uuid4().hex
        claims['token'] = tokenId
        token_fresh = create_access_token(identity=userId, additional_claims=claims, expires_delta=expire_access, fresh=True)
        
        saveToken.append(token_fresh)
        
    if refresh_token:
        tokenId = uuid.uuid4().hex
        claims['token'] = tokenId
        token_refresh = create_refresh_token(identity=userId, additional_claims=claims, expires_delta=expire_refresh)
        
        saveToken.append(token_refresh)
       
    try: 
        addAndCommit(*[SessionTokenModel(id = decode_token(token)['token'], jti = decode_token(token)['jti'], user_id = userId) for token in saveToken])
    except SQLAlchemyError as e:
        traceback.print_exc()
        abort(500, message = str(e) if DEBUG else 'Could not generate tokens.')
    
    if token_fresh and token_refresh: 
        return token_fresh, token_refresh

    return token_fresh if token_fresh else token_refresh
    
    
def logOutAll(user_id):
    
    try:
        SessionTokenModel.query.filter(SessionTokenModel.user_id == user_id).delete()
        db.session.commit()
    except SQLAlchemyError as e:
        traceback.print_exc()
        abort(500, message = str(e) if DEBUG else 'Could not log-out all tokens.')
    

@blp.route('')
class User(MethodView):
    
    @blp.response(200, UserSchema)
    @blp.alt_response(404, description='The user was not found')
    @jwt_required(refresh=True)
    def get(self):
        return UserModel.query.get_or_404(get_jwt_identity())
    
    @blp.arguments(UserSchema)
    @blp.response(200, UserSchema)
    @blp.alt_response(404, description='The user was not found')
    @jwt_required(fresh=True)
    def put(self, user_data):
        user = UserModel.query.get_or_404(get_jwt_identity())
        
        user.email = user_data['email']
        user.password = pbkdf2_sha256.hash(user_data['password'])
        
        try:
            addAndCommit(user)
        except IntegrityError:
            abort(409, message = 'The email alredy exists.')
        except SQLAlchemyError as e:
            traceback.print_exc()
            abort(500, message = str(e) if DEBUG else 'Could not save user.')
            
        logOutAll(user.id)
            
        access_token, refresh_token = generateTokens(user.id, access_token=True, refresh_token=True)
            
        return {'access_token': access_token, 'refresh_token': refresh_token, 'user': user}
    
    @blp.response(204, description='Use was removed.')
    @blp.alt_response(404, description='The user was not found')
    @jwt_required(fresh=True)
    def delete(self):
        
        user = UserModel.query.get_or_404(get_jwt_identity())
        
        try:
            deleteAndCommit(user)
        except SQLAlchemyError as e:
            traceback.print_exc()
            abort(500, message = str(e) if DEBUG else 'Could not remove user.')
        
        return {}

@blp.route('/register')
class UserRegister(MethodView):
    
    @blp.arguments(UserSchema)
    @blp.response(201, UserTokensSchema)
    @blp.alt_response(409, description='The email alredy exists')
    def post(self, user_data):
                
        user = UserModel(**user_data)
        
        user.password = pbkdf2_sha256.hash(user.password)
                
        try:
            addAndCommit(user)
        except IntegrityError:
            abort(409, message = 'The email alredy exists.')
        except SQLAlchemyError as e:
            traceback.print_exc()
            abort(500, message = str(e) if DEBUG else 'Could not save user.')
            
        access_token, refresh_token = generateTokens(user.id, access_token=True, refresh_token=True)
                        
        return {'access_token': access_token, 'refresh_token': refresh_token, 'user': user}
    
@blp.route('/login')
class UserLogin(MethodView):
    
    @blp.arguments(UserSchema)
    @blp.response(200, UserTokensSchema)
    @blp.alt_response(404, description='User with email not found')
    @blp.alt_response(401, description='Invalid credentials')
    def post(self, user_data):
        
        user = UserModel.query.filter(UserModel.email == user_data['email']).first()
                
        if not user:
            abort(404, message = 'User not found.')
            
        if pbkdf2_sha256.verify(user_data['password'], user.password):
            access_token, refresh_token = generateTokens(user.id, access_token=True, refresh_token=True)
            
            return {'access_token': access_token, 'refresh_token': refresh_token, 'user': user}
                    
        abort(401, message='Invalid credentials.')
        
@blp.route('/logout')
class UserLogout(MethodView):
    
    @jwt_required(refresh=True)
    @blp.response(204, description='Logout user and expire the refresh-token')
    def post(self):
        tokenId = get_jwt().get('token')
        
        deleteAndCommit(SessionTokenModel.query.get(tokenId))
        
        return {}
    
@blp.route('/logout/all')
class UserLogout(MethodView):
    
    @jwt_required(refresh=True)
    @blp.response(204, description='Logout user and expire all the refresh-token')
    def post(self):
        
        logOutAll(get_jwt_identity())
        
        return {}
        
@blp.route('/token/refresh')
class UserTokenRefresh(MethodView):
    
    @jwt_required(refresh=True)
    @blp.response(200, description='Regenerate a new refresh token and expires the old one', example={'refresh_token': 'new-refresh-token'})
    def post(self):
        current_user = get_jwt_identity()
        token_id = get_jwt().get('token')
        
        old_token = SessionTokenModel.query.get_or_404(token_id)
        
        deleteAndCommit(old_token)
        
        return {'refresh_token': generateTokens(current_user, access_token=False, refresh_token=True)}    
    
@blp.route('/token/test')
class TokenTest(MethodView):
    @jwt_required(refresh=True)
    def post(self):
        headers = request.headers
        for header in headers:
            print(header)
        token = get_jwt()
        return {"message": "ok", "token_id": token.get('token'), "token_jti": token.get('jti'), "identity": get_jwt_identity() }