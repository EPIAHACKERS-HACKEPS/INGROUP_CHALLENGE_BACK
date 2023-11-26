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
    
    print(f"[DEBUG] CHECKING ASSISTANT '{assistant_name}'")
    
    def create(assistants: dict):
        
        print(f"[DEBUG] CREATING ASSISTANT '{assistant_name}'")
        
        assistant = openai.create_assistant(instructions = instructions, name = assistant_name, tools = [{"type": "retrieval"}], files=files)

        assistants[assistant_name] = {
            "id": assistant.id,
            "name": assistant.name,
            "description": assistant.description,
            "instructions": assistant.instructions,
            "file_ids": assistant.file_ids
        }

        print(f"\t'{assistant_name}'")

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

def chat_assistant(assistant_id, message, files:list = [], file_ids:list = [], thread_id = None, delete_thread = False):
    
    print(f"[DEBUG] CHATTING WITH ASSISTANT '{assistant_id}'")
    
    thread_id = thread_id or openai.create_thread().id
    
    print(f"[DEBUG] THREAD ID: '{thread_id}'")
    
    files_prompts = ""
    
    file_names = []
    
    for file in files:
        file_name = f"{int(time.time() * 1000)}_" + file.filename
        storage_file.save(file, file_name, mode="wb")
        print(f"[DEBUG] SAVING FILE '{file_name}' - {file}")
        file_ids.append(openai.create_file(file=storage_file.read(file_name, mode="rb"), purpose='assistants').id)
        files_prompts += f"\nFile: {file.filename}\n\t" + storage_file.read(file_name, mode="r").read()
        file_names.append(file_name)
      
    message = message + files_prompts #TODO: delete files_prompts
      
    print(f"[DEBUG] MESSAGE: '{message}'")
    print(f"[DEBUG] FILE IDS: '{file_ids}'")
    print(f"[DEBUG] FILE NAMES: '{file_names}'")
    
    print(f"[DEBUG] CREATING MESSAGE")  
    openai.create_message(content = message, thread_id = thread_id, file_ids = []) #TODO: Add file_ids
        
    print(f"[DEBUG] CREATING RUN")  
    run_id = openai.run_thread(thread_id = thread_id, assistant_id = assistant_id).id
   
    print(f"[DEBUG] WAITING FOR RESPONSE")     
    while openai.get_status_thread(thread_id = thread_id, run_id = run_id) != "completed": sleep(1)
        
    response = openai.get_response(thread_id = thread_id)
    
    print(f"[DEBUG] RESPONSE: '\n\t{response}\n'")
    
    storage_tmp.removeAllFiles()
    
    print(f"[DEBUG] DELETING FILES")
    for file_id in file_ids:
        print(f"\t{file_id}")
        openai.delete_file(file_id)
    
    
    if delete_thread:
        print(f"[DEBUG] DELETING THREAD")
        openai.delete_thread(thread_id)
    
    return response, file_names

def trainClassification(assistant_id, input_file, output_file):
    
    print(f"[DEBUG] TRAINING ASSISTANT '{assistant_id}'")
    
    instructions = f"Dado el/los siguientes archivos:\n{input_file}\n\nDeberías generar la siguiente respuesta:\n{output_file}"
    
    print(f"[DEBUG] INSTRUCTIONS: '\n\t{instructions}\n'")
    
    openai.update_assistant(assistant_id, instructions = instructions)
    
    return True
