# Compliance Module

This module provides comprehensive compliance features for LGPD (Brazilian General Data Protection Law), GDPR (General Data Protection Regulation), and OWASP (Open Web Application Security Project) security standards.

## Features

### 1. Data Privacy (LGPD/GDPR)

#### Consent Management
- Record and track user consent for different data processing purposes
- Support for multiple consent types (essential, analytics, marketing, third-party)
- Audit trail for consent changes
- Easy consent revocation

#### Data Subject Rights
- **Right to Access**: Users can request their data
- **Right to Rectification**: Users can correct their data
- **Right to Erasure**: Users can request deletion (right to be forgotten)
- **Right to Data Portability**: Users can export their data
- **Right to Restriction**: Users can restrict data processing
- **Right to Objection**: Users can object to data processing

#### Data Anonymization
- Email anonymization
- Phone number anonymization
- Name anonymization
- Pseudonymization for analytics
- Irreversible hashing for sensitive data

### 2. Security (OWASP)

#### Security Headers
All responses include OWASP-recommended security headers:
- `X-Frame-Options`: Prevents clickjacking
- `X-Content-Type-Options`: Prevents MIME sniffing
- `Content-Security-Policy`: Controls resource loading
- `Strict-Transport-Security`: Enforces HTTPS
- `Referrer-Policy`: Controls referrer information
- `Permissions-Policy`: Controls browser features

#### Rate Limiting
- IP-based rate limiting
- Configurable limits per endpoint
- Rate limit headers in responses
- Protection against brute force attacks

#### Password Policy
- Minimum length: 12 characters
- Requires uppercase, lowercase, digits, and special characters
- Common password detection
- Password strength validation

#### Input Sanitization
- SQL injection prevention
- XSS (Cross-Site Scripting) prevention
- HTML sanitization
- Email validation

#### CSRF Protection
- Token generation and validation
- Protection against Cross-Site Request Forgery attacks

### 3. Audit Logging

Comprehensive audit logging for compliance:
- Authentication events (login, logout, password changes)
- Data access events (read, create, update, delete)
- Privacy events (consent changes, data requests)
- Security events (suspicious activity, alerts)
- System events (configuration changes, tenant operations)

All audit logs include:
- Who: User ID and performer
- What: Action and resource
- When: Timestamp
- Where: IP address, user agent, endpoint
- Why/How: Purpose and legal basis
- Context: Trace ID for correlation with application logs

### 4. Data Retention and Encryption

#### Data Retention Policies
Automatic data retention management based on data category:
- **Short-term**: 30 days (sessions, cache)
- **Medium-term**: 1 year (preferences, logs)
- **Long-term**: 7 years (transactions, contracts, audit logs)
- **Permanent**: Never deleted (consent records)

#### Encryption at Rest
- AES-256 encryption for sensitive data
- Key management with master key encryption
- Key rotation support
- Secure key storage

## Usage

### Consent Management

```python
from src.compliance.data_privacy import ConsentManager, ConsentRequest, ConsentType

# Record consent
consent_request = ConsentRequest(
    user_id="user123",
    consent_type=ConsentType.MARKETING,
    granted=True,
    ip_address="192.168.1.1",
    user_agent="Mozilla/5.0...",
    consent_text="I agree to receive marketing emails"
)
await ConsentManager.record_consent(db, consent_request)

# Check consent
has_consent = await ConsentManager.check_consent(
    db, "user123", ConsentType.MARKETING
)

# Revoke consent
await ConsentManager.revoke_consent(db, "user123", ConsentType.MARKETING)
```

### Data Subject Rights

```python
from src.compliance.data_privacy import (
    DataSubjectRightsManager,
    DataSubjectRequestCreate,
    DataSubjectRight
)

# Create a data subject request
request = DataSubjectRequestCreate(
    user_id="user123",
    request_type=DataSubjectRight.ERASURE,
    notes="User requested account deletion"
)
await DataSubjectRightsManager.create_request(db, request)

# Export user data
user_data = await DataSubjectRightsManager.get_user_data(db, "user123")

# Anonymize user data
await DataSubjectRightsManager.anonymize_user_data(db, "user123")
```

### Data Anonymization

```python
from src.compliance.data_privacy import DataAnonymizer

# Anonymize email
anonymized = DataAnonymizer.anonymize_email("john.doe@example.com")
# Result: "j*****e@example.com"

# Anonymize phone
anonymized = DataAnonymizer.anonymize_phone("+1-555-123-4567")
# Result: "***4567"

# Anonymize name
anonymized = DataAnonymizer.anonymize_name("John Michael Doe")
# Result: "J*** ******* D**"

# Hash data (irreversible)
hashed = DataAnonymizer.hash_data("sensitive_data", salt="random_salt")

# Pseudonymize data
pseudo = DataAnonymizer.pseudonymize("data", "user123")
```

### Audit Logging

```python
from src.compliance.audit_log import AuditLogger, AuditAction, AuditSeverity

# Log authentication
await AuditLogger.log_authentication(
    db=db,
    action=AuditAction.LOGIN,
    user_id="user123",
    ip_address="192.168.1.1",
    success=True
)

# Log data access
await AuditLogger.log_data_access(
    db=db,
    action=AuditAction.DATA_READ,
    user_id="user123",
    resource_type="account",
    resource_id="acc456",
    tenant_id="tenant1"
)

# Log privacy event
await AuditLogger.log_privacy_event(
    db=db,
    action=AuditAction.CONSENT_GRANTED,
    user_id="user123",
    performed_by="user123",
    details="Marketing consent granted"
)

# Log security event
await AuditLogger.log_security_event(
    db=db,
    action=AuditAction.SUSPICIOUS_ACTIVITY,
    user_id="user123",
    ip_address="192.168.1.1",
    severity=AuditSeverity.WARNING,
    details="Multiple failed login attempts"
)
```

