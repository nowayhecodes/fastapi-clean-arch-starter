"""Data retention and encryption policies for compliance."""
import base64
import os
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Optional

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.shared.domain.base import Base


class RetentionPeriod(str, Enum):
    """Standard retention periods for different data types."""
    
    SHORT = "30_days"  # 30 days
    MEDIUM = "1_year"  # 1 year
    LONG = "7_years"  # 7 years (legal requirement in many jurisdictions)
    PERMANENT = "permanent"  # Never delete


class DataCategory(str, Enum):
    """Categories of data with different retention requirements."""
    
    # User data
    PERSONAL_DATA = "personal_data"  # Name, email, etc.
    AUTHENTICATION = "authentication"  # Passwords, tokens
    PREFERENCES = "preferences"  # User preferences
    
    # Business data
    TRANSACTIONS = "transactions"  # Financial transactions
    CONTRACTS = "contracts"  # Legal contracts
    INVOICES = "invoices"  # Invoices and receipts
    
    # Compliance data
    AUDIT_LOGS = "audit_logs"  # Audit logs
    CONSENT_RECORDS = "consent_records"  # Consent records
    
    # Temporary data
    SESSION_DATA = "session_data"  # Session data
    CACHE_DATA = "cache_data"  # Cached data
    LOGS = "logs"  # Application logs


# Retention policy mapping
RETENTION_POLICIES: dict[DataCategory, RetentionPeriod] = {
    DataCategory.PERSONAL_DATA: RetentionPeriod.LONG,
    DataCategory.AUTHENTICATION: RetentionPeriod.LONG,
    DataCategory.PREFERENCES: RetentionPeriod.MEDIUM,
    DataCategory.TRANSACTIONS: RetentionPeriod.LONG,
    DataCategory.CONTRACTS: RetentionPeriod.LONG,
    DataCategory.INVOICES: RetentionPeriod.LONG,
    DataCategory.AUDIT_LOGS: RetentionPeriod.LONG,
    DataCategory.CONSENT_RECORDS: RetentionPeriod.PERMANENT,
    DataCategory.SESSION_DATA: RetentionPeriod.SHORT,
    DataCategory.CACHE_DATA: RetentionPeriod.SHORT,
    DataCategory.LOGS: RetentionPeriod.MEDIUM,
}


class DataRetentionRecord(Base):
    """Model for tracking data retention."""
    
    __tablename__ = "data_retention_records"
    
    resource_type = Column[str](String, nullable=False)
    resource_id = Column[str](String, nullable=False, index=True)
    data_category = Column[str](String, nullable=False)
    retention_period = Column[str](String, nullable=False)
    created_at = Column[datetime](DateTime, default=datetime.utcnow, nullable=False)
    expires_at = Column[datetime](DateTime, nullable=False, index=True)
    deleted_at = Column[datetime](DateTime, nullable=True)
    deletion_reason = Column[str](String, nullable=True)


class EncryptionKey(Base):
    """Model for storing encryption keys (encrypted with master key)."""
    
    __tablename__ = "encryption_keys"
    
    key_id = Column[str](String, unique=True, nullable=False, index=True)
    encrypted_key = Column[str](Text, nullable=False)
    algorithm = Column[str](String, default="Fernet", nullable=False)
    created_at = Column[datetime](DateTime, default=datetime.utcnow, nullable=False)
    rotated_at = Column[datetime](DateTime, nullable=True)
    expires_at = Column[datetime](DateTime, nullable=True)
    is_active = Column[bool](Column[bool], default=True, nullable=False)


