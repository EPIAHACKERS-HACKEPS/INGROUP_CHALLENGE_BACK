import traceback
from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity, decode_token
from flask import request, jsonify


from models import UserStoryModel
from schema import UserStorySchema

from db import db, addAndCommit, deleteAndCommit

from globals import DEBUG
blp = Blueprint('user_stories', __name__, description='User Story access')

@blp.route('')
class UserStoryResource(MethodView):

    @blp.arguments(UserStorySchema)
    @blp.response(201, UserStorySchema)
    def post(self, user_story_data):
        user_story = UserStoryModel(**user_story_data)

        try:
            addAndCommit(user_story)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return user_story

    @blp.response(200, UserStorySchema(many=True))
    def get(self):
        # Parámetros opcionales de paginación
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)

        # Cálculo del offset
        offset = (page - 1) * per_page

        # Consulta paginada a la base de datos
        user_stories = UserStoryModel.query.offset(offset).limit(per_page).all()

        # Obtener el total de elementos
        total_elements = UserStoryModel.query.count()

        # Serializar los resultados
        user_stories_schema = UserStorySchema(many=True)
        result = user_stories_schema.dump(user_stories)

        # Añadir el total de elementos al JSON de respuesta
        result_with_total = {
            'total_elements': total_elements,
            'user_stories': result
        }

        return jsonify(result_with_total)



@blp.route('/<int:id>')
class UserStoryItemResource(MethodView):

    @blp.response(200, UserStorySchema)
    @blp.alt_response(404, description='User Story not found')
    def get(self, id):
        return UserStoryModel.query.get_or_404(id)

    @blp.arguments(UserStorySchema)
    @blp.response(200, UserStorySchema)
    @blp.alt_response(404, description='User Story not found')
    def put(self, user_story_data, id):
        user_story = UserStoryModel.query.get_or_404(id)

        # Actualiza los campos del UserStory según los datos proporcionados
        for key, value in user_story_data.items():
            setattr(user_story, key, value)

        try:
            addAndCommit(user_story)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return user_story
    
    @blp.response(204, description='User Story was removed')
    @blp.alt_response(404, description='User Story not found')
    def delete(self, id):
        user_story = UserStoryModel.query.get_or_404(id)

        try:
            deleteAndCommit(user_story)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {}
    
@blp.route('/create')
class UserStoryCreate(MethodView):
    
    @blp.arguments(UserStorySchema)
    @blp.response(201, UserStorySchema)
    def post(self, user_data):
        user_story = UserStoryModel(**user_data)                
        try:
            addAndCommit(user_story)
        except SQLAlchemyError as e:
            traceback.print_exc()
            abort(500, message = str(e) if DEBUG else 'Could not save user.')
                        
        return user_story
