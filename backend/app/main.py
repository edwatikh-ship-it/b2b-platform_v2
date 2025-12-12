from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import documents, suppliers, requests, user, moderator

# Создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="B2B Platform API", version="0.2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(suppliers.router, prefix="/api/v1/suppliers", tags=["Suppliers"])
app.include_router(requests.router, prefix="/api/v1/requests", tags=["Requests"])
app.include_router(user.router, prefix="/api/v1/user", tags=["User Cabinet"])
app.include_router(moderator.router, prefix="/api/v1/moderator", tags=["Moderator Cabinet"])


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.2.0"}
