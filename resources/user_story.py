import traceback
from flask import request
from flask_smorest import Blueprint, abort
from flask.views import MethodView
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt, get_jwt_identity, decode_token

from models import UserStoryModel
from schema import UserStorySchema

from db import db, addAndCommit, deleteAndCommit

from globals import DEBUG

# Creación de un Blueprint para el recurso de user stories
blp = Blueprint('user_stories', __name__, description='User Story access')

# Definición de la ruta para listar y crear user stories
@blp.route('')
class UserStoryResource(MethodView):

    @blp.arguments(UserStorySchema)
    @blp.response(201, UserStorySchema)
    def post(self, user_story_data):
        """
        Endpoint para crear un nuevo user story.

        :param user_story_data: Datos del user story proporcionados en la solicitud.
        :return: User story creado.
        """
        user_story = UserStoryModel(**user_story_data)

        try:
            addAndCommit(user_story)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return user_story

    @blp.response(200, UserStorySchema(many=True))
    def get(self):
        """
        Endpoint para obtener todos los user stories.

        :return: Lista de todos los user stories.
        """
        return UserStoryModel.query.all()

# Definición de la ruta para obtener, actualizar y eliminar un user story específico
@blp.route('/<int:id>')
class UserStoryItemResource(MethodView):

    @blp.response(200, UserStorySchema)
    @blp.alt_response(404, description='User Story not found')
    def get(self, id):
        """
        Endpoint para obtener un user story específico por su ID.

        :param id: ID del user story a obtener.
        :return: User story encontrado.
        """
        return UserStoryModel.query.get_or_404(id)

    @blp.arguments(UserStorySchema)
    @blp.response(200, UserStorySchema)
    @blp.alt_response(404, description='User Story not found')
    def put(self, user_story_data, id):
        """
        Endpoint para actualizar un user story específico por su ID.

        :param user_story_data: Nuevos datos para el user story.
        :param id: ID del user story a actualizar.
        :return: User story actualizado.
        """
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
        """
        Endpoint para eliminar un user story específico por su ID.

        :param id: ID del user story a eliminar.
        :return: Respuesta vacía con código 204 si la eliminación fue exitosa.
        """
        user_story = UserStoryModel.query.get_or_404(id)

        try:
            deleteAndCommit(user_story)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {}

# Definición de la ruta para crear un user story
@blp.route('/create')
class UserStoryCreate(MethodView):
    
    @blp.arguments(UserStorySchema)
    @blp.response(201, UserStorySchema)
    def post(self, user_data):
        """
        Endpoint para crear un nuevo user story.

        :param user_data: Datos del user story proporcionados en la solicitud.
        :return: User story creado.
        """
        user_story = UserStoryModel(**user_data)                
        try:
            addAndCommit(user_story)
        except SQLAlchemyError as e:
            traceback.print_exc()
            abort(500, message=str(e) if DEBUG else 'Could not save user.')
                        
        return user_story
