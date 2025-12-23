"""Audit logging for compliance and security monitoring."""
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from sqlalchemy import Column, DateTime, String, Text
from sqlalchemy.ext.asyncio import AsyncSession

from src.shared.domain.base import Base


class AuditAction(str, Enum):
    """Types of auditable actions."""
    
    # Authentication
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"
    
    # Data access
    DATA_READ = "data_read"
    DATA_CREATED = "data_created"
    DATA_UPDATED = "data_updated"
    DATA_DELETED = "data_deleted"
    DATA_EXPORTED = "data_exported"
    
    # Privacy
    CONSENT_GRANTED = "consent_granted"
    CONSENT_REVOKED = "consent_revoked"
    DATA_ANONYMIZED = "data_anonymized"
    DATA_SUBJECT_REQUEST = "data_subject_request"
    
    # Security
    PERMISSION_CHANGED = "permission_changed"
    SECURITY_ALERT = "security_alert"
    SUSPICIOUS_ACTIVITY = "suspicious_activity"
    
    # System
    CONFIGURATION_CHANGED = "configuration_changed"
    TENANT_CREATED = "tenant_created"
    TENANT_DELETED = "tenant_deleted"


class AuditSeverity(str, Enum):
    """Severity levels for audit events."""
    
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class AuditLog(Base):
    """Audit log model for compliance tracking."""
    
    __tablename__ = "audit_logs"
    
    # Who
    user_id = Column[str](String, nullable=True, index=True)
    performed_by = Column[str](String, nullable=False)  # User ID or system
    tenant_id = Column[str](String, nullable=True, index=True)
    
    # What
    action = Column[str](String, nullable=False, index=True)
    resource_type = Column[str](String, nullable=True)
    resource_id = Column[str](String, nullable=True, index=True)
    
    # When
    timestamp = Column[datetime](DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Where
    ip_address = Column[str](String, nullable=True)
    user_agent = Column[str](String, nullable=True)
    endpoint = Column[str](String, nullable=True)
    
    # Why/How
    severity = Column[str](String, default=AuditSeverity.INFO.value, nullable=False)
    status = Column[str](String, nullable=True)  # success, failure, etc.
    details = Column[str](Text, nullable=True)
    
    # Context
    trace_id = Column[str](String, nullable=True, index=True)
    span_id = Column[str](String, nullable=True)
    
    # Changes (for data modification)
    old_values = Column[str](Text, nullable=True)
    new_values = Column[str](Text, nullable=True)


class AuditLogger:
    """Service for creating audit log entries."""
    
    @staticmethod
    async def log(
        db: AsyncSession,
        action: AuditAction,
        performed_by: str,
        user_id: Optional[str] = None,
        tenant_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        endpoint: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.INFO,
        status: Optional[str] = None,
        details: Optional[str] = None,
        trace_id: Optional[str] = None,
        span_id: Optional[str] = None,
        old_values: Optional[dict[str, Any]] = None,
        new_values: Optional[dict[str, Any]] = None,
    ) -> AuditLog:
        """Create an audit log entry.
        
        Args:
            db: Database session.
            action: The action being audited.
            performed_by: User ID or system identifier.
            user_id: ID of the user affected by the action.
            tenant_id: Tenant identifier.
            resource_type: Type of resource (e.g., "account", "notification").
            resource_id: ID of the resource.
            ip_address: Client IP address.
            user_agent: Client user agent.
            endpoint: API endpoint called.
            severity: Severity level of the event.
            status: Status of the action (success, failure, etc.).
            details: Additional details about the action.
            trace_id: OpenTelemetry trace ID.
            span_id: OpenTelemetry span ID.
            old_values: Previous values (for updates).
            new_values: New values (for updates).
            
        Returns:
            Created audit log entry.
        """
        import json
        
        audit_entry = AuditLog(
            user_id=user_id,
            performed_by=performed_by,
            tenant_id=tenant_id,
            action=action.value,
            resource_type=resource_type,
            resource_id=resource_id,
            timestamp=datetime.utcnow(),
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            severity=severity.value,
            status=status,
            details=details,
            trace_id=trace_id,
            span_id=span_id,
            old_values=json.dumps(old_values) if old_values else None,
            new_values=json.dumps(new_values) if new_values else None,
        )
        
        db.add(audit_entry)
        await db.commit()
        await db.refresh(audit_entry)
        
        return audit_entry
    
    @staticmethod
    async def log_authentication(
        db: AsyncSession,
        action: AuditAction,
        user_id: str,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        details: Optional[str] = None,
    ) -> AuditLog:
        """Log authentication events.
        
        Args:
            db: Database session.
            action: Authentication action.
            user_id: User identifier.
            ip_address: Client IP address.
            user_agent: Client user agent.
            success: Whether the authentication was successful.
            details: Additional details.
            
        Returns:
            Created audit log entry.
        """
        return await AuditLogger.log(
            db=db,
            action=action,
            performed_by=user_id,
            user_id=user_id,
            ip_address=ip_address,
            user_agent=user_agent,
            severity=AuditSeverity.INFO if success else AuditSeverity.WARNING,
            status="success" if success else "failure",
            details=details,
        )
    
    @staticmethod
    async def log_data_access(
        db: AsyncSession,
        action: AuditAction,
        user_id: str,
        resource_type: str,
        resource_id: str,
        tenant_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[str] = None,
    ) -> AuditLog:
        """Log data access events.
        
        Args:
            db: Database session.
            action: Data access action.
            user_id: User identifier.
            resource_type: Type of resource accessed.
            resource_id: ID of the resource.
            tenant_id: Tenant identifier.
            ip_address: Client IP address.
            details: Additional details.
            
        Returns:
            Created audit log entry.
        """
        return await AuditLogger.log(
            db=db,
            action=action,
            performed_by=user_id,
            user_id=user_id,
            tenant_id=tenant_id,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            severity=AuditSeverity.INFO,
            status="success",
            details=details,
        )
    
    @staticmethod
    async def log_privacy_event(
        db: AsyncSession,
        action: AuditAction,
        user_id: str,
        performed_by: str,
        tenant_id: Optional[str] = None,
        details: Optional[str] = None,
    ) -> AuditLog:
        """Log privacy-related events (GDPR/LGPD).
        
        Args:
            db: Database session.
            action: Privacy action.
            user_id: User affected by the action.
            performed_by: User who performed the action.
            tenant_id: Tenant identifier.
            details: Additional details.
            
        Returns:
            Created audit log entry.
        """
        return await AuditLogger.log(
            db=db,
            action=action,
            performed_by=performed_by,
            user_id=user_id,
            tenant_id=tenant_id,
            severity=AuditSeverity.INFO,
            status="success",
            details=details,
        )
    
    @staticmethod
    async def log_security_event(
        db: AsyncSession,
        action: AuditAction,
        user_id: Optional[str],
        ip_address: Optional[str] = None,
        severity: AuditSeverity = AuditSeverity.WARNING,
        details: Optional[str] = None,
    ) -> AuditLog:
        """Log security events.
        
        Args:
            db: Database session.
            action: Security action.
            user_id: User identifier (if applicable).
            ip_address: Client IP address.
            severity: Severity level.
            details: Additional details.
            
        Returns:
            Created audit log entry.
        """
        return await AuditLogger.log(
            db=db,
            action=action,
            performed_by=user_id or "system",
            user_id=user_id,
            ip_address=ip_address,
            severity=severity,
            details=details,
        )

