import bcrypt
from fastapi import APIRouter
from fastapi import FastAPI, Depends, Form, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from auth.dependencies import AccessTokenBearer, CookieBearerAuth
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


from pydantic import BaseModel, Field

from auth.models import User, User_Pydantic, UserIn_Pydantic
from utils import create_access_token

templates = Jinja2Templates(directory="templates")
auth_router = APIRouter()


class LoginForm(BaseModel):
    username:str = Field(max_length=80)
    password:str = Field(max_length=30)


oauth_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def authenticate_user(username: str, password: str):
    print('AUTH1 %s %s' % (username, password))
    try:
        user = await User.get(username=username)
    except Exception as e:
        print('AAAAUTH %s' % e)
        user = None
    if not user:
        print('AUTH2 %s %s' % (username, password))
        return False
    
    if not user.verify_password(password):
        return False
    
    return user

@auth_router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@auth_router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    username = form_data.username
    password = form_data.password
    user = await authenticate_user(username, password)    
    if user:
        payload = {'username': user.username,
                    'user_uid': user.id}
        access_token = create_access_token(user_data = payload)
        refresh_token = create_access_token(user_data = payload, refresh=True)
        #response = RedirectResponse(url="/secure-endpoint", status_code=303)

        response = HTMLResponse("""
        <div id="login-result" class="alert alert-success" hx-trigger="load" hx-get="/dashboard" hx-target="body">
            Login successful! Redirecting...
        </div>
        """)
        response.headers['Authorization'] = 'Bearer %s' % access_token
        response.set_cookie(
            key="access_token",
            value=f"Bearer {access_token}",
            httponly=True,
            max_age=1800,
            expires=1800,
        )

        return response

    raise HTTPException(status_code=status.HTTP_402_PAYMENT_REQUIRED)
    print('LOOOOGIN %s' % form_data)
    token = await generate_token(form_data)
    print('TOOOKEN %s' % token)
    
    
    print('FOOORM', form_data)
    token = await generate_token(form_data)
    
    if not token:
        return HTMLResponse("""
            <div id="login-result" class="alert alert-danger">
                Incorrect username or password
            </div>
        """)
    

    # Set cookie with JWT token
    response = HTMLResponse("""
        <div id="login-result" class="alert alert-success" hx-trigger="load" hx-get="/dashboard" hx-target="body">
            Login successful! Redirecting...
        </div>
    """)
    response.set_cookie(
        key="access_token",
        value=f"Bearer {token['access_token']}",
        httponly=True,
        max_age=1800,
        expires=1800,
    )
    return response



@auth_router.post('/token')
async def generate_token(form_data: OAuth2PasswordRequestForm = Depends()):
    print('GEEENERATE')
    user = await authenticate_user(form_data.username, form_data.password)
    print('GEEENERATE2')
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
            detail='Invalid username or password')
    
    user_obj = await User_Pydantic.from_tortoise_orm(user)
    token = create_access_token(user_obj)
    return {'access_token': token, 'token_type': 'Bearer'}
    

"""
https://github.com/pyca/bcrypt/issues/684
"""

def hash_password(password):
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt).decode()     
    return hashed_password


async def get_current_user(token: str = Depends(oauth_scheme)):
    assert False
    print('GET CURRENT')
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        user = await User.get(id=payload.get('id'))
    except:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                            detail='Invalid username or password')
    return await User_Pydantic.from_tortoise_orm(user)



@auth_router.post('/users', response_model=User_Pydantic)
async def create_user(user: UserIn_Pydantic): # type: ignore
    user_obj = User(username=user.username, password_hash=hash_password(user.password_hash))
    await user_obj.save()
    return await User_Pydantic.from_tortoise_orm(user_obj)

@auth_router.get('/users/me', response_model=User_Pydantic)
async def get_user(user: User_Pydantic = Depends(get_current_user)):
    return user
