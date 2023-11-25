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

item_type_blp = Blueprint('item_types', __name__, description='Item Type access')

@item_type_blp.route('')
class ItemTypeResource(MethodView):

    @item_type_blp.arguments(ItemTypeSchema)
    @item_type_blp.response(201, ItemTypeSchema)
    def post(self, item_type_data):
        item_type = ItemTypeModel(**item_type_data)

        try:
            addAndCommit(item_type)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return item_type

    @item_type_blp.response(200, ItemTypeSchema(many=True))
    def get(self):
        return ItemTypeModel.query.all()


@item_type_blp.route('/<int:item_type_id>')
class ItemTypeItemResource(MethodView):

    @item_type_blp.response(200, ItemTypeSchema)
    @item_type_blp.alt_response(404, description='Item Type not found')
    def get(self, item_type_id):
        return ItemTypeModel.query.get_or_404(item_type_id)

    @item_type_blp.response(204, description='Item Type was removed')
    @item_type_blp.alt_response(404, description='Item Type not found')
    def delete(self, item_type_id):
        item_type = ItemTypeModel.query.get_or_404(item_type_id)

        try:
            deleteAndCommit(item_type)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {}
