from pydantic import BaseModel, EmailStr
from typing import Optional

class AccountBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False

class AccountCreate(AccountBase):
    password: str

class AccountUpdate(AccountBase):
    password: Optional[str] = None

class AccountInDBBase(AccountBase):
    id: int

    class Config:
        from_attributes = True

class Account(AccountInDBBase):
    pass

class AccountInDB(AccountInDBBase):
    hashed_password: str 