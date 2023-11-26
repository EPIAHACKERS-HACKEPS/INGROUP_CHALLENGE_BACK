import json
from time import sleep
from flask import request
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from helpers import assistant
from flask.views import MethodView

from globals import ASSISTANT_CLASSIFICATION_PROMPT, PREFIX_PROMPT
from schema import AssistantSchema

blp = Blueprint('train assitant classification', __name__, description='Train classification assistant')


