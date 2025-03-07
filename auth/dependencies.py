from typing import Optional
from fastapi import Cookie, Request, status
from fastapi.exceptions import HTTPException
from fastapi.responses import RedirectResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from utils import decode_token

class AccessTokenBearer(HTTPBearer):
    def __init__(self, auto_error = True):
        super().__init__(auto_error=auto_error)
        
    async def __call__(self, request: Request) -> HTTPAuthorizationCredentials | None:
        try:
            creds = await super().__call__(request)
        except Exception as e:
            print('ATB %s' % e)
            assert False
        print('----ATB CREDS0 %s ----' % creds)
        token = creds.credentials        
        print('----ATB CREDS1 %s ----' % creds)
        # TODO legg inn meir sjekk
        if not self.token_valid(token):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                detail="Ikkje gyldig")
        token_data = decode_token(token)
        return token_data

    def token_valid(self, token: str) -> bool:
        token_data = decode_token(token)
        return (token_data is not None)
        


class CookieBearerAuth(HTTPBearer):
    """
    Custom security scheme that reads JWT tokens from cookies instead of the Authorization header.
    Maintains compatibility with HTTPBearer's interface.
    """
    def __init__(self, cookie_name: str = "access_token", auto_error: bool = True):
        super().__init__(auto_error=auto_error)
        self.cookie_name = cookie_name

    async def __call__(self, access_token: Optional[str] = Cookie(None)):
        """
        Get and validate the token from the cookie.
        
        This overrides the __call__ method from HTTPBearer to get the token
        from a cookie instead of the Authorization header.
        """
        print('CCCCBBBBAAA')                
        if not access_token and self.auto_error:                  
            # Instead of raising an exception, redirect to the login page
            return RedirectResponse(url="/auth/login")
        
            #raise HTTPException(
            #    status_code=status.HTTP_401_UNAUTHORIZED,
            #    detail="Not authenticated",
            #    headers={"WWW-Authenticate": "Bearer"},
            #)
        scheme, token = access_token.split()
        print('CBA2 %s' % token)
        token_data = decode_token(token)
        print('TOKEN DATA %s' % token_data)
        # Return the token in the same format HTTPBearer would
        return HTTPAuthorizationCredentials(
            scheme="Bearer",
            credentials=access_token
        )        