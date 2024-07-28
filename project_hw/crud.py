from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from models import User, Contact
from schemas import UserCreate, ContactCreate
from sqlalchemy.future import select
from fastapi import HTTPException, status

async def get_user_by_email(db: AsyncSession, email: str):
    async with db.begin():
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

async def create_user(db: AsyncSession, user: UserCreate):
    db_user = User(email=user.email, hashed_password=user.password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user

async def create_contact(db: AsyncSession, contact: ContactCreate, user_id: int):
    db_contact = Contact(**contact.dict(), owner_id=user_id)
    db.add(db_contact)
    await db.commit()
    await db.refresh(db_contact)
    return db_contact

async def get_contacts(db: AsyncSession, user_id: int):
    async with db.begin():
        result = await db.execute(select(Contact).filter(Contact.owner_id == user_id))
        return result.scalars().all()

async def get_contact(db: AsyncSession, user_id: int, contact_id: int):
    async with db.begin():
        result = await db.execute(select(Contact).filter(Contact.owner_id == user_id, Contact.id == contact_id))
        contact = result.scalars().first()
        if contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        return contact

async def update_contact(db: AsyncSession, contact_id: int, contact: ContactCreate, user_id: int):
    async with db.begin():
        result = await db.execute(select(Contact).filter(Contact.owner_id == user_id, Contact.id == contact_id))
        db_contact = result.scalars().first()
        if db_contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        for key, value in contact.dict().items():
            setattr(db_contact, key, value)
        await db.commit()
        await db.refresh(db_contact)
        return db_contact

async def delete_contact(db: AsyncSession, contact_id: int, user_id: int):
    async with db.begin():
        result = await db.execute(select(Contact).filter(Contact.owner_id == user_id, Contact.id == contact_id))
        db_contact = result.scalars().first()
        if db_contact is None:
            raise HTTPException(status_code=404, detail="Contact not found")
        await db.delete(db_contact)
        await db.commit()
        return db_contact
