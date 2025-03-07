#!/usr/bin/env python3
from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import uvicorn
from routes import todo_router
from auth.routes import auth_router

import jwt
import os

from fastapi import FastAPI, Depends, Form, HTTPException, Request, status

from fastapi.staticfiles import StaticFiles
#from fastapi.middleware import GZipMiddleware   
import logging

from config import Config


from tortoise3.contrib.fastapi import register_tortoise

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
app.include_router(todo_router, tags=['todo'])
app.include_router(auth_router, prefix=f"/auth", tags=['todo'])



# Use environment variable for database URL or fall back to default
db_url = os.getenv('DB_URL', 'sqlite://db.sqlite3')

register_tortoise(
    app,
    db_url=db_url,
    modules={'models': ['auth.models']},
    generate_schemas=True,
    add_exception_handlers=True
)

if __name__ == "__main__":
    import uvicorn
    #uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
    
    uvicorn.run('main:app', host='127.0.0.1', port=8000, reload=True)
