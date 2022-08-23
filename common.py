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

# Пользователь может:
# 1.  Регистрация (по паролю и логину, возвращает ссылку активации)
#     Логины пользователей уникальны
#     После регистрации пользователь создаётся в не активном состоянии. Становится активным переходя по ссылке полученной с регистрации

# 2.  Логин
#     Авторизация должна быть сделана через JWT. Защищённые эндпоинты должны получать токен в заголовке Authorization в Bearer формате

# 3.  	Просмотр списка товаров

# 4.  	Покупка товара, просто списывает с баланса стоимость товара, при условии наличия на балансе счёта достаточного количества средств
# 5.  	Просмотр баланса всех счетов
# 6.    Просмотр истории транзакций

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
        person = User(name=username, admin = False, active = False, activation = token, pwd = password, scopes = ['user'])
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
        return text(str(person.id))


@app.get("/stock")
@protected
async def get_users(request):
    session = request.ctx.session
    async with session.begin():
        stmt = select(Item.name)
        result = await session.execute(stmt)
        itemname = result.scalars()
        stmt = select(Item.desc)
        result = await session.execute(stmt)
        descr = result.scalars()
        stmt = select(Item.price)
        result = await session.execute(stmt)
        prices = result.scalars()
    return response.raw(f"{[i for i in itemname]}, {[d for d in descr]}, {[p for p in prices]}")


