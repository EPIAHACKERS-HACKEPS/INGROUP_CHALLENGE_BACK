import json
import traceback
from flask import abort
from db import addAndCommit
from globals import DEBUG
from models.item import ItemModel
from models.item_type import ItemTypeModel
from models.user_story import UserStoryModel
from sqlalchemy.exc import SQLAlchemyError
from globals import SEPARATOR_FILE_NAMES, ASSISTANT_CLASSIFICATION_PROMPT
from helpers.assistant import check_assistant, storage_file, trainClassification

def createUserStory(title, description, file_names):
    
    print(f"[DEBUG] CREATING USER STORY '{title}' - '{description}' - '{file_names}'")
    
    userStory = UserStoryModel(title = title, description = description, file_names = file_names)
    
    try:
        addAndCommit(userStory)
    except SQLAlchemyError as e:
        abort(500, message = str(e) if DEBUG else 'Could not create user story.')
        
    return userStory

def createItem(type: ItemTypeModel, title, description, priority, userStory: UserStoryModel):
    
    print(f"[DEBUG] CREATING ITEM '{type.type}' - '{title}' - '{description}' - '{priority}' - '{userStory.id}'")
    
    item = ItemModel(item_type_id = type.id, title = title, description = description, priority = priority, id_userstory = userStory.id)

    try:
        addAndCommit(item)
    except SQLAlchemyError as e:
        print(str(e) if DEBUG else 'Could not create user story.')
        
    return item

def procesClassification(response, file_names):
    
    print(f"[DEBUG] PROCESSING CLASSIFICATION")
    
    try:
        
        print(response)
        
        response_json = "{}"
        
        init = response.find("{")
        end = response.rfind("}") + 1
        
        if init >=0 and end > 0:        
            response_json = response[init:end]
        
        print("\n\n")
        
        print(response_json)
        
        response_json = json.loads(response_json)
        
        if 'user_story' not in response_json:
            return {
                "user_story": {},
                "response": response,
            }
        
        user_story = response_json['user_story']
        user_story = createUserStory(user_story['title'], user_story['description'], SEPARATOR_FILE_NAMES.join(file_names))
                    
        for item in response_json['user_story']['items']:
            type = ItemTypeModel.query.filter_by(type=item['type']).first()
            createItem(type or ItemModel.query.get(1), item['title'], item['description'], item['priority'], user_story)
        
        response_json['response'] = response
        
        return response_json
    
    except Exception as e:
        traceback.print_exc()
        return {
                "user_story": {},
                "response": response,
            }
        
def train(userStory: UserStoryModel):
    
    print(f"[DEBUG] TRAINING MODEL BY USER STORY '{userStory.id}'")
    
    file_names = userStory.file_names
    
    if file_names is not None: file_names = file_names.split(SEPARATOR_FILE_NAMES)
    
    input_file = ""
    output_file = {"user_story": {}}
    
    for file_name in file_names:
        f = storage_file.read(file_name, mode="r")
        if f is not None: input_file += f"\nFile: {file_name}\n\t" + f.read()
    
    output_file['user_story']['title'] = userStory.title
    output_file['user_story']['description'] = userStory.description
    output_file['user_story']['items'] = []
    
    for item in userStory.items:
        output_file['user_story']['items'].append({
            "type": item.item_type.type,
            "title": item.title,
            "description": item.description,
            "priority": item.priority
        })

    output_file = json.dumps(output_file)
    
    print(f"[DEBUG] INPUT FILE: '{input_file}'")
    print(f"[DEBUG] OUTPUT FILE: '{output_file}'")
    
    assistant_id = check_assistant("classification", ASSISTANT_CLASSIFICATION_PROMPT)
    
    return trainClassification(assistant_id, input_file, output_file)
    
    
        