import traceback
from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity, decode_token

import uuid
import datetime

from models import ItemTypeModel
from schema import ItemTypeSchema

from db import db, addAndCommit, deleteAndCommit

from globals import DEBUG

blp = Blueprint('item_types', __name__, description='Item Type access')

@blp.route('')
class ItemTypeResource(MethodView):

    @blp.arguments(ItemTypeSchema)
    @blp.response(201, ItemTypeSchema)
    def post(self, item_type_data):
        item_type = ItemTypeModel(**item_type_data)

        try:
            addAndCommit(item_type)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return item_type

    @blp.response(200, ItemTypeSchema(many=True))
    def get(self):
        return ItemTypeModel.query.all()


@blp.route('/<int:item_type_id>')
class ItemTypeItemResource(MethodView):

    @blp.response(200, ItemTypeSchema)
    @blp.alt_response(404, description='Item Type not found')
    def get(self, item_type_id):
        return ItemTypeModel.query.get_or_404(item_type_id)
    
    @blp.arguments(ItemTypeSchema)
    @blp.response(200, ItemTypeSchema)
    @blp.alt_response(404, description='Item Type not found')
    def put(self, item_type_data, item_type_id):
        item_type = ItemTypeModel.query.get_or_404(item_type_id)
        for key, value in item_type_data.items():
            setattr(item_type, key, value)

        try:
            addAndCommit(item_type)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return item_type
    @blp.response(204, description='Item Type was removed')
    @blp.alt_response(404, description='Item Type not found')
    def delete(self, item_type_id):
        item_type = ItemTypeModel.query.get_or_404(item_type_id)

        try:
            deleteAndCommit(item_type)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {}

