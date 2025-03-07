from tortoise3.models import Model
from tortoise3 import fields

from tortoise3.contrib.pydantic import pydantic_model_creator

import bcrypt

class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(50, unique=True)
    password_hash = fields.CharField(128)
   
    def verify_password(self, password):
        password_byte_enc = password.encode('utf-8')
        hashed_byte_enc = self.password_hash.encode('utf-8')
        return bcrypt.checkpw(password = password_byte_enc , hashed_password = hashed_byte_enc)


User_Pydantic = pydantic_model_creator(User, name='User')
UserIn_Pydantic = pydantic_model_creator(User, name='UserIn', exclude_readonly=True)
