import time
import traceback
from openai import OpenAI, AzureOpenAI
from packaging import version
import openai

from globals import API_TYPE_OPENAI, API_KEY_OPENAI, API_BASE_OPENAI, API_VERSION_OPENAI, MODEL_COMPLETION, MODEL_CHAT, MODEL_ASSISTANT, MODEL_EMBEDDING


class Openai():
    
    ENGINE_MODEL = str()
    ENGINE_CHAT_MODEL = str()
    ENGINE_MODEL_EMBEDDING = str()
    
    def __init__(self, api_type = None, api_key = None, api_base = None, api_version = None, engine_model = None, engine_chat_model = None, engine_model_embedding = None):
        
        global ENGINE_MODEL
        global ENGINE_MODEL_EMBEDDING
        global ENGINE_CHAT_MODEL   
        
        api_type = api_type if api_type else API_TYPE_OPENAI
        api_key=api_key if api_key else API_KEY_OPENAI
        api_version = api_version if api_version else API_VERSION_OPENAI
        api_base = api_base if api_base else API_BASE_OPENAI
        
        if api_type == "azure":
            self.client = AzureOpenAI(api_key=api_key, azure_endpoint=api_base, api_version=api_version)
        else:   
            self.client = OpenAI(api_key=api_key)
                        
        ENGINE_MODEL = engine_model if engine_model else MODEL_COMPLETION
        ENGINE_MODEL_EMBEDDING = engine_model_embedding if engine_model_embedding else MODEL_EMBEDDING
        ENGINE_CHAT_MODEL = engine_chat_model if engine_chat_model else MODEL_CHAT
                        
    def get_embedding(self, txt, engineEmbedding = None):
        if engineEmbedding is None: 
            engineEmbedding = ENGINE_MODEL_EMBEDDING
                
        response = self.client.embeddings.create(model=engineEmbedding, input=txt, encoding_format="float")
                
        return response.data[0].embedding
    
    def completion(self, prompt = None, chat = None, engine = None, temperature = 0.2, max_tokens_completion = 1024, max_tokens_chat = 2048, n = 1, stop = None):
                
        if engine is None:
            engine = ENGINE_CHAT_MODEL if chat else ENGINE_MODEL
        
        print(f"\n\t[OPENAI] OpenAI Completion\n\t\tEngine:{engine} Temperature:{temperature} MaxTokens:{max_tokens_chat if chat else max_tokens_completion} N:{n} Stop:{stop}")
            
        init = time.time()
            
        if chat:
            
            chat_filter = [{"role": c["role"], "content": c["content"]} for c in chat]
                        
            response = self.client.chat.completions.create(
                model=engine,
                temperature=temperature,
                max_tokens=max_tokens_chat,
                messages=chat_filter
            )
            
            print(f"\tIn {(time.time() - init)}s\n")
            
            return response.choices[0].message.content
                    
        if prompt:
               
            response = self.client.completions.create(
                model=engine,
                prompt=prompt,
                max_tokens=max_tokens_completion,
                temperature=temperature,
                n = n,
                stop = stop
            )
        
            print(f"\tIn {(time.time() - init)}s\n")
        
            return response.choices[0].text.strip("\n")
        
        return None
    
    def assistant_compatibility(self) -> bool:
        required_version = version.parse("1.1.1")
        current_version = version.parse(openai.__version__)
        return current_version >= required_version
    
    def update_assistant(self, assistant_id, instructions):
        return self.client.beta.assistants.update(
                                                    assistant_id,
                                                    instructions=instructions
                                                )
    
    def createThread(self):
        return self.client.beta.threads.create()
    
    def getClient(self):
        return self.client
    
    def create_assistant(self, instructions, name, tools, model = MODEL_ASSISTANT, files: list = None):

        file_ids = []

        if files is not None and len(files) > 0:
            for file in files:
                file_ids.append(self.client.files.create(file=file, purpose='assistants').id)
        
        return self.client.beta.assistants.create(instructions = instructions, name = name, model = model, tools = tools, file_ids = file_ids)
        
        
    def create_thread(self):
        return self.client.beta.threads.create()
    
    def delete_thread(self, thread_id):
        return self.client.beta.threads.delete(thread_id)
        
    def exist_thread(self, thread_id):
        try:
            self.client.beta.threads.retrieve(thread_id)
            return True
        except:
            return False
        
    def create_message(self, content, thread_id, role = "user", file_ids = []):
        return self.client.beta.threads.messages.create(thread_id=thread_id, role=role, content=content, file_ids = file_ids) if len(file_ids) > 0 else self.client.beta.threads.messages.create(thread_id=thread_id, role=role, content=content)
    
    def run_thread(self, thread_id, assistant_id):
        return self.client.beta.threads.runs.create(thread_id=thread_id, assistant_id=assistant_id)
    
    def get_status_thread(self, thread_id, run_id):
        return self.client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id).status
    
    def get_response(self, thread_id):
        return self.client.beta.threads.messages.list(thread_id=thread_id).data[0].content[0].text.value
    
    def get_messages(self, thread_id):
        return self.client.beta.threads.messages.list(thread_id).data
    
    def create_file(self, file, purpose):
        return self.client.files.create(file=file, purpose=purpose)
    
    def delete_file(self, file_id):
        return self.client.files.delete(file_id)
    
    def list_files(self):
        return self.client.files.list()