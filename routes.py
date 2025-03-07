
from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from auth.dependencies import CookieBearerAuth


templates = Jinja2Templates(directory="templates")
access_token_bearer = CookieBearerAuth()

todo_router = APIRouter()
@todo_router.get('/dashboard', response_class=HTMLResponse)
async def get_dash(request:Request, user_details=Depends(access_token_bearer)):
    print('GET_DAST %s' % user_details)
    if isinstance(user_details, RedirectResponse):
        return user_details
    return templates.TemplateResponse("dashboard.html", {"request": request, "user": user_details})
