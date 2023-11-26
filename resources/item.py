import traceback
from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity, decode_token
from flask import request, jsonify

import uuid
import datetime
from helpers.userStory import train

from models import ItemModel
from schema import ItemSchema

from db import db, addAndCommit, deleteAndCommit

from globals import DEBUG

blp = Blueprint('items', __name__, description='Item access')

@blp.route('')
class ItemResource(MethodView):
    @jwt_required(refresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema)
    def post(self, item_data):
        item = ItemModel(**item_data)

        try:
            addAndCommit(item)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return item
    @jwt_required(refresh=True)
    @blp.response(200, ItemSchema(many=True))
    def get(self):
        # Parámetros opcionales de paginación
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        
        # Nuevo parámetro para el orden (ascendente o descendente)
        order_by = request.args.get('order_by', default='desc', type=str)
        
        # Cálculo del offset
        offset = (page - 1) * per_page

        # Consulta paginada a la base de datos
        if order_by == 'asc':
            user_stories = ItemModel.query.order_by(ItemModel.id.asc()).offset(offset).limit(per_page).all()
        elif order_by == 'desc':
            user_stories = ItemModel.query.order_by(ItemModel.id.desc()).offset(offset).limit(per_page).all()
        else:
            abort(400, message='Invalid order_by parameter. Use "asc" or "desc".')

        # Obtener el total de elementos
        total_elements = ItemModel.query.count()

        # Serializar los resultados
        item_schema = ItemSchema(many=True)
        result = item_schema.dump(user_stories)

        # Añadir el total de elementos al JSON de respuesta
        result_with_total = {
            'total_elements': total_elements,
            'elements': result
        }

        return jsonify(result_with_total)


@blp.route('/<int:item_id>')
class ItemItemResource(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200, ItemSchema)
    @blp.alt_response(404, description='Item not found')
    def get(self, item_id):
        return ItemModel.query.get_or_404(item_id)
    @jwt_required(refresh=True)
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
            
        train(item.user_story)
            
        return item
    @jwt_required(refresh=True)
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
    @jwt_required(refresh=True)
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
@blp.route('/count')
class ItemCountResource(MethodView):
    @jwt_required(refresh=True)
    @blp.response(200)
    def get(self):
        # Obtener el número total de Items con type_id 1
        count_type_1 = ItemModel.query.filter_by(type_id=2).count()
        # Obtener el número total de Items con type_id 2
        count_type_2 = ItemModel.query.filter_by(type_id=3).count()
        # Crear un diccionario para el resultado
        result = {
            "bugs": count_type_1,
            "feature_requests": count_type_2,
        }

        return jsonify(result)