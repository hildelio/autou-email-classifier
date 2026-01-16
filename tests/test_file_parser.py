"""
Tests for FileParserService
"""

import tempfile
from pathlib import Path

import pytest

from src.services.file_parser import FileParserService


class TestFileParserService:
    """Test cases for FileParserService"""

    @pytest.fixture
    def temp_txt_file(self):
        """Create a temporary TXT file for testing"""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("This is a test email.\nWith multiple lines.")
            temp_path = f.name
        yield temp_path
        Path(temp_path).unlink()

    @pytest.fixture
    def temp_pdf_file(self):
        """Create a temporary PDF file for testing"""
        try:
            from pypdf import PdfWriter

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                temp_path = f.name

            writer = PdfWriter()
            writer.add_blank_page(width=200, height=200)
            page = writer.pages[0]
            page.merge_page(page)

            with open(temp_path, "wb") as f:
                writer.write(f)

            yield temp_path
            Path(temp_path).unlink()
        except Exception:
            pytest.skip("PDF creation failed")

    async def test_parse_txt_file(self, temp_txt_file):
        """Test parsing a TXT file"""
        result = await FileParserService.parse_file(temp_txt_file)
        assert result is not None
        assert len(result) > 0
        assert "test email" in result

    def test_parse_txt_direct(self, temp_txt_file):
        """Test parsing TXT directly"""
        result = FileParserService.parse_txt(temp_txt_file)
        assert "test email" in result

    def test_clean_text(self):
        """Test text cleaning"""
        dirty_text = "  This   is   a   test  \n  with   spaces  "
        cleaned = FileParserService.clean_text(dirty_text)
        # Current implementation collapses all whitespace to single spaces
        assert "This is a test with spaces" == cleaned

    def test_clean_text_collapses_whitespace(self):
        """Test that clean_text collapses all types of whitespace"""
        text_with_breaks = "Line 1\nLine 2\nLine 3"
        cleaned = FileParserService.clean_text(text_with_breaks)
        # Current behavior: all newlines become spaces
        assert "Line 1 Line 2 Line 3" == cleaned

    def test_clean_text_removes_empty_lines(self):
        """Test that clean_text handles excessive whitespace"""
        text = "Line 1\n\n\n\nLine 2\n\n"
        cleaned = FileParserService.clean_text(text)
        assert "Line 1" in cleaned
        assert "Line 2" in cleaned

    def test_clean_text_multiple_spaces(self):
        """Test cleaning multiple spaces on the same line"""
        text = "Too    many     spaces"
        cleaned = FileParserService.clean_text(text)
        assert cleaned == "Too many spaces"

    def test_clean_text_mixed_whitespace(self):
        """Test cleaning various whitespace characters"""
        text = "Text\twith\ttabs\n  and   spaces  "
        cleaned = FileParserService.clean_text(text)
        # All whitespace collapsed to single spaces
        assert "Text with tabs and spaces" == cleaned

    def test_clean_text_empty(self):
        """Test cleaning empty text"""
        result = FileParserService.clean_text("")
        assert result == ""

    def test_clean_text_only_whitespace(self):
        """Test cleaning text with only whitespace"""
        result = FileParserService.clean_text("   \n\n   \n  ")
        assert result == ""

    async def test_file_not_found(self):
        """Test error when file not found"""
        with pytest.raises(FileNotFoundError):
            await FileParserService.parse_file("/nonexistent/file.txt")

    async def test_unsupported_extension(self):
        """Test error for unsupported file type"""
        with tempfile.NamedTemporaryFile(suffix=".doc") as f:
            with pytest.raises(ValueError, match="Tipo de arquivo não suportado"):
                await FileParserService.parse_file(f.name)

    async def test_file_too_large(self):
        """Test error when file exceeds size limit"""
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            # Write data larger than 10MB (simulated)
            temp_path = f.name

        try:
            # Temporarily reduce size limit for testing
            original_limit = FileParserService.MAX_FILE_SIZE
            FileParserService.MAX_FILE_SIZE = 100  # 100 bytes

            with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
                f.write(b"x" * 200)
                temp_path = f.name

            try:
                with pytest.raises(ValueError, match="Arquivo muito grande"):
                    await FileParserService.parse_file(temp_path)
            finally:
                Path(temp_path).unlink()
        finally:
            FileParserService.MAX_FILE_SIZE = original_limit

    def test_supported_extensions(self):
        """Test supported file extensions"""
        assert ".pdf" in FileParserService.SUPPORTED_EXTENSIONS
        assert ".txt" in FileParserService.SUPPORTED_EXTENSIONS

    def test_parse_txt_latin1_encoding(self):
        """Test parsing TXT with latin-1 encoding"""
        with tempfile.NamedTemporaryFile(mode="wb", suffix=".txt", delete=False) as f:
            # Write text that will fail with UTF-8 but work with latin-1
            f.write(b"Caf\xe9")  # 'Café' in latin-1
            temp_path = f.name

        try:
            result = FileParserService.parse_txt(temp_path)
            assert "Caf" in result  # Should contain the text
        finally:
            Path(temp_path).unlink()

    # --- OCR Integration Tests ---

    @pytest.mark.asyncio
    async def test_parse_pdf_with_ocr_unavailable(self, temp_pdf_file):
        """Test parsing scanned PDF without OCR configured"""
        from unittest.mock import MagicMock, patch

        # Mock empty PDF (no extractable text)
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""
        mock_reader.pages = [mock_page]

        with patch("pypdf.PdfReader", return_value=mock_reader):
            # Ensure OCR is not available
            with patch.dict("src.config.__dict__", {"OCR_SPACE_API_KEY": None}):
                with pytest.raises(ValueError, match="PDF não contém texto extraível"):
                    await FileParserService.parse_pdf(temp_pdf_file)

    @pytest.mark.asyncio
    async def test_parse_pdf_with_ocr_success(self, temp_pdf_file):
        """Test parsing scanned PDF with OCR fallback"""
        from unittest.mock import AsyncMock, MagicMock, patch

        # Mock empty PDF (no extractable text)
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = ""
        mock_reader.pages = [mock_page]

        with patch("pypdf.PdfReader", return_value=mock_reader):
            # Make OCR available
            with patch.dict("src.config.__dict__", {"OCR_SPACE_API_KEY": "test_key"}):
                # Mock successful OCR extraction
                mock_ocr_result = AsyncMock(return_value="OCR extracted text")
                with patch(
                    "src.services.ocr_service.OCRService.extract_text_from_pdf",
                    mock_ocr_result,
                ):
                    result = await FileParserService.parse_pdf(temp_pdf_file)
                    assert "OCR extracted text" in result
                    # Verify OCR was called
                    assert mock_ocr_result.called

    @pytest.mark.asyncio
    async def test_parse_pdf_prefers_direct_extraction(self, temp_pdf_file):
        """Test that PDF with extractable text doesn't use OCR"""
        from unittest.mock import AsyncMock, MagicMock, patch

        # Mock PDF with extractable text
        mock_reader = MagicMock()
        mock_page = MagicMock()
        mock_page.extract_text.return_value = "Direct text from PDF"
        mock_reader.pages = [mock_page]

        with patch("pypdf.PdfReader", return_value=mock_reader):
            # Mock OCR (should NOT be called)
            mock_ocr_result = AsyncMock(return_value="OCR text")
            with patch(
                "src.services.ocr_service.OCRService.extract_text_from_pdf",
                mock_ocr_result,
            ):
                result = await FileParserService.parse_pdf(temp_pdf_file)
                assert "Direct text" in result
                # OCR should NOT have been called
                assert not mock_ocr_result.called
