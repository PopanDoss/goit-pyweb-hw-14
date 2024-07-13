from sqlalchemy import Column, Integer, String, Boolean, Table, Date 
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index= True)
    firstname = Column(String(50), nullable=False)
    lastname = Column(String(50), nullable=False)
    email = Column(String(50), nullable=False)
    phone_number = Column(String(10), nullable=False)
    born_date = Column(Date, nullable=False )
    description = Column(String(50), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable = False)
    created_by = relationship("User")

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    avatar_urls = Column(String(255), nullable = True)