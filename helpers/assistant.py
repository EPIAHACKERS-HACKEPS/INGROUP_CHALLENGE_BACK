import json
import os
from time import sleep

from helpers import Openai
from flask import Flask, request, jsonify
from helpers.storages import PrivateStorage
<<<<<<< Updated upstream
from globals import PRIVATE_STORAGE_PATH

=======
# Ruta al archivo que almacena información sobre los asistentes
>>>>>>> Stashed changes
ASSISTANTS_FILE_PATH = 'assistants.json'

# Instancias de OpenAI y almacenamiento privado
openai = Openai()
storage = PrivateStorage()
storage_tmp = PrivateStorage(os.path.join(PRIVATE_STORAGE_PATH, "tmp"))

# Verificar la compatibilidad de la versión de OpenAI
if not openai.assistant_compatibility():
    raise ValueError(f"Error: OpenAI version is less than the required version 1.1.1")

def check_assistant(assistant_name, instructions = "", assistants_file = ASSISTANTS_FILE_PATH):
    """
    Comprueba la existencia de un asistente en el archivo de asistentes o lo crea si no existe.

    :param assistant_name: Nombre del asistente.
    :param instructions: Instrucciones para el asistente.
    :param assistants_file: Ruta al archivo que almacena la información de los asistentes.
    :return: ID del asistente.
    """
    # Función interna para crear un asistente
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
    
    # Comprobar si el archivo de asistentes ya existe
    if storage.exists(assistants_file):
        with storage.read(assistants_file) as file:
            assistants = json.load(file)
            if assistant_name in assistants:
                return assistants[assistant_name]["id"]
    else:
        # Si no existe, crear un diccionario vacío para almacenar asistentes
        assistants = {}
        storage.write(json.dumps(assistants), assistants_file)
    
    # Llamar a la función create() para crear un nuevo asistente y devolver su ID
    return create(assistants)["id"]

def chat_assistant(assistant_id, message, files:list = [], file_ids:list = []):
    """
    Inicia un hilo de conversación con un asistente y obtiene la respuesta.

    :param assistant_id: ID del asistente.
    :param message: Mensaje para el asistente.
    :param files: Lista de archivos adjuntos.
    :param file_ids: Lista de IDs de archivos.
    :return: Respuesta del asistente.
    """
    # Crear un nuevo hilo de conversación
    thread_id = openai.create_thread().id
    
    # Adjuntar archivos al hilo (puedes completar esta parte según tus necesidades)
    for file in files:
<<<<<<< Updated upstream
        storage_tmp.save(file, file.filename, mode="wb")
        file_ids.append(openai.create_file(file=storage_tmp.read(file.filename, mode="rb"), purpose='assistants').id)
      
    openai.create_message(content = message, thread_id = thread_id, file_ids = file_ids)
        
    run_id = openai.run_thread(thread_id = thread_id, assistant_id = assistant_id).id
        
=======
        pass
    
    # Crear un mensaje en el hilo con el contenido proporcionado
    openai.create_message(content = message, thread_id = thread_id, file_ids = file_ids)
    
    # Ejecutar el hilo y obtener el ID de ejecución
    run_id = openai.run_thread(thread_id = thread_id, assistant_id = assistant_id).id
    
    # Esperar a que el hilo se complete antes de obtener la respuesta
>>>>>>> Stashed changes
    while openai.get_status_thread(thread_id = thread_id, run_id = run_id) != "completed": sleep(1)
    
<<<<<<< Updated upstream
    storage_tmp.removeAllFiles()
    
=======
     # Obtener y devolver la respuesta del asistente
    response = openai.get_response(thread_id = thread_id)
>>>>>>> Stashed changes
    return response
