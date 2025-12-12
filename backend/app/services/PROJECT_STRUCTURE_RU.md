# B2B Platform — как устроен проект (RU)

## 1) Что это
B2B Platform — платформа с 2 кабинетами:
- **Пользователь**: загружает документ → создаётся заявка (request).
- **Модератор**: видит заявки/задачи и запускает парсинг.

## 2) Главная мысль (почему было 404)
Backend уже реализован как **версионированное API** с префиксом **/api/v1**.
Поэтому запросы в /api/... дают 404, потому что правильные пути начинаются с /api/v1/...

## 3) Быстрые ссылки (dev)
- Backend health: http://127.0.0.1:8000/health
- Swagger: http://127.0.0.1:8000/docs
- OpenAPI JSON: http://127.0.0.1:8000/openapi.json

## 4) Контракт API (актуальный)

### Пользователь
- POST /api/v1/user/upload-and-create
  - multipart/form-data, поле: file
  - результат: создаёт request
- GET /api/v1/user/requests
  - список заявок
- GET /api/v1/user/requests/{request_id}
  - детали заявки
- POST /api/v1/user/requests/{request_id}/submit
  - отправка/фиксация заявки
- DELETE /api/v1/user/requests/{request_id}
  - удаление заявки

### Модератор
- GET /api/v1/moderator/tasks
  - список задач парсинга
- POST /api/v1/moderator/requests/{request_id}/start-parsing
  - старт парсинга по заявке
- GET /api/v1/moderator/tasks/{task_id}/status
  - статус/прогресс

## 5) Frontend (как должен работать)
Frontend отображает 2 вкладки:
- User Cabinet:
  - кнопка загрузки файла → POST /api/v1/user/upload-and-create
  - вывод списка заявок → GET /api/v1/user/requests
- Moderator Cabinet:
  - вывод задач → GET /api/v1/moderator/tasks
  - (дальше) старт парсинга выбранной заявки → POST /api/v1/moderator/requests/{request_id}/start-parsing

## 6) Структура проекта (типовая)
b2b-platform/
  backend/
    app/
      main.py              # FastAPI app + подключение роутеров /api/v1/...
      api/                 # роутеры v1 (documents, user, moderator, requests, suppliers)
      services/            # бизнес-логика
      models/              # модели/схемы
  frontend/
    src/
      App.tsx              # UI + вкладки
      ...components
    vite.config.ts
    package.json

## 7) Как запускать (dev)

### Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

### Frontend
cd frontend
npm run dev

## 8) Типовые ошибки
- 404 на /api/upload → нужно /api/v1/user/upload-and-create
- CORS ошибки → добавить CORSMiddleware и разрешить origin фронта (localhost:3000/5173)
- localhost:3000 не открывается → Vite не запущен или порт занят
