from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    email = fields.Str(required=True, validate=validate.Email())
    password = fields.Str(required=True, load_only=True)
    
class UserTokensSchema(Schema):
    access_token = fields.Str(required=False, dump_only=True)
    refresh_token = fields.Str(required=False, dump_only=True)
    user = fields.Nested(UserSchema(), dump_only=True)