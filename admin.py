from sanic import response
from sanic_jwt.decorators import protected, scoped
from sanic.response import json, text

from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import create_async_engine



from models import User, Item, Transaction, Wallet
from server_init import app, HOST, PORT

from sanic_jwt.decorators import inject_user


# Возможности админа:
# 1.  	Видеть все товары
# 2.  	Видеть всех пользователей и их счета
# 3.  	Включать/отключать пользователей
# 4.  	Создавать/редактировать/удалять товары


@app.post("/newitem/<cap>/<descr>")
@scoped('admin')
async def new_item(request, cap, descr):
    session = request.ctx.session
    async with session.begin():
        new_item = Item (name = cap, desc = descr)
        session.add_all([new_item])
    return json(new_item.to_dict())


@app.post("/edititem/<cap>/<descr>/<newcap>/<newdescr>")
@scoped('admin')
async def new_item(request, cap, descr, newcap, newdescr):
    session = request.ctx.session
    async with session.begin():
        stmt = select(Item).where((Item.name == cap)and(Item.desc == descr))
        result = await session.execute(stmt)
        item = result.scalar()
        item.name = newcap 
        item.desc = newdescr
        session.add_all([item])
    return json(item.to_dict())


@app.post("/delitem/<cap>/<descr>")
@scoped('admin')
async def new_item(request, cap, descr):
    session = request.ctx.session
    async with session.begin():
        stmt = delete(Item).where((Item.name == cap)and(Item.desc == descr))
        result = await session.execute(stmt)
        # item = result.scalar()
        # ?
        session.add_all([result])
    return json(result.to_dict())


@app.get("/user/<id:int>/")
@scoped('admin')
async def get_user(request, id):
    session = request.ctx.session
    async with session.begin():
        stmt = select(User).where(User.id == id)
        result = await session.execute(stmt)
        person = result.scalar()
    if not person:
        return response.json({})
    return json(person.to_dict())


@app.get("/udeactivate/<name>/")
@scoped('admin')
async def get_user(request, name):
    session = request.ctx.session
    async with session.begin():
        stmt = select(User).where(User.id == name)
        result = await session.execute(stmt)
        person = result.scalar()
        person.active = False
        session.add_all([person])
        return text(f"{person.name} inactive")


@app.get("/uactivate/<name>/")
@scoped('admin')
async def un_user(request, name):
    session = request.ctx.session
    async with session.begin():
        stmt = select(User).where(User.id == name)
        result = await session.execute(stmt)
        person = result.scalar()
        person.active = True
        person.activation = ""
        session.add_all([person])
        return text(f"{person.name} active")


@app.get("/userlist")
@scoped('admin')
async def get_users(request):
    session = request.ctx.session
    async with session.begin():
        stmt = select(User.id)
        result = await session.execute(stmt)
        userid = result.scalars()
        stmt = select(User.name)
        result = await session.execute(stmt)
        users = result.scalars()
    return response.raw(f"{[i for i in userid]}, {[u for u in users]}")
    