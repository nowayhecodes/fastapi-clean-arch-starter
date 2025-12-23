"""Security features for OWASP compliance."""
import secrets
from collections.abc import Callable
from datetime import datetime, timedelta
from typing import Optional

from fastapi import HTTPException, Request, Response, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from starlette.middleware.base import BaseHTTPMiddleware


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware to add security headers (OWASP recommendations)."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response.
        
        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.
            
        Returns:
            Response with security headers added.
        """
        response = await call_next(request)
        
        # OWASP recommended security headers
        
        # Prevent clickjacking attacks
        response.headers["X-Frame-Options"] = "DENY"
        
        # Enable XSS protection
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Control referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        
        # Strict Transport Security (HSTS)
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        
        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=(), payment=()"
        )
        
        # Remove server identification
        response.headers.pop("Server", None)
        
        # Add cache control for sensitive endpoints
        if any(path in request.url.path for path in ["/account", "/auth", "/api"]):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, private"
            response.headers["Pragma"] = "no-cache"
        
        return response


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Simple rate limiting middleware."""
    
    def __init__(self, app, requests_per_minute: int = 60):
        """Initialize rate limiter.
        
        Args:
            app: The FastAPI application.
            requests_per_minute: Maximum requests per minute per IP.
        """
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_counts: dict[str, list[datetime]] = {}
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check rate limit and process request.
        
        Args:
            request: The incoming request.
            call_next: The next middleware or route handler.
            
        Returns:
            Response or rate limit error.
        """
        # Skip rate limiting for health checks and docs
        if request.url.path in ["/health", "/docs", "/redoc", "/openapi.json"]:
            return await call_next(request)
        
        client_ip = get_remote_address(request)
        now = datetime.utcnow()
        
        # Clean old entries
        if client_ip in self.request_counts:
            self.request_counts[client_ip] = [
                req_time for req_time in self.request_counts[client_ip]
                if now - req_time < timedelta(minutes=1)
            ]
        else:
            self.request_counts[client_ip] = []
        
        # Check rate limit
        if len(self.request_counts[client_ip]) >= self.requests_per_minute:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Rate limit exceeded. Please try again later.",
                headers={"Retry-After": "60"},
            )
        
        # Add current request
        self.request_counts[client_ip].append(now)
        
        response = await call_next(request)
        
        # Add rate limit headers
        remaining = self.requests_per_minute - len(self.request_counts[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int((now + timedelta(minutes=1)).timestamp()))
        
        return response


# Create rate limiter instance for decorator-based rate limiting
limiter = Limiter(key_func=get_remote_address)


class CSRFProtection:
    """CSRF protection utilities."""
    
    @staticmethod
    def generate_token() -> str:
        """Generate a CSRF token.
        
        Returns:
            Random CSRF token.
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_token(token: str, expected_token: str) -> bool:
        """Validate CSRF token.
        
        Args:
            token: Token from request.
            expected_token: Expected token from session.
            
        Returns:
            True if tokens match.
        """
        return secrets.compare_digest(token, expected_token)


class PasswordPolicy:
    """Password policy enforcement (OWASP recommendations)."""
    
    MIN_LENGTH = 12
    REQUIRE_UPPERCASE = True
    REQUIRE_LOWERCASE = True
    REQUIRE_DIGIT = True
    REQUIRE_SPECIAL = True
    SPECIAL_CHARS = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    @classmethod
    def validate(cls, password: str) -> tuple[bool, Optional[str]]:
        """Validate password against policy.
        
        Args:
            password: Password to validate.
            
        Returns:
            Tuple of (is_valid, error_message).
        """
        if len(password) < cls.MIN_LENGTH:
            return False, f"Password must be at least {cls.MIN_LENGTH} characters long"
        
        if cls.REQUIRE_UPPERCASE and not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        if cls.REQUIRE_LOWERCASE and not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        if cls.REQUIRE_DIGIT and not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        
        if cls.REQUIRE_SPECIAL and not any(c in cls.SPECIAL_CHARS for c in password):
            return False, f"Password must contain at least one special character ({cls.SPECIAL_CHARS})"
        
        return True, None
    
    @staticmethod
    def check_common_passwords(password: str) -> bool:
        """Check if password is in common passwords list.
        
        Args:
            password: Password to check.
            
        Returns:
            True if password is common (should be rejected).
        """
        # Common passwords list (simplified - in production use a comprehensive list)
        common_passwords = {
            "password", "123456", "123456789", "12345678", "12345",
            "1234567", "password1", "123123", "1234567890", "qwerty",
            "abc123", "111111", "admin", "letmein", "welcome",
        }
        
        return password.lower() in common_passwords


class InputSanitizer:
    """Input sanitization to prevent injection attacks."""
    
    @staticmethod
    def sanitize_sql_input(value: str) -> str:
        """Sanitize input for SQL (note: use parameterized queries instead).
        
        Args:
            value: Input value.
            
        Returns:
            Sanitized value.
        """
        # Remove common SQL injection patterns
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        sanitized = value
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, "")
        return sanitized
    
    @staticmethod
    def sanitize_html_input(value: str) -> str:
        """Sanitize HTML input to prevent XSS.
        
        Args:
            value: Input value.
            
        Returns:
            Sanitized value.
        """
        # Basic HTML escaping
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            ">": "&gt;",
            "<": "&lt;",
        }
        return "".join(html_escape_table.get(c, c) for c in value)
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format.
        
        Args:
            email: Email address to validate.
            
        Returns:
            True if valid email format.
        """
        import re
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))


class SessionSecurity:
    """Session security utilities."""
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate secure session ID.
        
        Returns:
            Random session ID.
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def is_session_expired(
        created_at: datetime,
        max_age_minutes: int = 30,
    ) -> bool:
        """Check if session is expired.
        
        Args:
            created_at: Session creation time.
            max_age_minutes: Maximum session age in minutes.
            
        Returns:
            True if session is expired.
        """
        return datetime.utcnow() - created_at > timedelta(minutes=max_age_minutes)

