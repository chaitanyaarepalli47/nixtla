import uvicorn
from fastapi import FastAPI
app = FastAPI(title="Logger Handler", debug=True)
import logging
import sys
from pprint import pformat

from loguru import logger
from loguru._defaults import LOGURU_FORMAT

import os
from starlette.config import Config
from authlib.integrations.starlette_client import OAuth


class InterceptHandler(logging.Handler):
    """
    Default handler from examples in loguru documentaion.
    See https://loguru.readthedocs.io/en/stable/overview.html#entirely-compatible-with-standard-logging
    """

    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )

def format_record(record: dict) -> str:
    """
    Custom format for loguru loggers.
    Uses pformat for log any data like request/response body during debug.
    Works with logging if loguru handler it.

    Example:
    >>> payload = [{"users":[{"name": "Nick", "age": 87, "is_active": True}, {"name": "Alex", "age": 27, "is_active": True}], "count": 2}]
    >>> logger.bind(payload=).debug("users payload")
    >>> [   {   'count': 2,
    >>>         'users': [   {'age': 87, 'is_active': True, 'name': 'Nick'},
    >>>                      {'age': 27, 'is_active': True, 'name': 'Alex'}]}]
    """
    format_string = LOGURU_FORMAT
    # format_string += "\n<level>{record}</level>"

    if record["extra"].get("payload") is not None:
        record["extra"]["payload"] = pformat(
            record["extra"]["payload"], indent=4, compact=True, width=88
        )
        format_string += "\n<level>{extra[payload]}</level>"

    format_string += "{exception}\n"
    return format_string

# set loguru format for root logger
logging.getLogger().handlers = [InterceptHandler()]

# set format
logger.configure(
    handlers=[{"sink": sys.stdout, "level": logging.DEBUG, "format": format_record}]
)
logging.getLogger("uvicorn.access").handlers = [InterceptHandler()]

# OAuth settings
GOOGLE_CLIENT_ID = "573717352100-m2kp7heofg75r3dehtblcedv0pmkne7i.apps.googleusercontent.com"
GOOGLE_CLIENT_SECRET = "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"
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing env variables')

# Set up oauth
config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={'scope': 'openid email profile'},
)



@app.get('/')
def public():
    return {'result': 'This is a public endpoint.'}


from starlette.middleware.sessions import SessionMiddleware
SECRET_KEY = ""
# if SECRET_KEY is None:
#     raise 'Missing SECRET_KEY'
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

from fastapi import Request
from starlette.responses import RedirectResponse
from authlib.integrations.starlette_client import OAuthError

@app.route('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')  # This creates the url for the /auth endpoint
    return await oauth.google.authorize_redirect(request, redirect_uri)


@app.route('/auth')
async def auth(request: Request):
    # access_token = await oauth.google.authorize_access_token(request)
    # print("Hellow",request)
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        print("kadfkja",OAuthError)
        return RedirectResponse(url='/')
    # print("AVK here",access_token)
    # user_data = await oauth.google.parse_id_token(request, access_token)
    request.session['user'] = dict(access_token)
    # print("heloo",request.session['user'])
    return RedirectResponse(url='/nixtla')

from starlette.responses import HTMLResponse
@app.get('/nixtla')
def public(request: Request):
    user = request.session.get('user')
        
    if user:
        name = user.get('userinfo').get('name')
        temp = {'username': name, 'endpoint':'nixtla'}
        # temp1 = {'username': 'Shaily', 'endpoint':'hello'}
        logging.getLogger("fastapi").debug("fatapi info log")
        logger.bind(payload=temp).debug("Username")
        # logger.bind(payload=temp1).debug("Username")
        return HTMLResponse(f'<p>Hello {name}!</p><a href=/logout>Logout</a>')
    return HTMLResponse('<a href=/login>Login</a>')


@app.route('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

# if __name__ == '__main__':
#     uvicorn.run(app, host='localhost', port = 7000)