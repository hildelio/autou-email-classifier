import re
from pathlib import Path

import pypdf


class FileParserService:
    SUPPORTED_EXTENSIONS = {".pdf", ".txt"}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

    @staticmethod
    def parse_file(file_path: str) -> str:
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
            text = FileParserService.parse_pdf(str(path))
        else:
            text = FileParserService.parse_txt(str(path))

        return FileParserService.clean_text(text)

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        try:
            text = ""
            with open(file_path, "rb") as file:
                reader = pypdf.PdfReader(file)
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            return text
        except Exception as e:
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
