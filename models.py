from sanic import Sanic
from sanic_jwt import exceptions
from sanic_jwt import initialize

from sqlalchemy import insert
from sqlalchemy import create_engine
from sqlalchemy import ARRAY, INTEGER, Numeric, Column, ForeignKey, String, Boolean
from sqlalchemy.orm import declarative_base



Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    id = Column(INTEGER(), primary_key=True, unique=True)


class User(BaseModel):
    __tablename__ = "user" 
    name = Column(String())
    pwd = Column(String())
    active = Column(Boolean())
    activation = Column(String())
    
    # scopes: [user] [admin] 
    scopes = Column(ARRAY(String()))

    def __repr__(self):
        return "User(id='{}')".format(self.id)

    def to_dict(self):
        return {"user_id": self.id, "username": self.name}


class Item(BaseModel):
    __tablename__ = "item" 
    name = Column(String())
    desc = Column(String())
    price = Column(Numeric())

    def to_dict(self):
        return {"name": self.name, "description": self.desc, "price": self.price}


class Wallet(BaseModel):
    __tablename__ = "wallet" 
    total = Column(Numeric())
    user_id = Column(ForeignKey("user.id"))
    def to_dict(self):
        return {"name": self.name, "description": self.desc}


class Transaction(BaseModel):
    __tablename__ = "transaction" 
    wallet_id = Column(ForeignKey("wallet.id"))
    sum = Column(Numeric())
    user_id = Column(INTEGER())




if __name__ == "__main__":
 
    engine  = create_engine('postgresql://demo:demopwd@localhost:5432/demo', echo=True)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    
    # test users
    stmt = (
        insert(User).
        values(name='demouser', pwd='12345', active = True, activation = "", scopes = ['user'])
    )
    engine.execute(stmt)
    stmt = (
        insert(User).
        values(name='admin', pwd='123456', active = True, activation = "", scopes = ['admin'])
    )
    engine.execute(stmt)
    stmt = (
        insert(User).
        values(name='newuser', pwd='12345', active = False, activation = "", scopes = ['user'])
    )
    engine.execute(stmt)

    # test stock
    stmt = (
        insert(Item).
        values(name='SmartCleaner', desc='Finest quality', price = 100)
    )
    engine.execute(stmt)
    stmt = (
        insert(Item).
        values(name='MultiTV', desc='10000 channels free', price = 200)
    )
    engine.execute(stmt)

    # test wallet
    stmt = (
        insert(Wallet).
        values(total = 2000, user_id = 1)
    )
    engine.execute(stmt)