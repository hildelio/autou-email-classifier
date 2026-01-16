"""
OCR Service using OCR.space API

This service provides OCR capabilities for scanned PDFs that don't have
extractable text. Uses the free OCR.space API.

Free tier limitations:
- 25,000 requests/month
- 500 requests/day
- 1MB file size limit
"""

from pathlib import Path

import httpx

from src.config import OCR_SPACE_API_KEY


class OCRService:
    """Service for performing OCR on PDF files using OCR.space API"""

    BASE_URL = "https://api.ocr.space/parse/image"

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
        """
        # Check if API key is configured
        if not OCR_SPACE_API_KEY:
            raise ValueError(
                "OCR_SPACE_API_KEY not configured. "
                "Get a free API key at https://ocr.space/ocrapi"
            )

        # Validate file exists
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Check file size (1MB limit for free tier)
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > 1:
            raise ValueError(
                f"File too large for OCR ({file_size_mb:.2f}MB). "
                "OCR.space free tier has 1MB limit. "
                "Consider compressing the PDF or upgrading API plan."
            )

        try:
            # Prepare the API request
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

                    print("Sending PDF to OCR.space API for processing...")
                    response = await client.post(OCRService.BASE_URL, files=files, data=data)

            # Check response status
            if response.status_code != 200:
                raise ValueError(f"OCR API returned status {response.status_code}: {response.text}")

            # Parse response
            result = response.json()

            # Check for API errors
            if not result.get("IsErroredOnProcessing", False):
                # Success - extract text
                parsed_results = result.get("ParsedResults", [])
                if not parsed_results:
                    raise ValueError("OCR API returned no results")

                text = parsed_results[0].get("ParsedText", "")

                if not text or not text.strip():
                    raise ValueError(
                        "OCR could not extract any text from the PDF. "
                        "The PDF may be blank or image quality is too low."
                    )

                print(f"OCR extracted {len(text)} characters from PDF")
                return text
            else:
                # Error occurred
                error_msg = result.get("ErrorMessage", ["Unknown error"])
                error_details = result.get("ErrorDetails", "")
                raise ValueError(f"OCR processing error: {error_msg}. Details: {error_details}")

        except httpx.TimeoutException:
            raise ValueError("OCR request timed out. The file may be too large or complex.")
        except httpx.HTTPError as e:
            raise ValueError(f"Network error during OCR: {str(e)}") from e
        except Exception as e:
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Unexpected error during OCR: {str(e)}") from e
