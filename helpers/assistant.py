import io
import json
import os
from time import sleep
import time

from helpers import Openai
from flask import Flask, request, jsonify
from helpers.storages import PrivateStorage
from globals import PRIVATE_STORAGE_PATH

ASSISTANTS_FILE_PATH = 'assistants.json'

openai = Openai()
storage = PrivateStorage()
storage_tmp = PrivateStorage(os.path.join(PRIVATE_STORAGE_PATH, "tmp"))
storage_file = PrivateStorage(os.path.join(PRIVATE_STORAGE_PATH, "files"))

if not openai.assistant_compatibility():
    raise ValueError(f"Error: OpenAI version is less than the required version 1.1.1")

def check_assistant(assistant_name, instructions = "", assistants_file = ASSISTANTS_FILE_PATH, files = []):
    
    def create(assistants: dict):
        assistant = openai.create_assistant(instructions = instructions, name = assistant_name, tools = [{"type": "retrieval"}], files=files)

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

def chat_assistant(assistant_id, message, files:list = [], file_ids:list = [], thread_id = None):
    
    thread_id = thread_id or openai.create_thread().id
    
    files_prompts = ""
    
    file_names = []
    
    for file in files:
        file_name = file.filename + "_" + int(time.time() * 1000)
        storage_file.save(file, file_name, mode="wb")
        file_ids.append(openai.create_file(file=storage_tmp.read(file_name, mode="rb"), purpose='assistants').id)
        files_prompts += f"\nFile: {file.filename}\n\t" + storage_file.read(file.file_name, mode="r").read()
        file_names.append(file_name)
      
    message = message + files_prompts #TODO: delete files_prompts
      
    print("message:")
    print(message)
      
    openai.create_message(content = message, thread_id = thread_id, file_ids = []) #TODO: Add file_ids
        
    run_id = openai.run_thread(thread_id = thread_id, assistant_id = assistant_id).id
        
    while openai.get_status_thread(thread_id = thread_id, run_id = run_id) != "completed": sleep(1)
        
    response = openai.get_response(thread_id = thread_id)
    
    storage_tmp.removeAllFiles()
    
    for file_id in file_ids:
        openai.delete_file(file_id)
    
    return response, file_names

def trainClassification(assistant_id, input_file, output_file):
    
    instructions = f"Dado el/los siguientes archivos:\n{input_file}\n\nDeberías generar la siguiente respuesta:\n{output_file}"
    
    openai.update_assistant(assistant_id, instructions = instructions)
    
    return True
