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
        return UserStoryModel.query.all()


@blp.route('/<int:user_story_id>')
class UserStoryItemResource(MethodView):

    @blp.response(200, UserStorySchema)
    @blp.alt_response(404, description='User Story not found')
    def get(self, user_story_id):
        return UserStoryModel.query.get_or_404(user_story_id)

    @blp.arguments(UserStorySchema)
    @blp.response(200, UserStorySchema)
    @blp.alt_response(404, description='User Story not found')
    def put(self, user_story_data, user_story_id):
        user_story = UserStoryModel.query.get_or_404(user_story_id)

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
    def delete(self, user_story_id):
        user_story = UserStoryModel.query.get_or_404(user_story_id)

        try:
            deleteAndCommit(user_story)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {}
