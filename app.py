import os
import random
import traceback
from flask import Flask, jsonify, make_response, redirect, request, render_template
from flask_smorest import abort, Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from sqlalchemy.exc import SQLAlchemyError
from flask_cors import CORS

from db import db, deleteAndCommit

from globals import DEBUG, SECRET_JWT, DATABASE_URI, API_PREFIX
from db import db, deleteAndCommit

from resources.user import blp as UserBlueprint
from resources.user_story import blp as UserStoryBlueprint
from resources.item import blp as ItemBlueprint
from resources.item_type import blp as ItemTypeBlueprint
from resources.classification import blp as ClassificationBlueprint
from resources.assistant import blp as AssistantBlueprint

from models import SessionTokenModel

def create_app():
    app = Flask(__name__)
    cors = CORS(app, resources={f"/{API_PREFIX}/*": {"origins": "*"}})

    app.debug = DEBUG
    app.jinja_env.auto_reload = DEBUG
    
    app.config['API_TITLE'] = 'CLASSIFICATION API v1'
    app.config['API_VERSION'] = 'v1'
    app.config['OPENAPI_VERSION'] = '3.0.3'
    app.config['OPENAPI_URL_PREFIX'] = '/'
    app.config['OPENAPI_SWAGGER_UI_PATH'] = '/swagger-ui'
    app.config['OPENAPI_SWAGGER_UI_URL'] = 'https://cdn.jsdelivr.net/npm/swagger-ui-dist/'
    app.config['CORS_HEADERS'] = 'Content-Type'
    
    ##BBDD
    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config['JWT_SECRET_KEY'] = SECRET_JWT
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    
    db.init_app(app)
    
    Migrate(app, db)
    
    api = Api(app)
    
    api.spec.components.security_scheme(
        'jwt', {'type': 'http', 'scheme': 'bearer', 'bearerFormat': 'JWT', 'x-bearerInfoFunc': 'app.decode_token'}
    )
    
    jwt = JWTManager(app)
    
    def getApiPrefix(url): return f"/{API_PREFIX}/{url}"
    
    ##JWT CHECK
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        
        try:
            tokenId = jwt_payload['token']
            jti = jwt_payload['jti']
            identity = jwt_payload['sub']
            
            try:
                session_token = SessionTokenModel.query.get(tokenId)
            except SQLAlchemyError as e:
                traceback.print_exc()
                abort(500, message = str(e) if DEBUG else 'Could not check the token.')
            
            if not session_token: return True
            
            return not (session_token.jti == jti and session_token.user_id == identity)
            
        except KeyError:
            return True
            
    ## JWT ERRORS
    @jwt.invalid_token_loader
    def invalid_token_callback(error):                
        return jsonify({"message": error, "error": "invalid_token"}), 401
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token is not fresh.", "error": "fresh_token_required"}), 401
    
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        deleteAndCommit(SessionTokenModel.query.get(jwt_payload['token']))    
        return jsonify({"message": "The token has expired.", "error": "token_expired"}), 401
    
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        headers = request.headers
        for header in headers:
            print(header)
        return jsonify({"message": error, "error": "token_unauthorized"}), 401

    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return jsonify({"message": "The token has been revoked.", "error": "token_revoked"}), 401
    
    ## NotImplementedError
    @app.errorhandler(NotImplementedError)
    def handle_not_implemented_error(error):
        response = {
            "error_message": str(error),
            "code": 501,
            "status": "Not Implemented"
        }
        return jsonify(response), 501
    
    ##Routes
    api.register_blueprint(UserBlueprint, url_prefix=getApiPrefix('user'))
    api.register_blueprint(UserStoryBlueprint, url_prefix=getApiPrefix('user_story'))
    api.register_blueprint(ItemBlueprint, url_prefix=getApiPrefix('item'))
    api.register_blueprint(ItemTypeBlueprint, url_prefix=getApiPrefix('item_type'))
    api.register_blueprint(ClassificationBlueprint, url_prefix=getApiPrefix('classification'))
    api.register_blueprint(AssistantBlueprint, url_prefix=getApiPrefix('assistant'))
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(threaded=True)
