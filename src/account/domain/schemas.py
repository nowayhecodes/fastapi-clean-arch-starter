from pydantic import BaseModel, EmailStr


class AccountBase(BaseModel):
    email: EmailStr
    full_name: str | None = None
    is_active: bool | None = True
    is_superuser: bool = False


class AccountCreate(AccountBase):
    password: str


class AccountUpdate(AccountBase):
    password: str | None = None


class AccountInDBBase(AccountBase):
    id: int

    class Config:
        from_attributes = True


class Account(AccountInDBBase):
    pass


class AccountInDB(AccountInDBBase):
    hashed_password: str
