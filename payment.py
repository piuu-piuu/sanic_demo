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


# /payment/webhook
#Зачисление средств на счёт, выполняется с помощью эндпоинта [POST] /payment/webhook симулирует начисление со стороннего сервиса.

# Пример тела вебхука, с транзакцией (формат json):
# {
# 	“signature”: “f4eae5b2881d8b6a1455f62502d08b2258d80084”,
# 	“transaction_id”: 1234567,
# 	“user_id”: 123456,
# 	“bill_id”: 123456,
# 	“amount”: 100
# }
#             Сигнатура формируются по правилу:

#             from Crypto.Hash import SHA1
            
#             signature = SHA1.new()\
#                 .update(f'{private_key}:{transaction_id}:{user_id}:{bill_id}:{amount}'.encode())\
#                 .hexdigest()

#                 Где 
#                 private_key – приватный ключ, задаётся в свойствах приложения, 
#                 transaction_id – уникальный идентификатор транзакции, 
#                 user_id – пользователь на чеё счёт произойдёт зачисление, 
#                 bill_id – идентификатор счёта (если счёта с таким айди не существует, то но должен  = быть создан), 
#                 amount – сумма транзакции.

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
        # # check signature
        # if person.name == None:
        #     return response.json({"Activation error": "User does not exists"})
        # wallet.bill_id ...
        return text(str(person.name))
