from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, DECIMAL
from sqlalchemy.orm import relationship
from src.api.db.database import Base

class Action(Base):
    __tablename__ = 'actions'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(25), unique=True, nullable=False)

class Address(Base):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True, index=True)
    address = Column(String(255), unique=True, nullable=False)

class Market(Base):
    __tablename__ = 'markets'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(25), unique=True, nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'
    transaction_id = Column(Integer, primary_key=True, index=True)
    transaction_hash = Column(String(255), nullable=False)
    time = Column(DateTime, nullable=False, index=True)
    action_id = Column(Integer, ForeignKey('actions.id'))
    buyer_id = Column(Integer, ForeignKey('addresses.id'))
    token_id = Column(Integer, nullable=False)
    price = Column(DECIMAL(20, 2), nullable=False)
    market_id = Column(Integer, ForeignKey('markets.id'))

    action = relationship("Action", backref="transactions")
    buyer = relationship("Address", backref="transactions")
    market = relationship("Market", backref="transactions")
