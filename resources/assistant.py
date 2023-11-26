import json
import time
from flask_smorest import Blueprint, abort
from helpers import assistant
from flask.views import MethodView

from globals import ASSISTANT_BOT_PROMPT, ASSISTANT_CLASSIFICATION_PROMPT, DEBUG, KNOWLEDGE_FILE, PREFIX_PROMPT
from helpers.userStory import procesClassification
from models.item import ItemModel
from models.item_type import ItemTypeModel
from schema import AssistantSchema, ChatAssistantData, ThreadIdSchema

from helpers import assistant

blp = Blueprint('assitant', __name__, description='Start chat with assistant')

    
@blp.route('/start')
class StartAssistant(MethodView):
    
    @blp.response(200, ThreadIdSchema)
    def get(self):
        print(f"[DEBUG] STARTING ASSISTANT")        
        thread_id = assistant.openai.create_thread().id
        
        return {"thread_id": thread_id}
    
@blp.route('/chat')
class ChatAssistant(MethodView):
    
    @blp.arguments(ChatAssistantData)
    @blp.response(200, ChatAssistantData)
    @blp.alt_response(404, description='The thread was not found')
    def post(self, data):
        thread_id = data['thread_id']
        user_input = data['message']
        
        if not assistant.openai.exist_thread(thread_id):
            abort(404, message = "Thread not found")
        
        print(f"[DEBUG] CHATTING WITH ASSISTANT '{thread_id}' - '{user_input}'")
        
        assistant_id = assistant.check_assistant("bot", ASSISTANT_BOT_PROMPT, files = [assistant.storage.read(KNOWLEDGE_FILE, mode="rb")])
        
        response, _ = assistant.chat_assistant(assistant_id, message = user_input, thread_id = thread_id)
        
        print(f"[DEBUG] RESPONSE: {response}")
        
        assistant.storage.write(json.dumps({"id": thread_id}), f"thread_id.json")
        
        return {"response": response}
    
@blp.route('/end')
class EndAssistant(MethodView):
    
    @blp.response(200, AssistantSchema)
    @blp.alt_response(404, description='The thread was not found')
    def get(self):
        
        thread_id = json.loads(assistant.storage.read(f"thread_id.json", mode="r").read())["id"]
        
        print(f"[DEBUG] ENDING ASSISTANT '{thread_id}'")
        
        if not assistant.openai.exist_thread(thread_id):
            abort(404, message = "Thread not found")
        
        print(f"[DEBUG] GETTING MESSAGES FROM THREAD '{thread_id}'")
        messages = assistant.openai.get_messages(thread_id)
        print(f"[DEBUG] DELETING THREAD '{thread_id}'")
        assistant.openai.delete_thread(thread_id)
        
        chat = [{"role": m.role, "message": m.content[0].text.value} for m in messages]
        
        chat = chat[::-1]
        
        assistant_id = assistant.check_assistant("classification", ASSISTANT_CLASSIFICATION_PROMPT)
        
        storage_tmp = assistant.storage_tmp
                
        file_name = f"chat_bot_{int(time.time() * 1000)}.json"
        
        storage_tmp.write(json.dumps(chat), file_name)
        
        print(f"[DEBUG] FILE NAME: {file_name}")

        file_id = assistant.openai.create_file(file=storage_tmp.read(file_name, mode="rb"), purpose='assistants').id
        
        response, file_names = assistant.chat_assistant(assistant_id, message = PREFIX_PROMPT + "\nIt's a chat between an user and the app bot:\n" + storage_tmp.read(file_name, mode="r").read(), file_ids = [file_id]) #TODO: delete storage_tmp.read
                
        result = procesClassification(response, file_names)
        
        if "user_story" in result:
            return result
        
        print(f"[ERROR] user_story not found")
        
        abort(500, message = "Internal error")
        