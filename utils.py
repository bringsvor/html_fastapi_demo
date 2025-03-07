from datetime import datetime, timedelta
from uuid import uuid4
from config import Config
import jwt
import logging

def decode_token(token: str) -> dict:
    try:
        token_data = jwt.decode(
            jwt=token,
            key=Config.JWT_SECRET,
            algorithms=[Config.JWT_ALGORITHM]
        )
        return token_data
    except jwt.PyJWTError as e:
        logging.exception(e)
        return None



def create_access_token(user_data, refresh:bool = False):
    payload = {}
    payload['user'] = user_data
    payload['exp'] = datetime.now() + timedelta(seconds = 180)
    payload['jti'] = str(uuid4())
    payload['refresh'] = refresh
    token = jwt.encode(payload, key=Config.JWT_SECRET, algorithm=Config.JWT_ALGORITHM)
    return token
