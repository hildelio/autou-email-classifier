"""
OCR Service using OCR.space API

This service provides OCR capabilities for scanned PDFs that don't have
extractable text. Uses the free OCR.space API.

Free tier limitations:
- 25,000 requests/month
- 500 requests/day
- 1MB file size limit
"""

import logging
from pathlib import Path

import httpx

from src.config import OCR_SPACE_API_KEY

logger = logging.getLogger(__name__)


class OCRService:
    """Service for performing OCR on PDF files using OCR.space API"""

    BASE_URL = "https://api.ocr.space/parse/image"
    MAX_FILE_SIZE_MB = 1.0  # Free tier limit

    @staticmethod
    def _validate_api_key() -> None:
        """
        Validate that OCR API key is configured.

        Raises:
            ValueError: If API key is missing
        """
        if not OCR_SPACE_API_KEY:
            raise ValueError(
                "OCR_SPACE_API_KEY not configured. "
                "Get a free API key at https://ocr.space/ocrapi"
            )

    @staticmethod
    def _validate_file_exists(file_path: str) -> Path:
        """
        Validate that the file exists.

        Args:
            file_path: Path to the file

        Returns:
            Path object for the file

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        return path

    @staticmethod
    def _validate_file_size(path: Path) -> None:
        """
        Validate that file is within size limits.

        Args:
            path: Path to the file

        Raises:
            ValueError: If file exceeds size limit
        """
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > OCRService.MAX_FILE_SIZE_MB:
            raise ValueError(
                f"File too large for OCR ({file_size_mb:.2f}MB). "
                f"OCR.space free tier has {OCRService.MAX_FILE_SIZE_MB}MB limit. "
                "Consider compressing the PDF or upgrading API plan."
            )

    @staticmethod
    async def _send_ocr_request(file_path: str, path: Path) -> httpx.Response:
        """
        Send OCR request to API.

        Args:
            file_path: Path to the file
            path: Path object for the file

        Returns:
            API response

        Raises:
            ValueError: On timeout or network errors
        """
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                with open(file_path, "rb") as f:
                    files = {"file": (path.name, f, "application/pdf")}
                    data = {
                        "apikey": OCR_SPACE_API_KEY,
                        "language": "por",  # Portuguese
                        "isOverlayRequired": False,
                        "detectOrientation": True,
                        "scale": True,  # Auto-scale for better accuracy
                    }

                    logger.info("Sending PDF to OCR.space API for processing")
                    response = await client.post(
                        OCRService.BASE_URL, files=files, data=data
                    )
            return response

        except httpx.TimeoutException as e:
            logger.error("OCR request timed out")
            raise ValueError(
                "OCR request timed out. The file may be too large or complex."
            ) from e
        except httpx.HTTPError as e:
            logger.error(f"Network error during OCR: {e}")
            raise ValueError(f"Network error during OCR: {str(e)}") from e

    @staticmethod
    def _parse_ocr_response(response: httpx.Response) -> str:
        """
        Parse and validate OCR API response.

        Args:
            response: API response

        Returns:
            Extracted text

        Raises:
            ValueError: If response is invalid or contains errors
        """
        # Check response status
        if response.status_code != 200:
            logger.error(f"OCR API returned status {response.status_code}")
            raise ValueError(
                f"OCR API returned status {response.status_code}: {response.text}"
            )

        # Parse response
        result = response.json()

        # Check for API errors
        if result.get("IsErroredOnProcessing", False):
            # Error occurred
            error_msg = result.get("ErrorMessage", ["Unknown error"])
            error_details = result.get("ErrorDetails", "")
            logger.error(f"OCR processing error: {error_msg}")
            raise ValueError(
                f"OCR processing error: {error_msg}. Details: {error_details}"
            )

        # Success - extract text
        parsed_results = result.get("ParsedResults", [])
        if not parsed_results:
            logger.warning("OCR API returned no results")
            raise ValueError("OCR API returned no results")

        text = parsed_results[0].get("ParsedText", "")

        if not text or not text.strip():
            logger.warning("OCR could not extract any text from PDF")
            raise ValueError(
                "OCR could not extract any text from the PDF. "
                "The PDF may be blank or image quality is too low."
            )

        logger.info(f"OCR extracted {len(text)} characters from PDF")
        return text

    @staticmethod
    async def extract_text_from_pdf(file_path: str) -> str:
        """
        Extract text from a PDF file using OCR.space API.

        Args:
            file_path: Path to the PDF file

        Returns:
            Extracted text from the PDF

        Raises:
            ValueError: If OCR extraction fails or API key is missing
            FileNotFoundError: If file doesn't exist
        """
        # Validate preconditions
        OCRService._validate_api_key()
        path = OCRService._validate_file_exists(file_path)
        OCRService._validate_file_size(path)

        # Send request and parse response
        try:
            response = await OCRService._send_ocr_request(file_path, path)
            return OCRService._parse_ocr_response(response)
        except ValueError:
            # Re-raise ValueError as-is (already handled)
            raise
        except Exception as e:
            # Catch any unexpected errors
            logger.exception("Unexpected error during OCR")
            raise ValueError(f"Unexpected error during OCR: {str(e)}") from e