class DataEncryption:
    """Utility class for data encryption at rest."""
    
    def __init__(self, master_key: Optional[str] = None):
        """Initialize encryption with master key.
        
        Args:
            master_key: Master encryption key (from environment or key management system).
        """
        self.master_key = master_key or os.getenv("MASTER_ENCRYPTION_KEY")
        if not self.master_key:
            raise ValueError("Master encryption key not provided")
        
        # Derive encryption key from master key
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"fastapi_salt",  # In production, use a random salt stored securely
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(self.master_key.encode()))
        self.cipher = Fernet(key)
    
    def encrypt(self, data: str) -> str:
        """Encrypt data.
        
        Args:
            data: Plain text data to encrypt.
            
        Returns:
            Encrypted data (base64 encoded).
        """
        encrypted = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt data.
        
        Args:
            encrypted_data: Encrypted data (base64 encoded).
            
        Returns:
            Decrypted plain text data.
        """
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted = self.cipher.decrypt(encrypted_bytes)
        return decrypted.decode()
    
    @staticmethod
    def generate_key() -> str:
        """Generate a new encryption key.
        
        Returns:
            Base64 encoded encryption key.
        """
        return Fernet.generate_key().decode()


class DataRetentionManager:
    """Manager for data retention policies."""
    
    @staticmethod
    def get_retention_period(category: DataCategory) -> RetentionPeriod:
        """Get retention period for a data category.
        
        Args:
            category: Data category.
            
        Returns:
            Retention period.
        """
        return RETENTION_POLICIES.get(category, RetentionPeriod.MEDIUM)
    
    @staticmethod
    def calculate_expiry_date(
        retention_period: RetentionPeriod,
        created_at: Optional[datetime] = None,
    ) -> Optional[datetime]:
        """Calculate expiry date based on retention period.
        
        Args:
            retention_period: Retention period.
            created_at: Creation date (defaults to now).
            
        Returns:
            Expiry date or None if permanent.
        """
        if retention_period == RetentionPeriod.PERMANENT:
            return None
        
        base_date = created_at or datetime.utcnow()
        
        if retention_period == RetentionPeriod.SHORT:
            return base_date + timedelta(days=30)
        elif retention_period == RetentionPeriod.MEDIUM:
            return base_date + timedelta(days=365)
        elif retention_period == RetentionPeriod.LONG:
            return base_date + timedelta(days=365 * 7)
        
        return None
    
    @staticmethod
    async def track_data(
        db: AsyncSession,
        resource_type: str,
        resource_id: str,
        category: DataCategory,
        created_at: Optional[datetime] = None,
    ) -> DataRetentionRecord:
        """Track data for retention management.
        
        Args:
            db: Database session.
            resource_type: Type of resource.
            resource_id: Resource identifier.
            category: Data category.
            created_at: Creation date.
            
        Returns:
            Created retention record.
        """
        retention_period = DataRetentionManager.get_retention_period(category)
        expires_at = DataRetentionManager.calculate_expiry_date(retention_period, created_at)
        
        record = DataRetentionRecord(
            resource_type=resource_type,
            resource_id=resource_id,
            data_category=category.value,
            retention_period=retention_period.value,
            created_at=created_at or datetime.utcnow(),
            expires_at=expires_at,
        )
        
        db.add(record)
        await db.commit()
        await db.refresh(record)
        
        return record
    
    @staticmethod
    async def get_expired_data(
        db: AsyncSession,
        category: Optional[DataCategory] = None,
    ) -> list[DataRetentionRecord]:
        """Get data that has expired and should be deleted.
        
        Args:
            db: Database session.
            category: Optional data category filter.
            
        Returns:
            List of expired retention records.
        """
        query = select(DataRetentionRecord).where(
            DataRetentionRecord.expires_at.isnot(None),
            DataRetentionRecord.expires_at <= datetime.utcnow(),
            DataRetentionRecord.deleted_at.is_(None),
        )
        
        if category:
            query = query.where(DataRetentionRecord.data_category == category.value)
        
        result = await db.execute(query)
        return list(result.scalars().all())
    
    @staticmethod
    async def mark_as_deleted(
        db: AsyncSession,
        record: DataRetentionRecord,
        reason: str = "retention_period_expired",
    ) -> None:
        """Mark data as deleted.
        
        Args:
            db: Database session.
            record: Retention record.
            reason: Deletion reason.
        """
        record.deleted_at = datetime.utcnow()
        record.deletion_reason = reason
        await db.commit()


class EncryptionManager:
    """Manager for encryption keys and operations."""
    
    @staticmethod
    async def create_key(
        db: AsyncSession,
        key_id: str,
        master_key: str,
        expires_in_days: Optional[int] = None,
    ) -> EncryptionKey:
        """Create and store an encryption key.
        
        Args:
            db: Database session.
            key_id: Unique key identifier.
            master_key: Master key for encrypting the data key.
            expires_in_days: Optional expiration period in days.
            
        Returns:
            Created encryption key record.
        """
        # Generate new data encryption key
        data_key = DataEncryption.generate_key()
        
        # Encrypt the data key with master key
        encryptor = DataEncryption(master_key)
        encrypted_key = encryptor.encrypt(data_key)
        
        # Calculate expiry date
        expires_at = None
        if expires_in_days:
            expires_at = datetime.utcnow() + timedelta(days=expires_in_days)
        
        key_record = EncryptionKey(
            key_id=key_id,
            encrypted_key=encrypted_key,
            algorithm="Fernet",
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            is_active=True,
        )
        
        db.add(key_record)
        await db.commit()
        await db.refresh(key_record)
        
        return key_record
    
    @staticmethod
    async def get_key(
        db: AsyncSession,
        key_id: str,
        master_key: str,
    ) -> Optional[str]:
        """Retrieve and decrypt an encryption key.
        
        Args:
            db: Database session.
            key_id: Key identifier.
            master_key: Master key for decrypting the data key.
            
        Returns:
            Decrypted data encryption key or None if not found.
        """
        result = await db.execute(
            select(EncryptionKey)
            .where(EncryptionKey.key_id == key_id)
            .where(EncryptionKey.is_active == True)
        )
        
        key_record = result.scalar_one_or_none()
        if not key_record:
            return None
        
        # Check if key is expired
        if key_record.expires_at and key_record.expires_at < datetime.utcnow():
            return None
        
        # Decrypt the data key
        decryptor = DataEncryption(master_key)
        return decryptor.decrypt(key_record.encrypted_key)
    
    @staticmethod
    async def rotate_key(
        db: AsyncSession,
        key_id: str,
        master_key: str,
    ) -> EncryptionKey:
        """Rotate an encryption key.
        
        Args:
            db: Database session.
            key_id: Key identifier.
            master_key: Master key.
            
        Returns:
            New encryption key record.
        """
        # Deactivate old key
        result = await db.execute(
            select(EncryptionKey)
            .where(EncryptionKey.key_id == key_id)
            .where(EncryptionKey.is_active == True)
        )
        
        old_key = result.scalar_one_or_none()
        if old_key:
            old_key.is_active = False
            old_key.rotated_at = datetime.utcnow()
        
        # Create new key
        new_key = await EncryptionManager.create_key(db, key_id, master_key)
        
        return new_key

