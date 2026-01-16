"""
Tests for OCR Service
"""

from pathlib import Path
from unittest.mock import Mock, patch

import httpx
import pytest

from src.services.ocr_service import OCRService


class TestOCRService:
    """Test cases for OCRService"""

    @pytest.fixture
    def temp_pdf_file(self, tmp_path):
        """Create a temporary PDF file for testing"""
        pdf_file = tmp_path / "test.pdf"
        # Create a small PDF file (well under 1MB limit)
        pdf_file.write_bytes(b"%PDF-1.4\n%EOF\n")
        return str(pdf_file)

    @pytest.fixture
    def large_pdf_file(self, tmp_path):
        """Create a large PDF file (over 1MB) for testing"""
        pdf_file = tmp_path / "large.pdf"
        # Create a file larger than 1MB
        pdf_file.write_bytes(b"x" * (2 * 1024 * 1024))  # 2MB
        return str(pdf_file)

    @pytest.fixture
    def mock_success_response(self):
        """Mock successful OCR API response"""
        return {
            "IsErroredOnProcessing": False,
            "ParsedResults": [{"ParsedText": "This is extracted text from OCR"}],
        }

    @pytest.fixture
    def mock_error_response(self):
        """Mock error OCR API response"""
        return {
            "IsErroredOnProcessing": True,
            "ErrorMessage": ["OCR processing failed"],
            "ErrorDetails": "Image quality too low",
        }

    # --- Validation Tests ---

    def test_validate_api_key_missing(self):
        """Test validation fails when API key is missing"""
        with patch("src.services.ocr_service.OCR_SPACE_API_KEY", None):
            with pytest.raises(ValueError, match="OCR_SPACE_API_KEY not configured"):
                OCRService._validate_api_key()

    def test_validate_api_key_present(self):
        """Test validation succeeds when API key is present"""
        with patch("src.services.ocr_service.OCR_SPACE_API_KEY", "test_key"):
            # Should not raise
            OCRService._validate_api_key()

    def test_validate_file_exists(self, temp_pdf_file):
        """Test file existence validation succeeds"""
        path = OCRService._validate_file_exists(temp_pdf_file)
        assert isinstance(path, Path)
        assert path.exists()

    def test_validate_file_not_found(self):
        """Test file existence validation fails for nonexistent file"""
        with pytest.raises(FileNotFoundError, match="File not found"):
            OCRService._validate_file_exists("/nonexistent/file.pdf")

    def test_validate_file_size_ok(self, temp_pdf_file):
        """Test file size validation succeeds for small file"""
        path = Path(temp_pdf_file)
        # Should not raise
        OCRService._validate_file_size(path)

    def test_validate_file_size_too_large(self, large_pdf_file):
        """Test file size validation fails for large file"""
        path = Path(large_pdf_file)
        with pytest.raises(ValueError, match="File too large for OCR"):
            OCRService._validate_file_size(path)

    # --- API Request Tests ---

    @pytest.mark.asyncio
    async def test_send_ocr_request_success(self, temp_pdf_file):
        """Test successful OCR API request"""
        with patch("src.services.ocr_service.OCR_SPACE_API_KEY", "test_key"):
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "IsErroredOnProcessing": False,
                "ParsedResults": [{"ParsedText": "Test"}],
            }

            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post.return_value = (
                    mock_response
                )

                response = await OCRService._send_ocr_request(
                    temp_pdf_file, Path(temp_pdf_file)
                )

                assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_send_ocr_request_timeout(self, temp_pdf_file):
        """Test OCR request timeout handling"""
        with patch("src.services.ocr_service.OCR_SPACE_API_KEY", "test_key"):
            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post.side_effect = (
                    httpx.TimeoutException("Timeout")
                )

                with pytest.raises(ValueError, match="OCR request timed out"):
                    await OCRService._send_ocr_request(
                        temp_pdf_file, Path(temp_pdf_file)
                    )

    @pytest.mark.asyncio
    async def test_send_ocr_request_network_error(self, temp_pdf_file):
        """Test OCR request network error handling"""
        with patch("src.services.ocr_service.OCR_SPACE_API_KEY", "test_key"):
            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post.side_effect = (
                    httpx.ConnectError("Connection failed")
                )

                with pytest.raises(ValueError, match="Network error during OCR"):
                    await OCRService._send_ocr_request(
                        temp_pdf_file, Path(temp_pdf_file)
                    )

    # --- Response Parsing Tests ---

    def test_parse_ocr_response_success(self, mock_success_response):
        """Test parsing successful OCR response"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = mock_success_response

        text = OCRService._parse_ocr_response(mock_response)
        assert text == "This is extracted text from OCR"

    def test_parse_ocr_response_http_error(self):
        """Test parsing response with HTTP error status"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"

        with pytest.raises(ValueError, match="OCR API returned status 500"):
            OCRService._parse_ocr_response(mock_response)

    def test_parse_ocr_response_processing_error(self, mock_error_response):
        """Test parsing response with OCR processing error"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = mock_error_response

        with pytest.raises(ValueError, match="OCR processing error"):
            OCRService._parse_ocr_response(mock_response)

    def test_parse_ocr_response_no_results(self):
        """Test parsing response with no results"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "IsErroredOnProcessing": False,
            "ParsedResults": [],
        }

        with pytest.raises(ValueError, match="OCR API returned no results"):
            OCRService._parse_ocr_response(mock_response)

    def test_parse_ocr_response_empty_text(self):
        """Test parsing response with empty text"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "IsErroredOnProcessing": False,
            "ParsedResults": [{"ParsedText": ""}],
        }

        with pytest.raises(ValueError, match="OCR could not extract any text"):
            OCRService._parse_ocr_response(mock_response)

    def test_parse_ocr_response_whitespace_only(self):
        """Test parsing response with whitespace-only text"""
        mock_response = Mock(spec=httpx.Response)
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "IsErroredOnProcessing": False,
            "ParsedResults": [{"ParsedText": "   \n  \n  "}],
        }

        with pytest.raises(ValueError, match="OCR could not extract any text"):
            OCRService._parse_ocr_response(mock_response)

    # --- Integration Tests ---

    @pytest.mark.asyncio
    async def test_extract_text_from_pdf_success(
        self, temp_pdf_file, mock_success_response
    ):
        """Test complete successful OCR extraction flow"""
        with patch("src.services.ocr_service.OCR_SPACE_API_KEY", "test_key"):
            mock_response = Mock(spec=httpx.Response)
            mock_response.status_code = 200
            mock_response.json.return_value = mock_success_response

            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post.return_value = (
                    mock_response
                )

                text = await OCRService.extract_text_from_pdf(temp_pdf_file)
                assert text == "This is extracted text from OCR"

    @pytest.mark.asyncio
    async def test_extract_text_from_pdf_no_api_key(self, temp_pdf_file):
        """Test OCR extraction fails without API key"""
        with patch("src.services.ocr_service.OCR_SPACE_API_KEY", None):
            with pytest.raises(ValueError, match="OCR_SPACE_API_KEY not configured"):
                await OCRService.extract_text_from_pdf(temp_pdf_file)

    @pytest.mark.asyncio
    async def test_extract_text_from_pdf_file_not_found(self):
        """Test OCR extraction fails for nonexistent file"""
        with patch("src.services.ocr_service.OCR_SPACE_API_KEY", "test_key"):
            with pytest.raises(FileNotFoundError):
                await OCRService.extract_text_from_pdf("/nonexistent/file.pdf")

    @pytest.mark.asyncio
    async def test_extract_text_from_pdf_file_too_large(self, large_pdf_file):
        """Test OCR extraction fails for oversized file"""
        with patch("src.services.ocr_service.OCR_SPACE_API_KEY", "test_key"):
            with pytest.raises(ValueError, match="File too large for OCR"):
                await OCRService.extract_text_from_pdf(large_pdf_file)

    @pytest.mark.asyncio
    async def test_extract_text_from_pdf_timeout(self, temp_pdf_file):
        """Test OCR extraction handles timeout"""
        with patch("src.services.ocr_service.OCR_SPACE_API_KEY", "test_key"):
            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post.side_effect = (
                    httpx.TimeoutException("Timeout")
                )

                with pytest.raises(ValueError, match="OCR request timed out"):
                    await OCRService.extract_text_from_pdf(temp_pdf_file)

    @pytest.mark.asyncio
    async def test_extract_text_from_pdf_network_error(self, temp_pdf_file):
        """Test OCR extraction handles network errors"""
        with patch("src.services.ocr_service.OCR_SPACE_API_KEY", "test_key"):
            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post.side_effect = (
                    httpx.ConnectError("Connection failed")
                )

                with pytest.raises(ValueError, match="Network error during OCR"):
                    await OCRService.extract_text_from_pdf(temp_pdf_file)

    @pytest.mark.asyncio
    async def test_extract_text_from_pdf_unexpected_error(self, temp_pdf_file):
        """Test OCR extraction handles unexpected errors"""
        with patch("src.services.ocr_service.OCR_SPACE_API_KEY", "test_key"):
            with patch("httpx.AsyncClient") as mock_client:
                mock_client.return_value.__aenter__.return_value.post.side_effect = (
                    RuntimeError("Unexpected error")
                )

                with pytest.raises(ValueError, match="Unexpected error during OCR"):
                    await OCRService.extract_text_from_pdf(temp_pdf_file)
