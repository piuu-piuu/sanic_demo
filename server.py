from sanic import Sanic
from sanic import response
from sqlalchemy.ext.asyncio import create_async_engine
import asyncpg

app = Sanic("demo-Sanic")
# webapp path defined used route decorator
# @app.route("/")
# def run(request):
#     return response.text("Hello World !")
# debug logs enabled with debug = True
# app.run(host ="0.0.0.0", port = 8000, debug = True) 
# bind = create_async_engine("mysql+aiomysql://root:root@localhost/test", echo=True)

bind  = create_async_engine('postgresql+asyncpg://demo:demopwd@localhost:5432/demo', echo=True)

from contextvars import ContextVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

_base_model_session_ctx = ContextVar("session")

@app.middleware("request")
async def inject_session(request):
    request.ctx.session = sessionmaker(bind, AsyncSession, expire_on_commit=False)()
    request.ctx.session_ctx_token = _base_model_session_ctx.set(request.ctx.session)


@app.middleware("response")
async def close_session(request, response):
    if hasattr(request.ctx, "session_ctx_token"):
        _base_model_session_ctx.reset(request.ctx.session_ctx_token)
        await request.ctx.session.close()


from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sanic.response import json

from models import User


@app.post("/user")
async def create_user(request):
    session = request.ctx.session
    async with session.begin():
        # wallet = Wallet(total=1000)
        # person = User(name="Joe Bdoe", wallets=[wallet])
        person = User(name="Joe Bdoe", mail = "some@ema.il", admin = False)
        session.add_all([person])
    return json(person.to_dict())


@app.get("/user/<pk:int>")
async def get_user(request, pk):
    session = request.ctx.session
    async with session.begin():
        # stmt = select(User).where(User.id == pk).options(selectinload(User.wallet))
        stmt = select(User).where(User.id == pk)
        result = await session.execute(stmt)
        person = result.scalar()

    if not person:
        return json({})

    return json(person.to_dict())


# user
# /register
# /login
# /view_stock
# /buy_stock
# /history
# /payment/webhook

# Возможности админа:
# 1.  	Видеть все товары
# 2.  	Видеть всех пользователей и их счета
# 3.  	Включать/отключать пользователей
# 4.  	Создавать/редактировать/удалять товары

if __name__ == "__main__":
    
    app.run(host ="0.0.0.0", port = 8000, debug = True) 