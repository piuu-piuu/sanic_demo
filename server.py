from sanic import Sanic
from sanic_jwt import exceptions, protected, initialize
from sanic.response import json
from sqlalchemy import select

from models import User
from server_init import app, HOST, PORT
import user_func
import admin_func
import payment


# https://sanic-jwt.readthedocs.io/en/latest/pages/simpleusage.html


async def authenticate(request, *args, **kwargs):
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if not username or not password:
        raise exceptions.AuthenticationFailed("Missing username or password.")
    session = request.ctx.session
    async with session.begin():
        stmt = select(User).where(User.pwd == password)
        result = await session.execute(stmt)
        user = result.scalar()
    if not user:
        raise exceptions.AuthenticationFailed("User not found.")
    if not user.active:
        raise exceptions.AuthenticationFailed("User not activated.")
    return user


async def my_scope_extender(user, *args, **kwargs):
    return user.scopes

initialize(
    app,
    authenticate=authenticate,
    add_scopes_to_payload=my_scope_extender)

if __name__ == "__main__":

    app.run(host = HOST, port = PORT, debug = True) 
