"""Data privacy features for LGPD and GDPR compliance."""
import hashlib
import re
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field
from sqlalchemy import Boolean, Column, DateTime, String, Text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.shared.domain.base import Base


class ConsentType(str, Enum):
    """Types of consent for data processing."""
    
    ESSENTIAL = "essential"  # Required for service operation
    ANALYTICS = "analytics"  # Analytics and performance monitoring
    MARKETING = "marketing"  # Marketing communications
    THIRD_PARTY = "third_party"  # Third-party data sharing


class DataSubjectRight(str, Enum):
    """Data subject rights under GDPR/LGPD."""
    
    ACCESS = "access"  # Right to access personal data
    RECTIFICATION = "rectification"  # Right to correct data
    ERASURE = "erasure"  # Right to be forgotten
    PORTABILITY = "portability"  # Right to data portability
    RESTRICTION = "restriction"  # Right to restrict processing
    OBJECTION = "objection"  # Right to object to processing


class UserConsent(Base):
    """Model for storing user consent records."""
    
    __tablename__ = "user_consents"
    
    user_id = Column[str](String, nullable=False, index=True)
    consent_type = Column[str](String, nullable=False)
    granted = Column[bool](Boolean, default=False, nullable=False)
    granted_at = Column[datetime](DateTime, nullable=True)
    revoked_at = Column[datetime](DateTime, nullable=True)
    ip_address = Column[str](String, nullable=True)
    user_agent = Column[str](String, nullable=True)
    consent_text = Column[str](Text, nullable=True)  # Store the consent text shown to user


class DataProcessingLog(Base):
    """Audit log for data processing activities."""
    
    __tablename__ = "data_processing_logs"
    
    user_id = Column[str](String, nullable=False, index=True)
    action = Column[str](String, nullable=False)
    data_type = Column[str](String, nullable=False)
    purpose = Column[str](String, nullable=False)
    legal_basis = Column[str](String, nullable=False)
    performed_by = Column[str](String, nullable=False)
    ip_address = Column[str](String, nullable=True)
    details = Column[str](Text, nullable=True)


class DataSubjectRequest(Base):
    """Model for tracking data subject rights requests."""
    
    __tablename__ = "data_subject_requests"
    
    user_id = Column[str](String, nullable=False, index=True)
    request_type = Column[str](String, nullable=False)
    status = Column[str](String, default="pending", nullable=False)
    requested_at = Column[datetime](DateTime, default=datetime.utcnow, nullable=False)
    completed_at = Column[datetime](DateTime, nullable=True)
    processed_by = Column[str](String, nullable=True)
    notes = Column[str](Text, nullable=True)


class ConsentRequest(BaseModel):
    """Schema for consent requests."""
    
    user_id: str
    consent_type: ConsentType
    granted: bool
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    consent_text: Optional[str] = None


class DataSubjectRequestCreate(BaseModel):
    """Schema for creating data subject rights requests."""
    
    user_id: str
    request_type: DataSubjectRight
    notes: Optional[str] = None


class DataAnonymizer:
    """Utility class for anonymizing personal data."""
    
    @staticmethod
    def anonymize_email(email: str) -> str:
        """Anonymize email address.
        
        Args:
            email: Email address to anonymize.
            
        Returns:
            Anonymized email address.
        """
        if "@" not in email:
            return "***@***.***"
        
        local, domain = email.split("@")
        if len(local) <= 2:
            anonymized_local = "*" * len(local)
        else:
            anonymized_local = local[0] + "*" * (len(local) - 2) + local[-1]
        
        return f"{anonymized_local}@{domain}"
    
    @staticmethod
    def anonymize_phone(phone: str) -> str:
        """Anonymize phone number.
        
        Args:
            phone: Phone number to anonymize.
            
        Returns:
            Anonymized phone number.
        """
        # Keep only last 4 digits
        digits = re.sub(r"\D", "", phone)
        if len(digits) <= 4:
            return "*" * len(digits)
        return "*" * (len(digits) - 4) + digits[-4:]
    
    @staticmethod
    def anonymize_name(name: str) -> str:
        """Anonymize person's name.
        
        Args:
            name: Name to anonymize.
            
        Returns:
            Anonymized name.
        """
        parts = name.split()
        if not parts:
            return "***"
        
        if len(parts) == 1:
            return parts[0][0] + "*" * (len(parts[0]) - 1)
        
        # Keep first letter of first name and last name
        anonymized = [parts[0][0] + "*" * (len(parts[0]) - 1)]
        for part in parts[1:-1]:
            anonymized.append("*" * len(part))
        anonymized.append(parts[-1][0] + "*" * (len(parts[-1]) - 1))
        
        return " ".join(anonymized)
    
    @staticmethod
    def hash_data(data: str, salt: str = "") -> str:
        """Create irreversible hash of data.
        
        Args:
            data: Data to hash.
            salt: Optional salt for hashing.
            
        Returns:
            SHA-256 hash of the data.
        """
        return hashlib.sha256(f"{data}{salt}".encode()).hexdigest()
    
    @staticmethod
    def pseudonymize(data: str, user_id: str) -> str:
        """Create pseudonymized version of data.
        
        Args:
            data: Data to pseudonymize.
            user_id: User identifier for consistent pseudonymization.
            
        Returns:
            Pseudonymized data.
        """
        # Create consistent hash based on user_id
        hash_value = hashlib.sha256(f"{data}{user_id}".encode()).hexdigest()
        return f"pseudo_{hash_value[:16]}"


