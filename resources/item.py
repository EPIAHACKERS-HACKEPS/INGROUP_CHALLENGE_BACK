import traceback
from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity, decode_token

import uuid
import datetime

from models import ItemModel
from schema import ItemSchema

from db import db, addAndCommit, deleteAndCommit

from globals import DEBUG

blp = Blueprint('items', __name__, description='Item access')

@blp.route('')
class ItemResource(MethodView):

    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)

        try:
            addAndCommit(item)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return item

    @blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()


@blp.route('/<int:item_id>')
class ItemItemResource(MethodView):

    @blp.response(200, ItemSchema)
    @blp.alt_response(404, description='Item not found')
    def get(self, item_id):
        return ItemModel.query.get_or_404(item_id)
    
    @blp.arguments(ItemSchema)
    @blp.response(200, ItemSchema)
    @blp.alt_response(404, description='Item not found')
    def put(self, item_data, item_id):
        item = ItemModel.query.get_or_404(item_id)
        for key, value in item_data.items():
            setattr(item, key, value)
        try:
            addAndCommit(item)
        except SQLAlchemyError as e:
            abort(500, message=str(e))
        return item

    @blp.response(204, description='Item was removed')
    @blp.alt_response(404, description='Item not found')
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)

        try:
            deleteAndCommit(item)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {}
@blp.route('/create')
class UserStoryCreate(MethodView):
    
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, user_data):
        item = ItemModel(**user_data)                
        try:
            addAndCommit(item)
        except SQLAlchemyError as e:
            traceback.print_exc()
            abort(500, message = str(e) if DEBUG else 'Could not save user.')
                        
        return item