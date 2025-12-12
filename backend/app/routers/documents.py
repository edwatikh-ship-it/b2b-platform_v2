from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


class DocumentInfo(BaseModel):
    filename: str
    status: str
    size: int


@router.get("/formats")
async def get_supported_formats():
    """Получить список поддерживаемых форматов документов"""
    return {
        "formats": [
            {
                "ext": ".pdf",
                "mime": "application/pdf",
                "description": "PDF документ",
            },
            {
                "ext": ".docx",
                "mime": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "description": "Word документ",
            },
            {
                "ext": ".xlsx",
                "mime": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "description": "Excel таблица",
            },
        ]
    }


@router.get("/info/{doc_id}")
async def get_document_info(doc_id: int):
    """Получить информацию о документе"""
    # Простой ответ для демо
    return {
        "doc_id": doc_id,
        "filename": f"document_{doc_id}.pdf",
        "status": "uploaded",
        "size": 1024,
        "created_at": "2025-12-12T10:00:00Z",
    }
