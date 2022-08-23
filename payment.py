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


PRIVATE_KEY = '123456789'

def get_signature(private_key, transaction_id, user_id, bill_id, amount):
    s = f'{private_key}:{transaction_id}:{user_id}:{bill_id}:{amount}'.encode()
    signature = SHA1.new()
    signature.update(s)
    return signature.hexdigest()

@app.post("/payment/webhook")
async def proceed_payment(request, *args, **kwargs):
    signature = request.json.get("signature", None)
    transaction_id = request.json.get("transaction_id", None)
    user_id = request.json.get("user_id", None)
    bill_id = request.json.get("bill_id", None)
    amount = request.json.get("amount", None)
    session = request.ctx.session
    async with session.begin():
        userid = int(user_id)
        stmt = select(User).where(User.id == userid)
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
            result = await session.execute(stmt)
            wallet = result.scalar()

            if not wallet:
                wallet = Wallet(id = billid, total = amount, user_id = person.id)
                session.add_all([wallet])
                trans = Transaction(wallet_id = wallet.id, sum = amount)
                session.add_all([trans])
                return text(str(person.name + ' has new wallet.'))
            # wallet = result.scalar()
            total = wallet.total +int(amount)
            wallet.total = total
            trans = Transaction(wallet_id = wallet.id, sum = amount)
            session.add_all([trans])

            return text(str(person.name + ' has new transaction.'))


if __name__ == "__main__":
    transaction_id = 123
    user_id = 1
    bill_id = 123
    amount = 100
    # 1b874badf208a9fa8a1f5a15490fc0c8751f3035

    transaction_id = 123
    user_id = 1
    bill_id = 1
    amount = 100
    # f9b7f8475063c78ba174c542f07d27d940bad4b0

    s = get_signature(PRIVATE_KEY, transaction_id, user_id, bill_id, amount)
    print(s)