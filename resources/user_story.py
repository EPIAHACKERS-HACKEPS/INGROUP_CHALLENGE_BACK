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
user_story_blp = Blueprint('user_stories', __name__, description='User Story access')

@user_story_blp.route('')
class UserStoryResource(MethodView):

    @user_story_blp.arguments(UserStorySchema)
    @user_story_blp.response(201, UserStorySchema)
    def post(self, user_story_data):
        user_story = UserStoryModel(**user_story_data)

        try:
            addAndCommit(user_story)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return user_story

    @user_story_blp.response(200, UserStorySchema(many=True))
    def get(self):
        return UserStoryModel.query.all()


@user_story_blp.route('/<int:user_story_id>')
class UserStoryItemResource(MethodView):

    @user_story_blp.response(200, UserStorySchema)
    @user_story_blp.alt_response(404, description='User Story not found')
    def get(self, user_story_id):
        return UserStoryModel.query.get_or_404(user_story_id)

    @user_story_blp.response(204, description='User Story was removed')
    @user_story_blp.alt_response(404, description='User Story not found')
    def delete(self, user_story_id):
        user_story = UserStoryModel.query.get_or_404(user_story_id)

        try:
            deleteAndCommit(user_story)
        except SQLAlchemyError as e:
            abort(500, message=str(e))

        return {}