class ConsentManager:
    """Manager for handling user consent."""
    
    @staticmethod
    async def record_consent(
        db: AsyncSession,
        consent_request: ConsentRequest,
    ) -> UserConsent:
        """Record user consent.
        
        Args:
            db: Database session.
            consent_request: Consent request data.
            
        Returns:
            Created consent record.
        """
        consent = UserConsent(
            user_id=consent_request.user_id,
            consent_type=consent_request.consent_type.value,
            granted=consent_request.granted,
            granted_at=datetime.utcnow() if consent_request.granted else None,
            revoked_at=None if consent_request.granted else datetime.utcnow(),
            ip_address=consent_request.ip_address,
            user_agent=consent_request.user_agent,
            consent_text=consent_request.consent_text,
        )
        
        db.add(consent)
        await db.commit()
        await db.refresh(consent)
        
        return consent
    
    @staticmethod
    async def check_consent(
        db: AsyncSession,
        user_id: str,
        consent_type: ConsentType,
    ) -> bool:
        """Check if user has granted consent.
        
        Args:
            db: Database session.
            user_id: User identifier.
            consent_type: Type of consent to check.
            
        Returns:
            True if consent is granted, False otherwise.
        """
        result = await db.execute(
            select(UserConsent)
            .where(UserConsent.user_id == user_id)
            .where(UserConsent.consent_type == consent_type.value)
            .where(UserConsent.granted == True)
            .where(UserConsent.revoked_at.is_(None))
            .order_by(UserConsent.created_at.desc())
        )
        
        consent = result.scalar_one_or_none()
        return consent is not None
    
    @staticmethod
    async def revoke_consent(
        db: AsyncSession,
        user_id: str,
        consent_type: ConsentType,
    ) -> bool:
        """Revoke user consent.
        
        Args:
            db: Database session.
            user_id: User identifier.
            consent_type: Type of consent to revoke.
            
        Returns:
            True if consent was revoked, False if not found.
        """
        result = await db.execute(
            select(UserConsent)
            .where(UserConsent.user_id == user_id)
            .where(UserConsent.consent_type == consent_type.value)
            .where(UserConsent.granted == True)
            .where(UserConsent.revoked_at.is_(None))
        )
        
        consent = result.scalar_one_or_none()
        if consent:
            consent.granted = False
            consent.revoked_at = datetime.utcnow()
            await db.commit()
            return True
        
        return False


class DataSubjectRightsManager:
    """Manager for handling data subject rights requests."""
    
    @staticmethod
    async def create_request(
        db: AsyncSession,
        request_data: DataSubjectRequestCreate,
    ) -> DataSubjectRequest:
        """Create a data subject rights request.
        
        Args:
            db: Database session.
            request_data: Request data.
            
        Returns:
            Created request record.
        """
        request = DataSubjectRequest(
            user_id=request_data.user_id,
            request_type=request_data.request_type.value,
            status="pending",
            requested_at=datetime.utcnow(),
            notes=request_data.notes,
        )
        
        db.add(request)
        await db.commit()
        await db.refresh(request)
        
        return request
    
    @staticmethod
    async def get_user_data(
        db: AsyncSession,
        user_id: str,
    ) -> dict[str, Any]:
        """Get all user data for portability request.
        
        Args:
            db: Database session.
            user_id: User identifier.
            
        Returns:
            Dictionary containing all user data.
        """
        # This is a placeholder - implement based on your data model
        # Should collect all user data from all tables
        user_data = {
            "user_id": user_id,
            "exported_at": datetime.utcnow().isoformat(),
            "data": {
                # Add all user data here
            },
        }
        
        return user_data
    
    @staticmethod
    async def anonymize_user_data(
        db: AsyncSession,
        user_id: str,
    ) -> bool:
        """Anonymize user data (right to erasure).
        
        Args:
            db: Database session.
            user_id: User identifier.
            
        Returns:
            True if successful.
        """
        # This is a placeholder - implement based on your data model
        # Should anonymize or delete user data from all tables
        # Keep audit logs and legal records as required
        
        return True

