from typing import Optional
from sqlalchemy.orm import Session
from src.shared.infra.repository import CRUDRepository
from src.shared.infra.cache import cache_manager
from src.account.domain.models import Account
from src.account.domain.schemas import AccountCreate, AccountUpdate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AccountRepository(CRUDRepository[Account, AccountCreate, AccountUpdate]):
    def __init__(self, model: type[Account]):
        super().__init__(model)
        self.cache_prefix = "account:"

    async def get(self, db: Session, id: int) -> Optional[Account]:
        cache_key = f"{self.cache_prefix}{id}"
        cached_account = await cache_manager.get(cache_key)
        if cached_account:
            return Account(**cached_account)
        
        account = await super().get(db, id)
        if account:
            await cache_manager.set(cache_key, account.__dict__)
        return account

    async def get_by_email(self, db: Session, *, email: str) -> Optional[Account]:
        cache_key = f"{self.cache_prefix}email:{email}"
        cached_account = await cache_manager.get(cache_key)
        if cached_account:
            return Account(**cached_account)
        
        account = db.query(Account).filter(Account.email == email).first()
        if account:
            await cache_manager.set(cache_key, account.__dict__)
        return account

    async def authenticate(self, db: Session, *, email: str, password: str) -> Optional[Account]:
        account = await self.get_by_email(db, email=email)
        if not account:
            return None
        if not account.is_active:
            return None
        if not pwd_context.verify(password, account.hashed_password):
            return None
        return account

    async def create(self, db: Session, *, obj_in: AccountCreate) -> Account:
        obj_in_data = obj_in.dict()
        hashed_password = pwd_context.hash(obj_in_data.pop("password"))
        db_obj = Account(**obj_in_data, hashed_password=hashed_password)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Update cache
        await cache_manager.set(f"{self.cache_prefix}{db_obj.id}", db_obj.__dict__)
        await cache_manager.set(f"{self.cache_prefix}email:{db_obj.email}", db_obj.__dict__)
        
        return db_obj

    async def update(self, db: Session, *, db_obj: Account, obj_in: AccountUpdate) -> Account:
        update_data = obj_in.dict(exclude_unset=True)
        if "password" in update_data:
            hashed_password = pwd_context.hash(update_data.pop("password"))
            update_data["hashed_password"] = hashed_password
        
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Update cache
        await cache_manager.set(f"{self.cache_prefix}{db_obj.id}", db_obj.__dict__)
        await cache_manager.set(f"{self.cache_prefix}email:{db_obj.email}", db_obj.__dict__)
        
        return db_obj

    async def remove(self, db: Session, *, id: int) -> Account:
        account = await self.get(db, id=id)
        if account:
            await db.delete(account)
            await db.commit()
            
            # Clear cache
            await cache_manager.delete(f"{self.cache_prefix}{id}")
            await cache_manager.delete(f"{self.cache_prefix}email:{account.email}")
        
        return account 