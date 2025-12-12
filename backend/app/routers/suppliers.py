from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Supplier, Contact
from pydantic import BaseModel
from typing import List

router = APIRouter()


class ContactInfo(BaseModel):
    id: int
    name: str
    phone: str
    email: str
    position: str

    class Config:
        from_attributes = True


class SupplierInfo(BaseModel):
    id: int
    domain: str
    company_name: str
    inn: str
    rating: float
    contacts: List[ContactInfo]

    class Config:
        from_attributes = True


@router.get("/search")
async def search_suppliers(q: str, db: Session = Depends(get_db)):
    """Поиск поставщиков по названию или домену"""
    suppliers = (
        db.query(Supplier)
        .filter(
            (Supplier.company_name.ilike(f"%{q}%")) | (Supplier.domain.ilike(f"%{q}%"))
        )
        .limit(10)
        .all()
    )

    return [
        {
            "id": s.id,
            "domain": s.domain,
            "company_name": s.company_name,
            "inn": s.inn,
            "rating": s.rating,
            "contacts_count": len(s.contacts),
        }
        for s in suppliers
    ]


@router.get("/{supplier_id}")
async def get_supplier(supplier_id: int, db: Session = Depends(get_db)):
    """Получить полную информацию о поставщике"""
    supplier = db.query(Supplier).filter(Supplier.id == supplier_id).first()
    if not supplier:
        raise HTTPException(status_code=404, detail="Supplier not found")

    return {
        "id": supplier.id,
        "domain": supplier.domain,
        "company_name": supplier.company_name,
        "inn": supplier.inn,
        "rating": supplier.rating,
        "source": supplier.source,
        "created_at": supplier.created_at.isoformat(),
        "contacts": [
            {
                "id": c.id,
                "name": c.name,
                "phone": c.phone,
                "email": c.email,
                "position": c.position,
            }
            for c in supplier.contacts
        ],
    }


@router.get("/")
async def list_suppliers(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Список всех поставщиков"""
    suppliers = db.query(Supplier).offset(skip).limit(limit).all()

    return [
        {
            "id": s.id,
            "domain": s.domain,
            "company_name": s.company_name,
            "inn": s.inn,
            "rating": s.rating,
        }
        for s in suppliers
    ]
