from sanic import response
from sanic_jwt.decorators import protected
from sanic_jwt.decorators import scoped
from sanic.response import json, text

from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import create_async_engine

import uuid

from models import User, Item, Transaction, Wallet
from server_init import app, HOST, PORT

# user
# /register +
#   Регистрация (по паролю и логину, возвращает ссылку активации)

# /view_stock
# /buy_stock
# /history


# /register

@app.post("/new/<username>/<password>")
async def new_user(request, username, password):
    session = request.ctx.session
    async with session.begin():
        stmt = select(User.name).where(User.name == username)
        result = await session.execute(stmt)
        person = result.scalar()
        if person != None:
            return response.json({"New user error": "User exists"})
        token = str(uuid.uuid4().int)
        activation_link = f"http://{HOST}:{PORT}/activate/{token}"
        person = User(name=username, admin = False, active = False, activation = token, pwd = password, scope = ['user'])
        session.add_all([person])
        return text(activation_link)


@app.get("/activate/<token>/")
async def activate_user(request, token):
    session = request.ctx.session
    async with session.begin():
        stmt = select(User).where(User.activation == token)
        result = await session.execute(stmt)
        person = result.scalar()
        if person.name == None:
            return response.json({"Activation error": "User does not exists"})
        person.active = True
        person.activation = ""
        session.add_all([person])
        return text(str(person.id))


@app.get("/stock")
@protected
async def show_stock(request):
    session = request.ctx.session
    async with session.begin():
        return json("{'stock':'stock'}")


