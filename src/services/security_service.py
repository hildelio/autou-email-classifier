import re
from datetime import datetime, timedelta
from typing import Dict

from fastapi import HTTPException, Request


class RateLimitStorage:
    def __init__(self):
        self.requests: Dict[str, list] = {}
        self.daily_requests: Dict[str, list] = {}

    def add_request(self, client_ip: str) -> None:
        """Record a request for client IP"""
        now = datetime.now()

        if client_ip not in self.requests:
            self.requests[client_ip] = []
        if client_ip not in self.daily_requests:
            self.daily_requests[client_ip] = []

        self.requests[client_ip].append(now)
        self.daily_requests[client_ip].append(now)

        # Cleanup old requests (older than 1 hour)
        cutoff_time = now - timedelta(hours=1)
        self.requests[client_ip] = [t for t in self.requests[client_ip] if t > cutoff_time]
        self.daily_requests[client_ip] = [
            t for t in self.daily_requests[client_ip] if t > cutoff_time
        ]

    def get_recent_requests(self, client_ip: str, minutes: int = 5) -> int:
        """Get count of requests in last N minutes"""
        if client_ip not in self.requests:
            return 0

        now = datetime.now()
        cutoff = now - timedelta(minutes=minutes)
        return len([t for t in self.requests[client_ip] if t > cutoff])

    def get_daily_requests(self, client_ip: str) -> int:
        """Get count of requests in last 24 hours"""
        if client_ip not in self.daily_requests:
            return 0

        now = datetime.now()
        cutoff = now - timedelta(hours=24)
        return len([t for t in self.daily_requests[client_ip] if t > cutoff])


# Global rate limit storage
rate_limiter = RateLimitStorage()


class SecurityService:
    # Limits configuration
    REQUESTS_PER_5_MIN = 10
    REQUESTS_PER_24_HOURS = 100
    MAX_FILE_SIZE_MB = 5
    REQUEST_TIMEOUT_SECONDS = 30

    # Patterns for basic security validation
    SQL_INJECTION_PATTERN = re.compile(
        r"(union|select|insert|update|delete|drop|create|alter|exec|execute)",
        re.IGNORECASE,
    )
    XSS_PATTERN = re.compile(r"(<script|javascript:|onerror=|onclick=)", re.IGNORECASE)

    @staticmethod
    def get_client_ip(request: Request) -> str:
        """Extract client IP from request (handles proxies)"""
        if request.headers.get("x-forwarded-for"):
            return request.headers.get("x-forwarded-for").split(",")[0].strip()
        return request.client.host if request.client else "unknown"

    @staticmethod
    def validate_rate_limit(request: Request) -> None:
        """Check rate limiting for client IP"""
        client_ip = SecurityService.get_client_ip(request)

        # Check 5-minute limit
        recent_requests = rate_limiter.get_recent_requests(client_ip, minutes=5)
        if recent_requests >= SecurityService.REQUESTS_PER_5_MIN:
            raise HTTPException(
                status_code=429,
                detail=f"Muitas requisições. Máximo {SecurityService.REQUESTS_PER_5_MIN} requisições a cada 5 minutos. Tente novamente mais tarde.",
            )

        # Check 24-hour limit
        daily_requests = rate_limiter.get_daily_requests(client_ip)
        if daily_requests >= SecurityService.REQUESTS_PER_24_HOURS:
            raise HTTPException(
                status_code=429,
                detail=f"Limite diário excedido. Máximo {SecurityService.REQUESTS_PER_24_HOURS} requisições por 24 horas.",
            )

    @staticmethod
    def record_request(request: Request) -> None:
        """Record a successful request for rate limiting"""
        client_ip = SecurityService.get_client_ip(request)
        rate_limiter.add_request(client_ip)

    @staticmethod
    def validate_file_size(file_size_bytes: int) -> None:
        """Validate file size doesn't exceed maximum"""
        max_size_bytes = SecurityService.MAX_FILE_SIZE_MB * 1024 * 1024

        if file_size_bytes > max_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"Arquivo muito grande. Máximo {SecurityService.MAX_FILE_SIZE_MB}MB. Recebido: {file_size_bytes / (1024 * 1024):.2f}MB",
            )

    @staticmethod
    def validate_input_content(content: str) -> None:
        """Validate content for basic security threats"""
        if len(content) > 1000000:  # 1MB of text
            raise HTTPException(
                status_code=413,
                detail="Conteúdo muito longo. Máximo 1MB de texto.",
            )

        # Basic SQL injection check
        if SecurityService.SQL_INJECTION_PATTERN.search(content):
            raise HTTPException(
                status_code=400,
                detail="Conteúdo contém padrões suspeitos. Envie um email legítimo.",
            )

        # Basic XSS check
        if SecurityService.XSS_PATTERN.search(content):
            raise HTTPException(
                status_code=400,
                detail="Conteúdo contém scripts. Envie um email legítimo.",
            )

    @staticmethod
    def get_rate_limit_headers(request: Request) -> dict:
        """Generate rate limit headers for response"""
        client_ip = SecurityService.get_client_ip(request)
        recent = rate_limiter.get_recent_requests(client_ip, minutes=5)
        daily = rate_limiter.get_daily_requests(client_ip)

        return {
            "X-RateLimit-Limit-5min": str(SecurityService.REQUESTS_PER_5_MIN),
            "X-RateLimit-Remaining-5min": str(max(0, SecurityService.REQUESTS_PER_5_MIN - recent)),
            "X-RateLimit-Limit-24h": str(SecurityService.REQUESTS_PER_24_HOURS),
            "X-RateLimit-Remaining-24h": str(max(0, SecurityService.REQUESTS_PER_24_HOURS - daily)),
        }
