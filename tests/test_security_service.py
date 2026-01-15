"""
Tests for Security Service - Rate Limiting and Input Validation
"""

import pytest

from src.services.security_service import SecurityService, rate_limiter


# Mock Request object for testing
class MockRequest:
    def __init__(self, client_host="192.168.1.100", headers=None):
        self.client = type("obj", (object,), {"host": client_host})()
        self.headers = headers or {}


class TestSecurityService:
    """Test cases for Security Service"""

    def test_get_client_ip_from_direct_connection(self):
        """Test extracting IP from direct connection"""
        request = MockRequest(client_host="192.168.1.100")
        ip = SecurityService.get_client_ip(request)
        assert ip == "192.168.1.100"

    def test_get_client_ip_from_proxy(self):
        """Test extracting IP from X-Forwarded-For header"""
        request = MockRequest(headers={"x-forwarded-for": "10.0.0.1, 192.168.1.100"})
        ip = SecurityService.get_client_ip(request)
        assert ip == "10.0.0.1"

    def test_rate_limit_storage_add_request(self):
        """Test adding requests to rate limit storage"""
        rate_limiter.requests.clear()
        rate_limiter.daily_requests.clear()

        rate_limiter.add_request("192.168.1.100")
        assert "192.168.1.100" in rate_limiter.requests
        assert len(rate_limiter.requests["192.168.1.100"]) == 1

    def test_rate_limit_storage_get_recent_requests(self):
        """Test getting recent requests count"""
        rate_limiter.requests.clear()
        rate_limiter.daily_requests.clear()

        ip = "192.168.1.100"
        for _ in range(5):
            rate_limiter.add_request(ip)

        recent = rate_limiter.get_recent_requests(ip, minutes=5)
        assert recent == 5

    def test_rate_limit_storage_get_daily_requests(self):
        """Test getting daily requests count"""
        rate_limiter.requests.clear()
        rate_limiter.daily_requests.clear()

        ip = "192.168.1.100"
        for _ in range(8):
            rate_limiter.add_request(ip)

        daily = rate_limiter.get_daily_requests(ip)
        assert daily == 8

    def test_validate_file_size_under_limit(self):
        """Test file size validation with valid size"""
        # 5MB = 5242880 bytes
        size_bytes = 1024 * 1024  # 1MB
        SecurityService.validate_file_size(size_bytes)  # Should not raise

    def test_validate_file_size_exceeds_limit(self):
        """Test file size validation with size exceeding limit"""
        # 6MB = 6291456 bytes (exceeds 5MB limit)
        size_bytes = 6 * 1024 * 1024
        with pytest.raises(Exception) as exc_info:
            SecurityService.validate_file_size(size_bytes)
        exc_str = (
            str(exc_info.value.detail) if hasattr(exc_info.value, "detail") else str(exc_info.value)
        )
        assert "muito grande" in exc_str

    def test_validate_input_content_valid_email(self):
        """Test input validation with legitimate email content"""
        content = "Olá, gostaria de saber o status do meu pedido. Obrigado!"
        SecurityService.validate_input_content(content)  # Should not raise

    def test_validate_input_content_sql_injection_attempt(self):
        """Test input validation detects SQL injection attempt"""
        content = "SELECT * FROM users; DROP TABLE emails; --"
        with pytest.raises(Exception) as exc_info:
            SecurityService.validate_input_content(content)
        exc_str = (
            str(exc_info.value.detail) if hasattr(exc_info.value, "detail") else str(exc_info.value)
        )
        assert "suspeitos" in exc_str

    def test_validate_input_content_xss_attempt(self):
        """Test input validation detects XSS attempt"""
        content = "<script>alert('hacked')</script>"
        with pytest.raises(Exception) as exc_info:
            SecurityService.validate_input_content(content)
        exc_str = (
            str(exc_info.value.detail) if hasattr(exc_info.value, "detail") else str(exc_info.value)
        )
        assert "scripts" in exc_str

    def test_validate_input_content_too_long(self):
        """Test input validation with content exceeding length limit"""
        content = "A" * (1000001)  # 1MB + 1 byte
        with pytest.raises(Exception) as exc_info:
            SecurityService.validate_input_content(content)
        exc_str = (
            str(exc_info.value.detail) if hasattr(exc_info.value, "detail") else str(exc_info.value)
        )
        assert "muito longo" in exc_str

    def test_get_rate_limit_headers(self):
        """Test rate limit headers generation"""
        rate_limiter.requests.clear()
        rate_limiter.daily_requests.clear()

        request = MockRequest(client_host="192.168.1.100")

        # Add 3 requests
        for _ in range(3):
            rate_limiter.add_request("192.168.1.100")

        headers = SecurityService.get_rate_limit_headers(request)

        assert headers["X-RateLimit-Limit-5min"] == "10"
        assert headers["X-RateLimit-Remaining-5min"] == "7"  # 10 - 3
        assert headers["X-RateLimit-Limit-24h"] == "100"
        assert headers["X-RateLimit-Remaining-24h"] == "97"  # 100 - 3


class TestClassifierSecurityIntegration:
    """Integration tests for security with classifier endpoint"""

    def setup_method(self):
        """Setup for each test"""
        rate_limiter.requests.clear()
        rate_limiter.daily_requests.clear()

    def test_rate_limit_blocks_excessive_requests(self):
        """Test that rate limiting blocks excessive requests"""
        from fastapi import HTTPException

        # Simulate 10 requests in 5 minutes
        for _ in range(10):
            rate_limiter.add_request("127.0.0.1")

        # 11th request should trigger rate limit
        request = MockRequest(client_host="127.0.0.1")
        with pytest.raises(HTTPException) as exc_info:
            SecurityService.validate_rate_limit(request)
        assert exc_info.value.status_code == 429
