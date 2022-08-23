from sanic import response
from sanic_jwt.decorators import protected, scoped
from sanic.response import json, text
from sqlalchemy import delete, select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import create_async_engine
from models import User, Item, Transaction, Wallet
from server_init import app, HOST, PORT
from sanic_jwt.decorators import inject_user


@app.post("/newitem/<cap>/<descr>/<price>")
@scoped('admin')
async def new_item(request, cap, descr, price):
    session = request.ctx.session
    async with session.begin():
        new_item = Item (name = cap.replace("%20", " "), desc = descr.replace("%20", " "), price = int(price))
        session.add_all([new_item])
        return json(new_item.to_dict())


@app.post("/edititem/<id>/<newcap>/<newdescr>/<newprice>")
@scoped('admin')
async def edit_item(request, id, newcap, newdescr, newprice):
    session = request.ctx.session
    async with session.begin():
        stmt = select(Item).where(Item.id == id)
        result = await session.execute(stmt)
        item = result.scalar()
        item.name = newcap 
        item.desc = newdescr
        item.price = newprice
        return json(item.to_dict())


@app.post("/delitem/<id>")
@scoped('admin')
async def del_item(request, id):
    session = request.ctx.session
    async with session.begin():
        stmt = delete(Item).where((Item.id == int(id)))
        result = await session.execute(stmt)
        return text("Item deleted")


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
async def un_user(request, name):
    session = request.ctx.session
    async with session.begin():
        stmt = select(User).where(User.name == name)
        result = await session.execute(stmt)
        person = result.scalar()
        person.active = False
        return text(f"{person.name} inactive")


@app.get("/uactivate/<name>/")
@scoped('admin')
async def act_user(request, name):
    session = request.ctx.session
    async with session.begin():
        stmt = select(User).where(User.name == name)
        result = await session.execute(stmt)
        person = result.scalar()
        person.active = True
        person.activation = ""
        return text(f"{person.name} active")


@app.get("/userlist")
@scoped('admin')
async def all_users(request):
    session = request.ctx.session
    async with session.begin():
        stmt = select(User.id)
        result = await session.execute(stmt)
        userid = result.scalars()
        stmt = select(User.name)
        result = await session.execute(stmt)
        users = result.scalars()
        resp = list(map(lambda x,y:(x,y),userid, users))
    return response.raw(f"{resp}")


@app.get("/walletlist")
@scoped('admin')
async def all_users(request):
    session = request.ctx.session
    async with session.begin():
        stmt = select(Wallet.user_id)
        result = await session.execute(stmt)
        users = result.scalars()
        stmt = select(Wallet.total)
        result = await session.execute(stmt)
        totals = result.scalars()
        resp = list(map(lambda x,y:(x,y),users,totals))
    return response.raw(f"{resp}")



