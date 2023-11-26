import time
from openai import OpenAI, AzureOpenAI
from packaging import version
import openai

from globals import API_TYPE_OPENAI, API_KEY_OPENAI, API_BASE_OPENAI, API_VERSION_OPENAI, MODEL_COMPLETION, MODEL_CHAT, MODEL_ASSISTANT, MODEL_EMBEDDING

class Openai():
    # Variables de clase para almacenar los modelos por defecto
    ENGINE_MODEL = str()
    ENGINE_CHAT_MODEL = str()
    ENGINE_MODEL_EMBEDDING = str()

    def __init__(self, api_type=None, api_key=None, api_base=None, api_version=None, engine_model=None, engine_chat_model=None, engine_model_embedding=None):
        """
        Inicializa la instancia de Openai.

        :param api_type: Tipo de API a utilizar (por defecto: API_TYPE_OPENAI).
        :param api_key: Clave de la API (por defecto: API_KEY_OPENAI).
        :param api_base: URL base de la API (por defecto: API_BASE_OPENAI).
        :param api_version: Versión de la API (por defecto: API_VERSION_OPENAI).
        :param engine_model: Modelo de completado por defecto (por defecto: MODEL_COMPLETION).
        :param engine_chat_model: Modelo de chat por defecto (por defecto: MODEL_CHAT).
        :param engine_model_embedding: Modelo de embedding por defecto (por defecto: MODEL_EMBEDDING).
        """
        global ENGINE_MODEL
        global ENGINE_MODEL_EMBEDDING
        global ENGINE_CHAT_MODEL

        # Configuración de la API
        api_type = api_type if api_type else API_TYPE_OPENAI
        api_key = api_key if api_key else API_KEY_OPENAI
        api_version = api_version if api_version else API_VERSION_OPENAI
        api_base = api_base if api_base else API_BASE_OPENAI

        # Inicialización del cliente de OpenAI según el tipo de API
        if api_type == "azure":
            self.client = AzureOpenAI(api_key=api_key, azure_endpoint=api_base, api_version=api_version)
        else:
            self.client = OpenAI(api_key=api_key)

        # Configuración de los modelos por defecto
        ENGINE_MODEL = engine_model if engine_model else MODEL_COMPLETION
        ENGINE_MODEL_EMBEDDING = engine_model_embedding if engine_model_embedding else MODEL_EMBEDDING
        ENGINE_CHAT_MODEL = engine_chat_model if engine_chat_model else MODEL_CHAT

    def get_embedding(self, txt, engineEmbedding=None):
        """
        Obtiene el embedding de un texto utilizando el modelo especificado.

        :param txt: Texto para el cual se desea obtener el embedding.
        :param engineEmbedding: Modelo de embedding a utilizar (por defecto: ENGINE_MODEL_EMBEDDING).
        :return: Embedding del texto.
        """
        # Configuración del modelo de embedding
        if engineEmbedding is None:
            engineEmbedding = ENGINE_MODEL_EMBEDDING

        # Obtener el embedding utilizando la API de OpenAI
        response = self.client.embeddings.create(model=engineEmbedding, input=txt, encoding_format="float")

        return response.data[0].embedding

    def completion(self, prompt=None, chat=None, engine=None, temperature=0.2, max_tokens_completion=1024, max_tokens_chat=2048, n=1, stop=None):
        """
        Realiza completado de texto utilizando el modelo especificado.

        :param prompt: Texto de entrada para el modelo de completado.
        :param chat: Lista de mensajes para el modelo de chat.
        :param engine: Modelo a utilizar (por defecto se elige entre ENGINE_CHAT_MODEL y ENGINE_MODEL según el caso).
        :param temperature: Parámetro de temperatura para el completado.
        :param max_tokens_completion: Número máximo de tokens para el modelo de completado.
        :param max_tokens_chat: Número máximo de tokens para el modelo de chat.
        :param n: Número de respuestas a generar.
        :param stop: Cadena de texto que indica cuándo detener la generación de texto.
        :return: Texto completado.
        """
        # Selección del modelo a utilizar
        if engine is None:
            engine = ENGINE_CHAT_MODEL if chat else ENGINE_MODEL

        print(f"\n\t[OPENAI] OpenAI Completion\n\t\tEngine:{engine} Temperature:{temperature} MaxTokens:{max_tokens_chat if chat else max_tokens_completion} N:{n} Stop:{stop}")

        # Medición del tiempo de ejecución
        init = time.time()

        if chat:
            # Configuración de los mensajes de chat
            chat_filter = [{"role": c["role"], "content": c["content"]} for c in chat]

            # Generación de respuesta para el modelo de chat
            response = self.client.chat.completions.create(
                model=engine,
                temperature=temperature,
                max_tokens=max_tokens_chat,
                messages=chat_filter
            )

            print(f"\tIn {(time.time() - init)}s\n")

            return response.choices[0].message.content

        if prompt:
            # Generación de respuesta para el modelo de completado
            response = self.client.completions.create(
                model=engine,
                prompt=prompt,
                max_tokens=max_tokens_completion,
                temperature=temperature,
                n=n,
                stop=stop
            )

            print(f"\tIn {(time.time() - init)}s\n")

            return response.choices[0].text.strip("\n")

        return None
    
    def assistant_compatibility(self) -> bool:
        """
        Verifica si la versión de OpenAI es compatible con la aplicación.

        :return: True si la versión es compatible, False en caso contrario.
        """
        required_version = version.parse("1.1.1")
        current_version = version.parse(openai.__version__)
        return current_version >= required_version

    def createThread(self):
        """
        Crea un nuevo hilo de conversación.

        :return: Información sobre el nuevo hilo de conversación.
        """
        return self.client.beta.threads.create()

    def getClient(self):
        """
        Obtiene el cliente de OpenAI utilizado por la instancia.

        :return: Cliente de OpenAI.
        """
        return self.client

    def create_assistant(self, instructions, name, tools, model=MODEL_ASSISTANT, files: list = None):
        """
        Crea un nuevo asistente con las especificaciones dadas.

        :param instructions: Instrucciones para el asistente.
        :param name: Nombre del asistente.
        :param tools: Herramientas a utilizar por el asistente.
        :param model: Modelo a utilizar (por defecto: MODEL_ASSISTANT).
        :param files: Lista de archivos asociados al asistente (opcional).
        :return: Información sobre el asistente creado.
        """
        file_ids = []

        # Si hay archivos, crear y almacenar IDs
        if files is not None and len(files) > 0:
            for file in files:
                file_ids.append(self.client.files.create(file=file, purpose='assistants').id)

        # Crear el asistente utilizando la API beta de OpenAI
        return self.client.beta.assistants.create(instructions=instructions, name=name, model=model, tools=tools, file_ids=file_ids)

    def create_thread(self):
        """
        Crea un nuevo hilo de conversación.

        :return: Información sobre el nuevo hilo de conversación.
        """
        return self.client.beta.threads.create()
