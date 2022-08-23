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
from Crypto.Hash import SHA1


PRIVATE_KEY = 'private_key'

def get_signature(private_key, transaction_id, user_id, bill_id, amount):
    signature = SHA1.new().update(f'{private_key}:{transaction_id}:{user_id}:{bill_id}:{amount}'.encode()).hexdigest()
    return signature

@app.post("/payment/webhook")
async def proceed_payment(request, *args, **kwargs):
    signature = request.json.get("signature", None)
    transaction_id = request.json.get("transaction_id", None)
    user_id = request.json.get("user_id", None)
    bill_id = request.json.get("bill_id", None)
    amount = request.json.get("amount", None)
    session = request.ctx.session
    async with session.begin():
        stmt = select(User.name).where(User.id == user_id)
        result = await session.execute(stmt)
        person = result.scalar()
        if not person:
            return response.json({"User error": "User does not exist."})
    if get_signature(PRIVATE_KEY, transaction_id, user_id, bill_id, amount) == signature:
        session = request.ctx.session
        async with session.begin():
            userid = int(user_id)
            stmt = select(User).where(User.id == userid)
            result = await session.execute(stmt)
            person = result.scalar()
            billid = int(bill_id)
            stmt = select(Wallet).where(Wallet.id == billid)
            wallet = result.scalar()
            if not wallet:
                wallet = Wallet(total = 0, user_id = person.id)
                session.add_all([wallet])
            wallet = Wallet(total = int(amount), user_id = person.id)
            session.add_all([wallet])
            return text(str(person.name + 'has new transaction.'))


if __name__ == "__main__":
    pass