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

item_blp = Blueprint('items', __name__, description='Item access')

@item_blp.route('')
class ItemResource(MethodView):

    @item_blp.arguments(ItemSchema)
    @item_blp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)

        try:
            addAndCommit(item)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return item

    @item_blp.response(200, ItemSchema(many=True))
    def get(self):
        return ItemModel.query.all()


@item_blp.route('/<int:item_id>')
class ItemItemResource(MethodView):

    @item_blp.response(200, ItemSchema)
    @item_blp.alt_response(404, description='Item not found')
    def get(self, item_id):
        return ItemModel.query.get_or_404(item_id)

    @item_blp.response(204, description='Item was removed')
    @item_blp.alt_response(404, description='Item not found')
    def delete(self, item_id):
        item = ItemModel.query.get_or_404(item_id)

        try:
            deleteAndCommit(item)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {}
