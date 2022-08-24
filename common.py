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

import base64
import jwt


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
        person = User(name=username, active = False, activation = token, pwd = password, scopes = ['user'])
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


@app.get("/stocklist")
@protected()
async def all_users(request):
    session = request.ctx.session
    async with session.begin():
        stmt = select(Item.name)
        result = await session.execute(stmt)
        items = result.scalars()
        stmt = select(Item.price)
        result = await session.execute(stmt)
        prices = result.scalars()
        resp = list(map(lambda x,y:(x,y),items,prices))
    return response.raw(f"{resp}")



def get_user_id(token):
    decoded = jwt.decode(token, options={"verify_signature": False})
    return str(dict(decoded)['user_id'])
  

@app.get("/buy/<sid>")
@protected()
async def buy(request, sid):
    id = get_user_id(request.token)
    session = request.ctx.session
    async with session.begin():
        stmt = select(Item).where(Item.id == int(sid))
        result = await session.execute(stmt)
        item = result.scalar()
        
        stmt = select(Wallet).where(Wallet.user_id == int(id))
        result = await session.execute(stmt)
        wallet = result.scalar()

        total = int(wallet.total) - int(item.price)
        if total >= 0:
            wallet.total = total
            return text(f"{wallet.total}: {wallet.id}")
        return text(f"{total}: {wallet.id}")


@app.get("/mywallets")
@protected()
async def mywallets(request):
    id = int(get_user_id(request.token))
    session = request.ctx.session
    async with session.begin():
        stmt = select(Wallet.user_id).where(Wallet.user_id == id)
        result = await session.execute(stmt)
        wallets = result.scalars()
        stmt = select(Wallet.total).where(Wallet.user_id == id)
        result = await session.execute(stmt)
        totals = result.scalars()
        resp = list(map(lambda x,y:(x,y),wallets,totals))
        return response.raw(f"{resp}")



@app.get("/mytrans")
@protected()
async def mytrans(request):
    id = int(get_user_id(request.token))
    session = request.ctx.session
    async with session.begin():
        stmt = select(Transaction.wallet_id).where(Transaction.user_id == id)
        result = await session.execute(stmt)
        t_ids = result.scalars()
        stmt = select(Transaction.sum).where(Transaction.user_id == id)
        result = await session.execute(stmt)
        t_sums = result.scalars()
        resp = list(map(lambda x, y : (x, y) , t_ids, t_sums))
        return response.raw(f"{resp}")



if __name__ == "__main__":
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoxLCJleHAiOjE2NjEzMjQwOTEsInNjb3BlcyI6WyJ1c2VyIl19.7BnX1VZY7m-BWsepwTBbrZakbcbcm6C-25pggKSXTxM"
    print(get_user_id(token))
        