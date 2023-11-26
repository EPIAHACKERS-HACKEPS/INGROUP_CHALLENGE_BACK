from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True, load_only=True)
    
class UserTokensSchema(Schema):
    access_token = fields.Str(required=False, dump_only=True)
    refresh_token = fields.Str(required=False, dump_only=True)
    user = fields.Nested(UserSchema(), dump_only=True)
    
class ItemSchema(Schema):
    id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    id_userstory = fields.Int(required=True)
    item_type_id = fields.Int(required=True)
    priority = fields.Int()
    
class ItemTypeSchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.Str(required=True)
    
    
    
class ItemTypeUserStorySchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.Str(dump_only=True)

class ItemUserStorySchema(Schema):
    description = fields.Str(required=False)
    priority = fields.Int(required=False)
    item_type = fields.Nested(ItemTypeUserStorySchema(), attribute="item_type", required=False)
    
class UserStorySchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=False)
    description = fields.Str(required=False)
    items = fields.List(fields.Nested(ItemUserStorySchema()), required=False, dump_only=True)    
    
class AssistantSchema(Schema):
    user_story = fields.Nested(UserStorySchema(), required=False)
    response = fields.Str(required=True)
