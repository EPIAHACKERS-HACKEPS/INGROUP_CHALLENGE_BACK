import json
from time import sleep
from flask import request
from flask_jwt_extended import jwt_required
from flask_smorest import Blueprint, abort
from helpers import assistant
from flask.views import MethodView

from globals import ASSISTANT_CLASSIFICATION_PROMPT, PREFIX_PROMPT
from schema import AssistantSchema

blp = Blueprint('assitant', __name__, description='Start chat with assistant')


@blp.route('')
class Classification(MethodView):
    
    @jwt_required(refresh=True)
    @blp.response(200, AssistantSchema)
    def post(self):
        
        assistant_id = assistant.check_assistant("classification", ASSISTANT_CLASSIFICATION_PROMPT)
        
        files = request.files.getlist("files")
        
        prompt = PREFIX_PROMPT + "\n" + (request.form.get("prompt") or "").strip()
        
        response = assistant.chat_assistant(assistant_id, prompt, files = files)
                
        try:
            
            response_json = "{}"
            
            init = response.find("{")
            end = response.rfind("}") + 1
            
            if init >=0 and end > 0:        
                response_json = response[init:end]
            
            response_json = json.loads(response_json)
            response_json['response'] = response
            return response_json
        except:
            return {
                "user_story": {},
                "response": response,
            }
                