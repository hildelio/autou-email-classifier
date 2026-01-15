from fastapi import APIRouter, HTTPException, UploadFile
from pydantic import BaseModel

from src.services.ai_service import AIService
from src.services.file_parser import FileParserService

router = APIRouter(prefix="/api", tags=["classification"])


class ClassificationResponse(BaseModel):
    category: str
    confidence: float
    suggested_reply: str
    reasoning: str = ""


@router.post("/analyze", response_model=ClassificationResponse)
async def analyze_email(file: UploadFile):
    # Validar tipo de arquivo
    allowed_types = {"application/pdf", "text/plain"}
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de arquivo não suportado. Use PDF ou TXT. Recebido: {file.content_type}",
        )

    try:
        # Salvar arquivo temporário
        import tempfile
        from pathlib import Path

        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()

            # Validar arquivo não vazio
            if not content or len(content) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Arquivo vazio ou sem conteúdo válido",
                )

            tmp.write(content)
            tmp_path = tmp.name

        try:
            # Parse do arquivo
            email_content = FileParserService.parse_file(tmp_path)

            if not email_content or len(email_content.strip()) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Arquivo vazio ou sem conteúdo válido",
                )

            # Classificação com IA
            ai_service = AIService()
            result = await ai_service.classify_email(email_content)

            return ClassificationResponse(**result)

        finally:
            # Limpar arquivo temporário
            Path(tmp_path).unlink(missing_ok=True)

    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao processar arquivo: {str(e)}",
        ) from e
