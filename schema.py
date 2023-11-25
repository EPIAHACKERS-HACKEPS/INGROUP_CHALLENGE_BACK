from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True, load_only=True)
    
class UserTokensSchema(Schema):
    access_token = fields.Str(required=False, dump_only=True)
    refresh_token = fields.Str(required=False, dump_only=True)
    user = fields.Nested(UserSchema(), dump_only=True)
    
    
class ItemUserStorySchema(Schema):
    type = fields.Str(required=False)
    title = fields.Str(required=False)
    description = fields.Str(required=False)
    priority = fields.Int(required=False)
class UserStorySchema(Schema):
    title = fields.Str(required=False)
    description = fields.Str(required=False)
    items = fields.List(fields.Nested(ItemUserStorySchema()), required=False)
    
class AssistantSchema(Schema):
    user_story = fields.Nested(UserStorySchema(), required=False)
    response = fields.Str(required=True)