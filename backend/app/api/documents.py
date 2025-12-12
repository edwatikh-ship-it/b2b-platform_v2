from fastapi import APIRouter, UploadFile, File
from app.services.parser import DocumentParser
import os
import tempfile

router = APIRouter()
parser = DocumentParser()

@router.post("/api/v1/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Загрузка и парсинг документа через Groq"""
    
    # Сохрани временно
    with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file.filename.split('.')[-1]}") as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        file_type = file.filename.split(".")[-1].lower()
        result = await parser.parse_document_smart(tmp_path, file_type)
        
        # Форматируй для фронта (как сейчас в preview)
        preview = "\n".join([
            f"{p['pos']} | {p['name']} | {p['unit']} | {p['qty']}"
            for p in result["positions"]
        ])
        
        return {
            "preview": preview,
            "metadata": result.get("metadata", {}),
            "positions": result["positions"],
        }
    finally:
        # Очистка
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