### Data Retention

```python
from src.compliance.data_retention import (
    DataRetentionManager,
    DataCategory
)

# Track data for retention
await DataRetentionManager.track_data(
    db=db,
    resource_type="account",
    resource_id="acc123",
    category=DataCategory.PERSONAL_DATA
)

# Get expired data
expired = await DataRetentionManager.get_expired_data(db)

# Mark as deleted
for record in expired:
    await DataRetentionManager.mark_as_deleted(
        db, record, reason="retention_period_expired"
    )
```

### Encryption

```python
from src.compliance.data_retention import DataEncryption

# Initialize with master key
encryptor = DataEncryption(master_key="your-master-key")

# Encrypt data
encrypted = encryptor.encrypt("sensitive data")

# Decrypt data
decrypted = encryptor.decrypt(encrypted)

# Generate new encryption key
new_key = DataEncryption.generate_key()
```

### Security Middleware

The security middleware is automatically applied to all requests:

```python
from fastapi import FastAPI
from src.compliance.security import SecurityHeadersMiddleware, RateLimitMiddleware

app = FastAPI()

# Add security headers
app.add_middleware(SecurityHeadersMiddleware)

# Add rate limiting
app.add_middleware(RateLimitMiddleware, requests_per_minute=60)
```

### Password Validation

```python
from src.compliance.security import PasswordPolicy

# Validate password
is_valid, error_message = PasswordPolicy.validate("MyP@ssw0rd123")

if not is_valid:
    print(f"Password invalid: {error_message}")

# Check if password is common
if PasswordPolicy.check_common_passwords("password123"):
    print("Password is too common")
```

## API Endpoints

### Consent Management

```bash
# Record consent
POST /api/v1/compliance/consent
{
  "user_id": "user123",
  "consent_type": "marketing",
  "granted": true,
  "consent_text": "I agree to receive marketing emails"
}

# Check consent
GET /api/v1/compliance/consent/{user_id}/{consent_type}

# Revoke consent
DELETE /api/v1/compliance/consent/{user_id}/{consent_type}
```

### Data Subject Rights

```bash
# Create data subject request
POST /api/v1/compliance/data-subject-request
{
  "user_id": "user123",
  "request_type": "erasure",
  "notes": "User requested account deletion"
}

# Export user data
GET /api/v1/compliance/data-export/{user_id}

# Delete/anonymize user data
DELETE /api/v1/compliance/user-data/{user_id}
```

## Environment Variables

```bash
# Master encryption key (required for data encryption)
MASTER_ENCRYPTION_KEY=your-secure-master-key

# Rate limiting
RATE_LIMIT_PER_MINUTE=60

# Password policy
PASSWORD_MIN_LENGTH=12
```

## Compliance Checklist

### LGPD Compliance
- [x] Consent management
- [x] Data subject rights (access, rectification, erasure, portability)
- [x] Data anonymization
- [x] Audit logging
- [x] Data retention policies
- [x] Security measures

### GDPR Compliance
- [x] Lawful basis for processing
- [x] Consent management
- [x] Data subject rights
- [x] Data portability
- [x] Right to be forgotten
- [x] Data breach notification (via audit logs)
- [x] Privacy by design
- [x] Data protection impact assessment support

### OWASP Top 10 (2021)
- [x] A01: Broken Access Control (rate limiting, authentication)
- [x] A02: Cryptographic Failures (encryption at rest)
- [x] A03: Injection (input sanitization, parameterized queries)
- [x] A04: Insecure Design (security by design)
- [x] A05: Security Misconfiguration (security headers)
- [x] A06: Vulnerable Components (dependency management)
- [x] A07: Authentication Failures (password policy, audit logging)
- [x] A08: Software and Data Integrity (audit logging)
- [x] A09: Security Logging Failures (comprehensive audit logging)
- [x] A10: SSRF (input validation)

## Best Practices

1. **Always log sensitive operations**: Use audit logging for all data access and modifications
2. **Encrypt sensitive data**: Use encryption for passwords, tokens, and personal data
3. **Implement consent checks**: Verify consent before processing user data
4. **Regular data cleanup**: Implement automated jobs to delete expired data
5. **Key rotation**: Regularly rotate encryption keys
6. **Monitor audit logs**: Set up alerts for suspicious activities
7. **Test security**: Regular security testing and penetration testing
8. **Update dependencies**: Keep security dependencies up to date
9. **Document data flows**: Maintain documentation of data processing activities
10. **Train team**: Ensure team understands compliance requirements

## Migration Guide

To add compliance features to existing code:

1. **Add audit logging to sensitive operations**:
```python
# Before
user = await create_user(db, user_data)

# After
user = await create_user(db, user_data)
await AuditLogger.log_data_access(
    db, AuditAction.DATA_CREATED, user.id, "user", user.id
)
```

2. **Add consent checks**:
```python
# Before
await send_marketing_email(user)

# After
if await ConsentManager.check_consent(db, user.id, ConsentType.MARKETING):
    await send_marketing_email(user)
```

3. **Anonymize data on deletion**:
```python
# Before
await db.delete(user)

# After
await DataSubjectRightsManager.anonymize_user_data(db, user.id)
```

## Monitoring and Alerts

Set up monitoring for:
- Failed authentication attempts
- Suspicious activity patterns
- Data subject requests
- Consent revocations
- Data retention policy violations
- Encryption key expiration

## Support

For compliance questions or security concerns, refer to:
- LGPD: https://www.gov.br/cidadania/pt-br/acesso-a-informacao/lgpd
- GDPR: https://gdpr.eu/
- OWASP: https://owasp.org/

