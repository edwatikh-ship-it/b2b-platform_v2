from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List
import json
import asyncio
import logging

from app.database import get_db
from app.models import (
    Request,
    RequestStatus,
    URLStatus,
    ParsingTask,
    ParsedURL,
    ModeratedURL,
    Supplier,
    Contact,
    SearchResultFromDB,
)
from app.services.parser import search_suppliers
from pydantic import BaseModel

router = APIRouter()
logger = logging.getLogger(__name__)


# ---- Pydantic Models ----
class ParsedURLOut(BaseModel):
    id: int
    url: str
    title: str
    company_name: str

    class Config:
        from_attributes = True


class ParsingTaskOut(BaseModel):
    id: int
    item_id: int
    search_query: str
    status: str
    created_at: str

    class Config:
        from_attributes = True


class ModerateURLRequest(BaseModel):
    status: str  # "approved" или "rejected"
    inn: str = None
    checko_data: dict = None
    contact_info: dict = None


class ParseRequest(BaseModel):
    method: str  # "background_task", "celery", или "patchright"


# ---- BACKGROUND TASK (встроено в FastAPI) ----
async def _parse_task_background(task_id: int, db_path: str = "b2b_platform.db"):
    """Парсинг в фоновом потоке (FastAPI BackgroundTasks)"""
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        task = db.query(ParsingTask).filter(ParsingTask.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        task.status = URLStatus.PENDING
        task.started_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"[BACKGROUND] Запуск парсинга для задачи {task_id}: {task.search_query}")
        
        # Запускаем парсер
        urls = asyncio.run(search_suppliers(task.search_query, pages=2))
        
        # Сохраняем результаты
        for url in urls:
            parsed_url = ParsedURL(
                task_id=task.id,
                url=url,
                title="",
                company_name="",
            )
            db.add(parsed_url)
        
        task.status = URLStatus.APPROVED
        task.completed_at = datetime.utcnow()
        task.result_json = json.dumps({"urls": list(urls)})
        db.commit()
        
        logger.info(f"[BACKGROUND] ✅ Парсинг завершён для задачи {task_id}: {len(urls)} ссылок")
    
    except Exception as e:
        logger.error(f"[BACKGROUND] ❌ Ошибка парсинга задачи {task_id}: {e}")
        task = db.query(ParsingTask).filter(ParsingTask.id == task_id).first()
        if task:
            task.status = URLStatus.NEEDS_REVIEW
            db.commit()
    
    finally:
        db.close()


# ---- CELERY TASK ----
try:
    from app.celery_app import celery_app
    
    @celery_app.task(bind=True)
    def _parse_task_celery(self, task_id: int):
        """Парсинг через Celery (очередь Redis)"""
        from app.database import SessionLocal
        
        db = SessionLocal()
        try:
            task = db.query(ParsingTask).filter(ParsingTask.id == task_id).first()
            if not task:
                logger.error(f"Task {task_id} not found")
                return {"status": "error", "message": "Task not found"}
            
            task.status = URLStatus.PENDING
            task.started_at = datetime.utcnow()
            db.commit()
            
            logger.info(f"[CELERY] Запуск парсинга для задачи {task_id}: {task.search_query}")
            
            # Запускаем парсер
            urls = asyncio.run(search_suppliers(task.search_query, pages=2))
            
            # Сохраняем результаты
            for url in urls:
                parsed_url = ParsedURL(
                    task_id=task.id,
                    url=url,
                    title="",
                    company_name="",
                )
                db.add(parsed_url)
            
            task.status = URLStatus.APPROVED
            task.completed_at = datetime.utcnow()
            task.result_json = json.dumps({"urls": list(urls)})
            db.commit()
            
            logger.info(f"[CELERY] ✅ Парсинг завершён для задачи {task_id}: {len(urls)} ссылок")
            return {"status": "success", "urls_count": len(urls)}
        
        except Exception as e:
            logger.error(f"[CELERY] ❌ Ошибка парсинга задачи {task_id}: {e}")
            task = db.query(ParsingTask).filter(ParsingTask.id == task_id).first()
            if task:
                task.status = URLStatus.NEEDS_REVIEW
                db.commit()
            return {"status": "error", "message": str(e)}
        
        finally:
            db.close()

