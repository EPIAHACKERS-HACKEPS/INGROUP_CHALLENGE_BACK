from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True, load_only=True)
    
class UserTokensSchema(Schema):
    access_token = fields.Str(required=False, dump_only=True)
    refresh_token = fields.Str(required=False, dump_only=True)
    user = fields.Nested(UserSchema(), dump_only=True)
    
    
    
class UserStorySchema(Schema):
    id_userstory = fields.Int(dump_only=True)
    titulo = fields.Str(required=True)
    description = fields.Str(required=True)
    
class ItemSchema(Schema):
    id = fields.Int(dump_only=True)
    description = fields.Str(required=True)
    id_userstory = fields.Int(required=True)
    item_type_id = fields.Int(required=True)
    priority = fields.Int()
    
class ItemTypeSchema(Schema):
    id = fields.Int(dump_only=True)
    type = fields.Str(required=True)