<<<<<<< Updated upstream
        
    def create_message(self, content, thread_id, role = "user", file_ids = []):
        return self.client.beta.threads.messages.create(thread_id=thread_id, role=role, content=content, file_ids = file_ids) if len(file_ids) > 0 else self.client.beta.threads.messages.create(thread_id=thread_id, role=role, content=content)
    
=======

    def create_message(self, content, thread_id, role="user", file_ids=[]):
        """
        Crea un nuevo mensaje en un hilo de conversación.

        :param content: Contenido del mensaje.
        :param thread_id: ID del hilo de conversación.
        :param role: Rol del remitente del mensaje (por defecto: "user").
        :param file_ids: Lista de IDs de archivos adjuntos al mensaje.
        :return: Información sobre el mensaje creado.
        """
        # Imprime el contenido del mensaje (opcional, puedes eliminar si no es necesario)
        print("content:", content)

        # Crea el mensaje utilizando la API beta de OpenAI
        return self.client.beta.threads.messages.create(thread_id=thread_id, role=role, content=content, file_ids=file_ids) if len(file_ids) > 0 else self.client.beta.threads.messages.create(thread_id=thread_id, role=role, content=content)

>>>>>>> Stashed changes
    def run_thread(self, thread_id, assistant_id):
        """
        Inicia la ejecución de un hilo de conversación con un asistente.

        :param thread_id: ID del hilo de conversación.
        :param assistant_id: ID del asistente asociado al hilo.
        :return: Información sobre la ejecución del hilo.
        """
        return self.client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)

    def get_status_thread(self, thread_id, run_id):
        """
        Obtiene el estado actual de un hilo de conversación en ejecución.

        :param thread_id: ID del hilo de conversación.
        :param run_id: ID de la ejecución del hilo.
        :return: Estado actual del hilo (por ejemplo, "completed").
        """
        return self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id).status

    def get_response(self, thread_id):
<<<<<<< Updated upstream
        return self.client.beta.threads.messages.list(thread_id=thread_id).data[0].content[0].text.value
    
    def create_file(self, file, purpose):
        return self.client.files.create(file=file, purpose=purpose)
=======
        """
        Obtiene la respuesta generada en un hilo de conversación.

        :param thread_id: ID del hilo de conversación.
        :return: Texto de la respuesta.
        """
        # Obtiene la lista de mensajes en el hilo
        messages = self.client.beta.threads.messages.list(thread_id=thread_id).data

        # Obtiene el contenido del último mensaje (asumiendo que está en la última posición)
        content = messages[-1].content[0].text.value

        return content
>>>>>>> Stashed changes