except ImportError:
    logger.warning("Celery не установлен, используй 'background_task' или 'patchright'")
    _parse_task_celery = None


# ---- PATCHRIGHT TASK ----
async def _parse_task_patchright(task_id: int, db_path: str = "b2b_platform.db"):
    """Парсинг с использованием Patchright (лучше от капчи)"""
    from app.database import SessionLocal
    
    try:
        import patchright
    except ImportError:
        logger.error("Patchright не установлен")
        return {"status": "error", "message": "Patchright не установлен"}
    
    db = SessionLocal()
    try:
        task = db.query(ParsingTask).filter(ParsingTask.id == task_id).first()
        if not task:
            logger.error(f"Task {task_id} not found")
            return
        
        task.status = URLStatus.PENDING
        task.started_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"[PATCHRIGHT] Запуск парсинга для задачи {task_id}: {task.search_query}")
        
        # Импортируем парсер Patchright версию (или используем Playwright с Patchright)
        # Здесь используем обычный парсер, но можешь заменить на patchright-специфичный
        urls = await search_suppliers(task.search_query, pages=2)
        
        # Сохраняем результаты
        for url in urls:
            parsed_url = ParsedURL(
                task_id=task.id,
                url=url,
                title="",
                company_name="",
            )
            db.add(parsed_url)
        
        task.status = URLStatus.APPROVED
        task.completed_at = datetime.utcnow()
        task.result_json = json.dumps({"urls": list(urls)})
        db.commit()
        
        logger.info(f"[PATCHRIGHT] ✅ Парсинг завершён для задачи {task_id}: {len(urls)} ссылок")
        return {"status": "success", "urls_count": len(urls)}
    
    except Exception as e:
        logger.error(f"[PATCHRIGHT] ❌ Ошибка парсинга задачи {task_id}: {e}")
        task = db.query(ParsingTask).filter(ParsingTask.id == task_id).first()
        if task:
            task.status = URLStatus.NEEDS_REVIEW
            db.commit()
        return {"status": "error", "message": str(e)}
    
    finally:
        db.close()


# ================ ENDPOINTS ================

@router.get("/tasks")
async def list_parsing_tasks(db: Session = Depends(get_db)):
    """Список всех задач на парсинг (для модератора)"""
    tasks = db.query(ParsingTask).filter(
        ParsingTask.status == URLStatus.PENDING
    ).all()

    return [
        {
            "task_id": t.id,
            "request_id": t.request_id,
            "item_name": t.item.name,
            "search_query": t.search_query,
            "status": t.status.value,
            "created_at": t.created_at.isoformat(),
        }
        for t in tasks
    ]


