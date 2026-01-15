from fastapi import APIRouter, HTTPException, Request, UploadFile
from pydantic import BaseModel

from src.services.ai_service import AIService
from src.services.file_parser import FileParserService
from src.services.security_service import SecurityService

router = APIRouter(prefix="/api", tags=["classification"])


class ClassificationResponse(BaseModel):
    category: str
    confidence: float
    suggested_reply: str
    reasoning: str = ""


@router.post("/analyze", response_model=ClassificationResponse)
async def analyze_email(file: UploadFile, request: Request):
    # Rate limiting validation
    SecurityService.validate_rate_limit(request)

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

        print(f"=== DEBUG: Received file {file.filename}, content_type: {file.content_type} ===")
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            
            print(f"DEBUG: File content size: {len(content)} bytes")

            # Validar arquivo não vazio
            if not content or len(content) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="Arquivo vazio ou sem conteúdo válido",
                )

            # Validar tamanho do arquivo
            SecurityService.validate_file_size(len(content))

            tmp.write(content)
            tmp_path = tmp.name
            print(f"DEBUG: Saved to temp file: {tmp_path}")

        try:
            # Parse do arquivo
            print(f"=== DEBUG: Parsing file {file.filename} ===")
            email_content = FileParserService.parse_file(tmp_path)
            print(f"DEBUG: Extracted text length: {len(email_content)}")
            print(f"DEBUG: First 500 chars: {email_content[:500]!r}")

            if not email_content or len(email_content.strip()) == 0:
                print(f"DEBUG: Text is empty after strip! Original length was {len(email_content)}")
                raise HTTPException(
                    status_code=400,
                    detail="Arquivo vazio ou sem conteúdo válido",
                )

            print(f"DEBUG: Text validation passed. Length: {len(email_content)}")

            # Validar conteúdo extraído para segurança
            SecurityService.validate_input_content(email_content)

            # Classificação com IA
            ai_service = AIService()
            result = await ai_service.classify_email(email_content)

            # Record successful request for rate limiting
            SecurityService.record_request(request)

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
