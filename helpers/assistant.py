import json
from time import sleep

from helpers import Openai
from flask import Flask, request, jsonify
from helpers.storages import PrivateStorage

ASSISTANTS_FILE_PATH = 'assistants.json'

openai = Openai()
storage = PrivateStorage()

if not openai.assistant_compatibility():
    raise ValueError(f"Error: OpenAI version is less than the required version 1.1.1")

def check_assistant(assistant_name, instructions = "", assistants_file = ASSISTANTS_FILE_PATH):
    
    def create(assistants: dict):
        assistant = openai.create_assistant(instructions = instructions, name = assistant_name, tools = [{"type": "retrieval"}])

        assistants[assistant_name] = {
            "id": assistant.id,
            "name": assistant.name,
            "description": assistant.description,
            "instructions": assistant.instructions,
            "file_ids": assistant.file_ids
        }

        storage.write(json.dumps(assistants), assistants_file)

        return assistants[assistant_name]
    
    if storage.exists(assistants_file):
        with storage.read(assistants_file) as file:
            assistants = json.load(file)
            if assistant_name in assistants:
                return assistants[assistant_name]["id"]
    else:
        assistants = {}
        storage.write(json.dumps(assistants), assistants_file)
    
    return create(assistants)["id"]

def chat_assistant(assistant_id, message, files:list = [], file_ids:list = []):
    
    thread_id = openai.create_thread().id
    
    for file in files:
        pass
    
    openai.create_message(content = message, thread_id = thread_id, file_ids = file_ids)
    
    run_id = openai.run_thread(thread_id = thread_id, assistant_id = assistant_id).id
    
    while openai.get_status_thread(thread_id = thread_id, run_id = run_id) != "completed": sleep(1)
        
    response = openai.get_response(thread_id = thread_id)
    
    return response
