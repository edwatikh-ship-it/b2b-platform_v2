from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from typing import List
import json

from app.database import get_db
from app.models import Request, RequestItem, SearchResultFromDB, RequestStatus
from app.services.document_parser import DocumentParser
from pydantic import BaseModel

router = APIRouter()


# ---- Pydantic Models ----
class RequestItemOut(BaseModel):
    pos: int
    name: str
    unit: str
    qty: float | str


class ContactOut(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    position: str

    class Config:
        from_attributes = True


class SupplierOut(BaseModel):
    id: int
    company_name: str
    inn: str
    domain: str
    rating: float

    class Config:
        from_attributes = True


class SearchResultOut(BaseModel):
    supplier: SupplierOut
    contact: ContactOut

    class Config:
        from_attributes = True


class RequestOut(BaseModel):
    id: int
    filename: str
    status: str
    items: List[RequestItemOut]
    created_at: str

    class Config:
        from_attributes = True


class RequestDetailOut(BaseModel):
    id: int
    filename: str
    status: str
    items: List[RequestItemOut]
    search_results: List[SearchResultOut]
    created_at: str

    class Config:
        from_attributes = True


# ---- Endpoints ----

@router.post("/upload-and-create")
async def upload_and_create_request(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Загрузить документ + распознать + создать Request + найти контакты из БД"""
    filename = file.filename or ""
    ext = "." + filename.split(".")[-1].lower()

    if ext not in [".pdf", ".docx", ".xlsx"]:
        raise HTTPException(status_code=400, detail="Поддерживаются только PDF/DOCX/XLSX")

    data = await file.read()
    parser = DocumentParser()

    if ext == ".pdf":
        text = parser.parse_pdf_bytes(data)
    elif ext == ".docx":
        text = parser.parse_docx_bytes(data)
    else:
        text = parser.parse_xlsx_bytes(data)

    # Парсим items из текста
    import re
    items = []
    for line in text.splitlines():
        if " | " not in line:
            continue
        parts = [p.strip() for p in line.split("|")]
        if len(parts) < 4:
            continue
        if not re.fullmatch(r"\d+", parts[0]):
            continue

        name = parts[1]
        unit = parts[2]
        qty_raw = parts[3].replace(",", ".").strip()

        try:
            qty = float(qty_raw)
            if qty.is_integer():
                qty = int(qty)
        except:
            qty = qty_raw

        items.append({"pos": int(parts[0]), "name": name, "unit": unit, "qty": qty})

    # Создаём Request
    request = Request(filename=filename, status=RequestStatus.DRAFT)
    db.add(request)
    db.flush()

    # Добавляем items
    for item_data in items:
        item = RequestItem(
            request_id=request.id,
            pos=item_data["pos"],
            name=item_data["name"],
            unit=item_data["unit"],
            qty=item_data["qty"],
        )
        db.add(item)
    db.flush()

    # Ищем контакты в БД для каждого item (простой поиск по названию)
    for item in request.items:
        # Берём ключевые слова из названия товара
        keywords = item.name.lower().split()[:2]  # Первые 2 слова

        # Ищем в suppliers по company_name
        suppliers = db.query(SearchResultFromDB.__table__.c.supplier_id).distinct()
        # Пока простой вариант: просто берём первых поставщиков
        from sqlalchemy import func, or_
        from app.models import Supplier, Contact

        suppliers_found = (
            db.query(Supplier, Contact)
            .join(Contact, Supplier.id == Contact.supplier_id)
            .limit(3)
            .all()
        )

        for supplier, contact in suppliers_found:
            result = SearchResultFromDB(
                request_id=request.id,
                item_id=item.id,
                supplier_id=supplier.id,
                contact_id=contact.id,
                source="database",
            )
            db.add(result)

    db.commit()

    return {
        "status": "success",
        "request_id": request.id,
        "filename": filename,
        "items": len(items),
        "db_contacts_found": len(request.search_results),
    }


@router.get("/requests")
async def list_requests(db: Session = Depends(get_db)):
    """Список всех Request пользователя (draft + submitted)"""
    requests = db.query(Request).filter(
        Request.status.in_([RequestStatus.DRAFT, RequestStatus.SUBMITTED])
    ).all()

    return [
        {
            "id": r.id,
            "filename": r.filename,
            "status": r.status.value,
            "items_count": len(r.items),
            "contacts_count": len(r.search_results),
            "created_at": r.created_at.isoformat(),
        }
        for r in requests
    ]


@router.get("/requests/{request_id}")
async def get_request_detail(request_id: int, db: Session = Depends(get_db)):
    """Детали заявки + контакты из БД"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    items = [
        {
            "pos": item.pos,
            "name": item.name,
            "unit": item.unit,
            "qty": str(item.qty) if item.qty else None,
        }
        for item in request.items
    ]

    contacts = []
    for result in request.search_results:
        contacts.append(
            {
                "supplier_name": result.supplier.company_name,
                "supplier_inn": result.supplier.inn,
                "supplier_domain": result.supplier.domain,
                "contact_name": result.contact.name,
                "contact_phone": result.contact.phone,
                "contact_email": result.contact.email,
            }
        )

    return {
        "id": request.id,
        "filename": request.filename,
        "status": request.status.value,
        "items": items,
        "db_contacts": contacts,
        "created_at": request.created_at.isoformat(),
    }


@router.post("/requests/{request_id}/submit")
async def submit_request(request_id: int, db: Session = Depends(get_db)):
    """Отправить заявку на модерацию (статус: submitted → moderation)"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    request.status = RequestStatus.SUBMITTED
    db.commit()

    return {
        "status": "success",
        "request_id": request.id,
        "new_status": request.status.value,
    }


@router.delete("/requests/{request_id}")
async def delete_request(request_id: int, db: Session = Depends(get_db)):
    """Удалить заявку"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    db.delete(request)
    db.commit()

    return {"status": "success", "deleted_id": request_id}
