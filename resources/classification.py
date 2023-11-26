import json
from time import sleep
from flask import request
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from helpers import assistant
from flask.views import MethodView

from globals import ASSISTANT_CLASSIFICATION_PROMPT, PREFIX_PROMPT
from helpers.userStory import procesClassification
from schema import AssistantSchema

blp = Blueprint('assitant classification', __name__, description='Classification assistant')

@blp.route('')
class Classification(MethodView):
    
    @jwt_required(refresh=True)
    @blp.response(200, AssistantSchema)
    def post(self):
        
        assistant_id = assistant.check_assistant("classification", ASSISTANT_CLASSIFICATION_PROMPT)
        
        files = request.files.getlist("files")
        
        prompt = PREFIX_PROMPT + "\n" + (request.form.get("prompt") or "").strip()
        
        response, file_names = assistant.chat_assistant(assistant_id, prompt, files = files)
                
        return procesClassification(response, file_names)
                
