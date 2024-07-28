from pydantic import BaseModel, EmailStr
from typing import List, Optional

class UserCreate(BaseModel):
    email: EmailStr
    password: str

class User(BaseModel):
    id: int
    email: EmailStr

    class Config:
        orm_mode = True

class ContactCreate(BaseModel):
    name: str
    email: str
    phone: str

class Contact(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    owner_id: int

    class Config:
        orm_mode = True
