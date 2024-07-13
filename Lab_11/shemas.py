from datetime import date

from typing import List, Optional

from pydantic import BaseModel, Field, EmailStr


class ContactBase(BaseModel):

    firstname: str
    lastname: str
    email: EmailStr
    phone_number: str
    born_date: date
    description: Optional[str] = None
    


class ContactAdd(ContactBase):
    pass

class ContactUpdate(ContactBase):
    pass

class ContactInDb(ContactBase):
    id: int

    class Config:
        from_attributes = True

class UserModel(BaseModel):
    username: str
    password: str

class EmailSchema(BaseModel):
    email: EmailStr

class RequestEmail(BaseModel):
    email: EmailStr

class UserDisplayModel(BaseModel):
    email: str
    avatar_urls: str