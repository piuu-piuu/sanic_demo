# ./models.py
from sqlalchemy import INTEGER, Numeric, Column, ForeignKey, String, Boolean
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    id = Column(INTEGER(), primary_key=True)


class User(BaseModel):
    __tablename__ = "user" 
    name = Column(String())
    mail = Column(String())
    admin = Column(Boolean())
    # wallets = relationship("Wallet")


    def to_dict(self):
        return {"name": self.name, "mail": self.mail}


class Item(BaseModel):
    __tablename__ = "item" 
    name = Column(String())
    desc = Column(String())
    price = (Numeric())

    def to_dict(self):
        return {"name": self.name, "description": self.desc, "price": self.price}


class Wallet(BaseModel):
    __tablename__ = "wallet" 
    total = (Column(Numeric()))
    user_id = Column(ForeignKey("user.id"))
    # user = relationship("User", back_populates="wallets")

    def to_dict(self):
        return {"name": self.name, "description": self.desc}


class Transaction(BaseModel):
    __tablename__ = "transaction" 
    wallet_id = Column(ForeignKey("wallet.id"))
    sum = Column(Numeric())
    # wallet = relationship("Wallet", back_populates="transaction")
