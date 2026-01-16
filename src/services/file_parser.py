import re
from pathlib import Path

import pypdf


class FileParserService:
    SUPPORTED_EXTENSIONS = {".pdf", ".txt"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    @staticmethod
    async def parse_file(file_path: str) -> str:
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {file_path}")

        if path.suffix.lower() not in FileParserService.SUPPORTED_EXTENSIONS:
            raise ValueError(
                f"Tipo de arquivo não suportado. " f"Use: {FileParserService.SUPPORTED_EXTENSIONS}"
            )

        if path.stat().st_size > FileParserService.MAX_FILE_SIZE:
            raise ValueError(
                f"Arquivo muito grande. Máximo: "
                f"{FileParserService.MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        if path.suffix.lower() == ".pdf":
            text = await FileParserService.parse_pdf(str(path))
        else:
            text = FileParserService.parse_txt(str(path))

        return FileParserService.clean_text(text)

    @staticmethod
    async def parse_pdf(file_path: str) -> str:
        """
        Parse PDF file. First tries to extract text directly.
        Falls back to OCR if no text is found (scanned PDF).
        """
        try:
            text = ""
            with open(file_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"

            # If we extracted text successfully, return it
            if text and text.strip():
                print(f"Extracted {len(text)} characters from PDF using pypdf")
                return text

            # No text found - PDF is likely scanned
            print("PDF has no extractable text. Attempting OCR...")

            # Try OCR as fallback
            from src.config import OCR_SPACE_API_KEY
            from src.services.ocr_service import OCRService

            if not OCR_SPACE_API_KEY:
                raise ValueError(
                    "PDF não contém texto extraível (PDF escaneado). "
                    "Para processar PDFs escaneados, configure OCR_SPACE_API_KEY no arquivo .env. "
                    "Obtenha uma chave grátis em: https://ocr.space/ocrapi"
                )

            # Use OCR to extract text
            text = await OCRService.extract_text_from_pdf(file_path)
            return text

        except Exception as e:
            # If it's a ValueError we threw, re-raise it
            if isinstance(e, ValueError):
                raise
            raise ValueError(f"Erro ao ler PDF: {str(e)}") from e

    @staticmethod
    def parse_txt(file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                return file.read()
        except UnicodeDecodeError:
            # Tentar com encoding latin-1 se utf-8 falhar
            with open(file_path, "r", encoding="latin-1") as file:
                return file.read()
        except Exception as e:
            raise ValueError(f"Erro ao ler TXT: {str(e)}") from e

    @staticmethod
    def clean_text(text: str) -> str:
        if not text:
            return ""

        # Remover espaços múltiplos
        text = re.sub(r"\s+", " ", text)

        # Remover espaços no início e fim
        text = text.strip()

        # Remover caracteres de controle (exceto quebras de linha)
        text = "".join(char for char in text if ord(char) >= 32 or char == "\n")

        return text
