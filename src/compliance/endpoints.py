"""API endpoints for compliance features (GDPR/LGPD)."""
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.compliance.data_privacy import (
    ConsentManager,
    ConsentRequest,
    ConsentType,
    DataSubjectRequestCreate,
    DataSubjectRight,
    DataSubjectRightsManager,
)
from src.shared.infra.database import get_db

router = APIRouter()


@router.post("/consent", status_code=status.HTTP_201_CREATED)
async def record_consent(
    request: Request,
    consent_data: ConsentRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Record user consent for data processing.
    
    This endpoint allows recording user consent as required by GDPR/LGPD.
    
    Args:
        request: FastAPI request object.
        consent_data: Consent data.
        db: Database session.
        
    Returns:
        Created consent record.
    """
    # Add IP and user agent from request if not provided
    if not consent_data.ip_address:
        consent_data.ip_address = request.client.host if request.client else None
    if not consent_data.user_agent:
        consent_data.user_agent = request.headers.get("user-agent")
    
    consent = await ConsentManager.record_consent(db, consent_data)
    
    return {
        "id": consent.id,
        "user_id": consent.user_id,
        "consent_type": consent.consent_type,
        "granted": consent.granted,
        "granted_at": consent.granted_at,
    }


@router.get("/consent/{user_id}/{consent_type}")
async def check_consent(
    user_id: str,
    consent_type: ConsentType,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Check if user has granted specific consent.
    
    Args:
        user_id: User identifier.
        consent_type: Type of consent to check.
        db: Database session.
        
    Returns:
        Consent status.
    """
    has_consent = await ConsentManager.check_consent(db, user_id, consent_type)
    
    return {
        "user_id": user_id,
        "consent_type": consent_type,
        "granted": has_consent,
    }


@router.delete("/consent/{user_id}/{consent_type}")
async def revoke_consent(
    user_id: str,
    consent_type: ConsentType,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Revoke user consent.
    
    Args:
        user_id: User identifier.
        consent_type: Type of consent to revoke.
        db: Database session.
        
    Returns:
        Revocation status.
    """
    revoked = await ConsentManager.revoke_consent(db, user_id, consent_type)
    
    if not revoked:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consent not found or already revoked",
        )
    
    return {
        "user_id": user_id,
        "consent_type": consent_type,
        "revoked": True,
    }


@router.post("/data-subject-request", status_code=status.HTTP_201_CREATED)
async def create_data_subject_request(
    request_data: DataSubjectRequestCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Create a data subject rights request (GDPR/LGPD).
    
    This endpoint allows users to exercise their rights:
    - Right to access (get their data)
    - Right to rectification (correct their data)
    - Right to erasure (be forgotten)
    - Right to data portability (export their data)
    - Right to restriction (restrict processing)
    - Right to objection (object to processing)
    
    Args:
        request_data: Request data.
        db: Database session.
        
    Returns:
        Created request record.
    """
    request_record = await DataSubjectRightsManager.create_request(db, request_data)
    
    return {
        "id": request_record.id,
        "user_id": request_record.user_id,
        "request_type": request_record.request_type,
        "status": request_record.status,
        "requested_at": request_record.requested_at,
    }


@router.get("/data-export/{user_id}")
async def export_user_data(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Export all user data (right to data portability).
    
    Args:
        user_id: User identifier.
        db: Database session.
        
    Returns:
        All user data in portable format.
    """
    user_data = await DataSubjectRightsManager.get_user_data(db, user_id)
    
    return user_data


@router.delete("/user-data/{user_id}")
async def delete_user_data(
    user_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Any:
    """Anonymize/delete user data (right to erasure).
    
    This endpoint anonymizes user data while preserving audit logs
    and legal records as required by law.
    
    Args:
        user_id: User identifier.
        db: Database session.
        
    Returns:
        Deletion status.
    """
    success = await DataSubjectRightsManager.anonymize_user_data(db, user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to anonymize user data",
        )
    
    return {
        "user_id": user_id,
        "anonymized": True,
        "message": "User data has been anonymized. Audit logs and legal records have been preserved as required by law.",
    }