@router.get("/tasks/{task_id}")
async def get_task_detail(task_id: int, db: Session = Depends(get_db)):
    """Детали задачи + найденные URL"""
    task = db.query(ParsingTask).filter(ParsingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    urls = [
        {
            "id": u.id,
            "url": u.url,
            "title": u.title,
            "company_name": u.company_name,
        }
        for u in task.parsed_urls
    ]

    return {
        "task_id": task.id,
        "request_id": task.request_id,
        "item_name": task.item.name,
        "search_query": task.search_query,
        "status": task.status.value,
        "urls": urls,
    }


@router.post("/requests/{request_id}/start-parsing")
async def start_parsing(request_id: int, db: Session = Depends(get_db)):
    """Запустить парсинг по всем позициям заявки"""
    request = db.query(Request).filter(Request.id == request_id).first()
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")

    # Обновляем статус
    request.status = RequestStatus.MODERATION
    db.commit()

    # Для каждого item создаём ParsingTask
    for item in request.items:
        search_query = f"{item.name} купить"

        task = ParsingTask(
            request_id=request.id,
            item_id=item.id,
            search_query=search_query,
            status=URLStatus.PENDING,
        )
        db.add(task)

    db.commit()

    return {
        "status": "success",
        "request_id": request_id,
        "tasks_created": len(request.items),
    }


@router.post("/tasks/{task_id}/parse")
async def parse_task(
    task_id: int,
    payload: ParseRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """
    Запустить парсинг для конкретной задачи.
    
    Методы:
    - background_task: FastAPI BackgroundTasks (встроено)
    - celery: Celery очередь (нужен Redis)
    - patchright: Patchright вместо Playwright (лучше от капчи)
    """
    task = db.query(ParsingTask).filter(ParsingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    method = payload.method.lower()

    if method == "background_task":
        # FastAPI BackgroundTasks (встроено, без зависимостей)
        logger.info(f"[API] Запуск парсинга методом: background_task")
        background_tasks.add_task(_parse_task_background, task_id)
        
        return {
            "status": "started",
            "task_id": task_id,
            "method": "background_task",
            "message": "Парсинг запущен в фоновом потоке (FastAPI)",
        }

    elif method == "celery":
        # Celery (асинхронная очередь с Redis)
        if _parse_task_celery is None:
            raise HTTPException(status_code=503, detail="Celery не установлен")
        
        logger.info(f"[API] Запуск парсинга методом: celery")
        celery_task = _parse_task_celery.delay(task_id)
        
        return {
            "status": "queued",
            "task_id": task_id,
            "celery_task_id": celery_task.id,
            "method": "celery",
            "message": "Задача добавлена в очередь Celery",
        }

    elif method == "patchright":
        # Patchright (асинхронный, лучше от капчи)
        logger.info(f"[API] Запуск парсинга методом: patchright")
        background_tasks.add_task(_parse_task_patchright, task_id)
        
        return {
            "status": "started",
            "task_id": task_id,
            "method": "patchright",
            "message": "Парсинг запущен с Patchright (лучше обходит капчу)",
        }

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Неизвестный метод: {method}. Используй: 'background_task', 'celery', или 'patchright'",
        )


@router.get("/tasks/{task_id}/status")
async def get_task_status(task_id: int, db: Session = Depends(get_db)):
    """Получить статус задачи парсинга"""
    task = db.query(ParsingTask).filter(ParsingTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task.id,
        "status": task.status.value,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed_at": task.completed_at.isoformat() if task.completed_at else None,
        "urls_found": len(task.parsed_urls),
    }


@router.post("/urls/{url_id}/moderate")
async def moderate_url(
    url_id: int,
    payload: ModerateURLRequest,
    db: Session = Depends(get_db),
):
    """Модерировать найденную ссылку"""
    parsed_url = db.query(ParsedURL).filter(ParsedURL.id == url_id).first()
    if not parsed_url:
        raise HTTPException(status_code=404, detail="URL not found")

    # Создаём или обновляем ModeratedURL
    moderated = parsed_url.moderated
    if not moderated:
        moderated = ModeratedURL(parsed_url_id=parsed_url.id, url=parsed_url.url)
        db.add(moderated)
        db.flush()

    moderated.status = payload.status
    moderated.inn = payload.inn
    moderated.checko_data = json.dumps(payload.checko_data) if payload.checko_data else None
    moderated.contact_info = json.dumps(payload.contact_info) if payload.contact_info else None
    moderated.moderated_at = datetime.utcnow()

    # Если одобрено: создаём Supplier + Contact и добавляем в search_results
    if payload.status == "approved" and payload.inn:
        supplier = db.query(Supplier).filter(Supplier.domain == parsed_url.url).first()
        if not supplier:
            supplier = Supplier(
                domain=parsed_url.url,
                company_name=payload.contact_info.get("company_name") if payload.contact_info else "",
                inn=payload.inn,
                source="parsing",
            )
            db.add(supplier)
            db.flush()

        contact = Contact(
            supplier_id=supplier.id,
            name=payload.contact_info.get("name") if payload.contact_info else "",
            phone=payload.contact_info.get("phone") if payload.contact_info else "",
            email=payload.contact_info.get("email") if payload.contact_info else "",
            source="parsing",
        )
        db.add(contact)
        db.flush()

        # Добавляем в search_results для передачи пользователю
        search_result = SearchResultFromDB(
            request_id=parsed_url.task.request_id,
            item_id=parsed_url.task.item_id,
            supplier_id=supplier.id,
            contact_id=contact.id,
            source="parsing",
        )
        db.add(search_result)

    db.commit()

    return {
        "status": "success",
        "url_id": url_id,
        "moderation_status": payload.status,
    }
