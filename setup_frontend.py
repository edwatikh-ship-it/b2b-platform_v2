#!/usr/bin/env python3
"""
B2B Platform Frontend Setup Script
Создаёт всю структуру фронтенда за раз
"""

import os
import json
import sys

# Определяем базовую папку
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(BASE_DIR, 'frontend')

def create_file(path: str, content: str) -> bool:
    """Создаёт файл с контентом"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"❌ Ошибка при создании {path}: {e}")
        return False

def main():
    print("🚀 B2B Platform Frontend Setup\n")
    
    files_to_create = {}
    
    # ================ ROOT FILES ================
    files_to_create['frontend/package.json'] = '''{
  "name": "b2b-platform-frontend",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "typescript": "^5.3.3",
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "axios": "^1.6.2",
    "lucide-react": "^0.298.0",
    "zustand": "^4.4.1"
  },
  "devDependencies": {
    "vite": "^5.0.8",
    "@vitejs/plugin-react": "^4.2.1"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "type-check": "tsc --noEmit"
  }
}'''

    files_to_create['frontend/index.html'] = '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>B2B Platform</title>
</head>
<body>
    <div id="root"></div>
    <script type="module" src="/src/main.tsx"></script>
</body>
</html>'''

    files_to_create['frontend/tsconfig.json'] = '''{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": true,
    "resolveJsonModule": true,
    "noImplicitAny": true,
    "moduleResolution": "bundler"
  },
  "include": ["src"],
  "exclude": ["node_modules"]
}'''

    files_to_create['frontend/vite.config.ts'] = '''import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})'''

    files_to_create['frontend/.env'] = '''VITE_API_URL=http://127.0.0.1:8000/api/v1
VITE_APP_NAME=B2B Platform'''

    files_to_create['frontend/.gitignore'] = '''node_modules/
dist/
build/
.DS_Store
*.log
.env.local
.env.*.local
*.swp
*.swo
*~
.idea/
.vscode/
.history/
.next/
out/'''

    # ================ SRC - MAIN FILES ================
    files_to_create['frontend/src/main.tsx'] = '''import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)'''

    files_to_create['frontend/src/index.css'] = '''* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html {
  font-size: 14px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.5;
  color: #1f2937;
  background-color: #f9fafb;
}

body {
  margin: 0;
  padding: 0;
}

button {
  cursor: pointer;
  border: none;
  font-family: inherit;
  transition: all 0.2s ease;
}

button:hover {
  opacity: 0.9;
}

input, textarea, select {
  font-family: inherit;
  font-size: inherit;
}

a {
  color: inherit;
  text-decoration: none;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
}

.btn {
  padding: 10px 16px;
  border-radius: 6px;
  font-weight: 500;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background-color: #2563eb;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #1d4ed8;
}

.btn-secondary {
  background-color: #e5e7eb;
  color: #1f2937;
}

.btn-secondary:hover:not(:disabled) {
  background-color: #d1d5db;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background-color: #dc2626;
}

.btn-success {
  background-color: #10b981;
  color: white;
}

.btn-success:hover:not(:disabled) {
  background-color: #059669;
}

.card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-label {
  display: block;
  margin-bottom: 6px;
  font-weight: 500;
  color: #374151;
  font-size: 14px;
}

.form-input, .form-textarea {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  font-size: 14px;
}

.form-input:focus, .form-textarea:focus {
  outline: none;
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 500;
}

.badge-primary {
  background-color: #dbeafe;
  color: #1e40af;
}

.badge-success {
  background-color: #dcfce7;
  color: #166534;
}

.badge-warning {
  background-color: #fef3c7;
  color: #92400e;
}

.badge-danger {
  background-color: #fee2e2;
  color: #991b1b;
}

.error-message {
  color: #dc2626;
  font-size: 12px;
  margin-top: 4px;
}

.alert-error {
  background-color: #fee2e2;
  color: #991b1b;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  border: 1px solid #fecaca;
}

.alert-success {
  background-color: #dcfce7;
  color: #166534;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
  border: 1px solid #bbf7d0;
}

.table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 16px;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

.table th {
  background-color: #f3f4f6;
  padding: 12px;
  text-align: left;
  font-weight: 600;
  border-bottom: 2px solid #e5e7eb;
}

.table td {
  padding: 12px;
  border-bottom: 1px solid #e5e7eb;
}

.table tr:hover {
  background-color: #f9fafb;
}

.loading {
  opacity: 0.6;
}

.text-center {
  text-align: center;
}

.mt-20 {
  margin-top: 20px;
}

.mb-20 {
  margin-bottom: 20px;
}

.gap-8 {
  gap: 8px;
}'''

    files_to_create['frontend/src/App.tsx'] = '''import React, { useState } from 'react'
import UserCabinet from './components/UserCabinet'
import ModeratorCabinet from './components/ModeratorCabinet'
import { useAppStore } from './stores/useAppStore'

function App() {
  const { activeTab, setActiveTab, error, success, setError, setSuccess } = useAppStore()

  return (
    <div style={styles.container}>
      <header style={styles.header}>
        <div style={styles.headerContent}>
          <h1 style={styles.title}>📊 B2B Platform</h1>
          <nav style={styles.nav}>
            <button
              style={{
                ...styles.navButton,
                ...(activeTab === 'user' ? styles.navButtonActive : {}),
              }}
              onClick={() => setActiveTab('user')}
            >
              👤 User Cabinet
            </button>
            <button
              style={{
                ...styles.navButton,
                ...(activeTab === 'moderator' ? styles.navButtonActive : {}),
              }}
              onClick={() => setActiveTab('moderator')}
            >
              🛡️ Moderator Cabinet
            </button>
          </nav>
        </div>
      </header>

      <main style={styles.main}>
        <div className="container">
          {error && (
            <div className="alert-error" onClick={() => setError(null)}>
              ❌ {error}
            </div>
          )}
          {success && (
            <div className="alert-success" onClick={() => setSuccess(null)}>
              ✅ {success}
            </div>
          )}

          {activeTab === 'user' && <UserCabinet />}
          {activeTab === 'moderator' && <ModeratorCabinet />}
        </div>
      </main>

      <footer style={styles.footer}>
        <p>© 2025 B2B Platform. Все права защищены.</p>
      </footer>
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    backgroundColor: '#f9fafb',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    backgroundColor: '#ffffff',
    borderBottom: '1px solid #e5e7eb',
    padding: '20px 0',
    boxShadow: '0 1px 3px rgba(0,0,0,0.05)',
  },
  headerContent: {
    maxWidth: '1200px',
    margin: '0 auto',
    padding: '0 20px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  title: {
    fontSize: '24px',
    fontWeight: 'bold',
    margin: 0,
    color: '#1f2937',
  },
  nav: {
    display: 'flex',
    gap: '12px',
  },
  navButton: {
    padding: '8px 16px',
    border: 'none',
    borderRadius: '6px',
    background: '#f3f4f6',
    cursor: 'pointer',
    fontWeight: 500,
    transition: 'all 0.2s',
    fontSize: '14px',
  },
  navButtonActive: {
    background: '#2563eb',
    color: 'white',
  },
  main: {
    padding: '40px 0',
    flex: 1,
  },
  footer: {
    textAlign: 'center',
    padding: '20px',
    borderTop: '1px solid #e5e7eb',
    backgroundColor: '#ffffff',
    color: '#6b7280',
    fontSize: '12px',
  },
}

export default App'''

    # ================ TYPES ================
    files_to_create['frontend/src/types/index.ts'] = '''export interface Request {
  id: number
  filename: string
  status: 'draft' | 'submitted' | 'moderation' | 'completed'
  items_count: number
  contacts_count: number
  created_at: string
}

export interface RequestItem {
  pos: number
  name: string
  unit: string
  qty: string | number
}

export interface Contact {
  supplier_name: string
  supplier_inn: string
  supplier_domain: string
  contact_name: string
  contact_phone: string
  contact_email: string
}

export interface ParsingTask {
  task_id: number
  request_id: number
  item_name: string
  search_query: string
  status: string
  created_at: string
}

export interface ParsedURL {
  id: number
  url: string
  title: string
  company_name: string
}

export interface Supplier {
  id: number
  domain: string
  company_name: string
  inn: string
  rating: number
}'''

    # ================ SERVICES ================
    files_to_create['frontend/src/services/api.ts'] = '''import axios from 'axios'
import { Request, ParsingTask, ParsedURL } from '../types'

const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000/api/v1'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// User Cabinet
export const uploadDocument = (file: File) => {
  const formData = new FormData()
  formData.append('file', file)
  return api.post('/user/upload-and-create', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
}

export const getRequests = (): Promise<Request[]> =>
  api.get('/user/requests').then(r => r.data)

export const getRequestDetail = (id: number) =>
  api.get(`/user/requests/${id}`).then(r => r.data)

export const submitRequest = (id: number) =>
  api.post(`/user/requests/${id}/submit`).then(r => r.data)

export const deleteRequest = (id: number) =>
  api.delete(`/user/requests/${id}`).then(r => r.data)

// Moderator Cabinet
export const getParsingTasks = (): Promise<ParsingTask[]> =>
  api.get('/moderator/tasks').then(r => r.data)

export const getTaskDetail = (id: number) =>
  api.get(`/moderator/tasks/${id}`).then(r => r.data)

export const startParsing = (requestId: number) =>
  api.post(`/moderator/requests/${requestId}/start-parsing`).then(r => r.data)

export const parseTask = (taskId: number, method: 'background_task' | 'celery' | 'patchright') =>
  api.post(`/moderator/tasks/${taskId}/parse`, { method }).then(r => r.data)

export const getTaskStatus = (id: number) =>
  api.get(`/moderator/tasks/${id}/status`).then(r => r.data)

export const moderateURL = (urlId: number, data: any) =>
  api.post(`/moderator/urls/${urlId}/moderate`, data).then(r => r.data)

// Suppliers
export const getSuppliers = (skip = 0, limit = 10) =>
  api.get('/suppliers/', { params: { skip, limit } }).then(r => r.data)

export const searchSuppliers = (q: string) =>
  api.get('/suppliers/search', { params: { q } }).then(r => r.data)

export const getSupplier = (id: number) =>
  api.get(`/suppliers/${id}`).then(r => r.data)'''

    # ================ STORES ================
    files_to_create['frontend/src/stores/useAppStore.ts'] = '''import { create } from 'zustand'

interface AppStore {
  activeTab: 'user' | 'moderator'
  setActiveTab: (tab: 'user' | 'moderator') => void
  loading: boolean
  setLoading: (loading: boolean) => void
  error: string | null
  setError: (error: string | null) => void
  success: string | null
  setSuccess: (success: string | null) => void
}

export const useAppStore = create<AppStore>((set) => ({
  activeTab: 'user',
  setActiveTab: (tab) => set({ activeTab: tab }),
  loading: false,
  setLoading: (loading) => set({ loading }),
  error: null,
  setError: (error) => {
    set({ error })
    if (error) setTimeout(() => set({ error: null }), 5000)
  },
  success: null,
  setSuccess: (success) => {
    set({ success })
    if (success) setTimeout(() => set({ success: null }), 5000)
  },
}))'''

    # ================ COMPONENTS ================
    files_to_create['frontend/src/components/UserCabinet.tsx'] = '''import React, { useState, useEffect } from 'react'
import { uploadDocument, getRequests, submitRequest, deleteRequest } from '../services/api'
import { useAppStore } from '../stores/useAppStore'
import { Request } from '../types'

export default function UserCabinet() {
  const [requests, setRequests] = useState<Request[]>([])
  const [loading, setLoading] = useState(false)
  const [file, setFile] = useState<File | null>(null)
  const { setError, setSuccess } = useAppStore()

  useEffect(() => {
    loadRequests()
    const interval = setInterval(loadRequests, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadRequests = async () => {
    try {
      const data = await getRequests()
      setRequests(data)
    } catch (err) {
      setError('Ошибка загрузки заявок')
    }
  }

  const handleUpload = async () => {
    if (!file) {
      setError('Выберите файл')
      return
    }
    try {
      setLoading(true)
      const result = await uploadDocument(file)
      setSuccess(`✅ Заявка #${result.request_id} создана (${result.items} позиций)`)
      setFile(null)
      await loadRequests()
    } catch (err) {
      setError('Ошибка загрузки файла')
    } finally {
      setLoading(false)
    }
  }

  const handleSubmit = async (id: number) => {
    try {
      await submitRequest(id)
      setSuccess('Заявка отправлена на модерацию')
      await loadRequests()
    } catch (err) {
      setError('Ошибка отправки заявки')
    }
  }

  const handleDelete = async (id: number) => {
    if (!confirm('Вы уверены? Заявка будет удалена безвозвратно.')) return
    try {
      await deleteRequest(id)
      setSuccess('Заявка удалена')
      await loadRequests()
    } catch (err) {
      setError('Ошибка удаления заявки')
    }
  }

  return (
    <div>
      <h2 style={{ marginBottom: '20px' }}>📋 Мои заявки</h2>

      <div className="card" style={styles.uploadCard}>
        <h3 style={{ marginBottom: '12px' }}>Загрузить документ</h3>
        <p style={{ fontSize: '12px', color: '#6b7280', marginBottom: '12px' }}>
          Поддерживаемые форматы: PDF, DOCX, XLSX
        </p>
        <input
          type="file"
          accept=".pdf,.docx,.xlsx"
          onChange={(e) => setFile(e.target.files?.[0] || null)}
          style={styles.fileInput}
        />
        {file && <p style={{ fontSize: '12px', color: '#059669', marginBottom: '12px' }}>✅ {file.name}</p>}
        <button
          onClick={handleUpload}
          disabled={loading || !file}
          style={{
            ...styles.button,
            opacity: loading || !file ? 0.6 : 1,
          }}
        >
          {loading ? '⏳ Загрузка...' : '📤 Загрузить'}
        </button>
      </div>

      <h3 style={{ marginTop: '40px', marginBottom: '16px' }}>Список заявок</h3>

      {requests.length === 0 ? (
        <p style={{ color: '#6b7280' }}>Нет заявок. Загрузите документ для начала работы.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>№</th>
                <th>Файл</th>
                <th>Статус</th>
                <th>Позиции</th>
                <th>Контакты</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {requests.map((req) => (
                <tr key={req.id}>
                  <td>{req.id}</td>
                  <td>{req.filename}</td>
                  <td>
                    <span className={`badge badge-${getStatusBadge(req.status)}`}>
                      {req.status}
                    </span>
                  </td>
                  <td>{req.items_count}</td>
                  <td>{req.contacts_count}</td>
                  <td style={{ display: 'flex', gap: '8px' }}>
                    {req.status === 'draft' && (
                      <>
                        <button
                          onClick={() => handleSubmit(req.id)}
                          className="btn btn-primary"
                          style={{ padding: '6px 12px', fontSize: '12px' }}
                        >
                          Отправить
                        </button>
                        <button
                          onClick={() => handleDelete(req.id)}
                          className="btn btn-danger"
                          style={{ padding: '6px 12px', fontSize: '12px' }}
                        >
                          Удалить
                        </button>
                      </>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  uploadCard: {
    background: 'white',
    padding: '20px',
    borderRadius: '8px',
  },
  fileInput: {
    width: '100%',
    padding: '10px',
    border: '2px dashed #d1d5db',
    borderRadius: '6px',
    marginBottom: '12px',
    cursor: 'pointer',
  },
  button: {
    padding: '10px 16px',
    background: '#2563eb',
    color: 'white',
    border: 'none',
    borderRadius: '6px',
    cursor: 'pointer',
    fontWeight: 500,
  },
}

function getStatusBadge(status: string): string {
  switch (status) {
    case 'draft': return 'primary'
    case 'submitted': return 'warning'
    case 'moderation': return 'warning'
    case 'completed': return 'success'
    default: return 'primary'
  }
}'''

    files_to_create['frontend/src/components/ModeratorCabinet.tsx'] = '''import React, { useState, useEffect } from 'react'
import { getParsingTasks, parseTask, getTaskStatus } from '../services/api'
import { useAppStore } from '../stores/useAppStore'
import { ParsingTask } from '../types'

export default function ModeratorCabinet() {
  const [tasks, setTasks] = useState<ParsingTask[]>([])
  const [loading, setLoading] = useState(false)
  const [selectedMethod, setSelectedMethod] = useState<'background_task' | 'celery' | 'patchright'>('background_task')
  const [statusMap, setStatusMap] = useState<Record<number, any>>({})
  const { setError, setSuccess } = useAppStore()

  useEffect(() => {
    loadTasks()
    const interval = setInterval(loadTasks, 3000)
    return () => clearInterval(interval)
  }, [])

  const loadTasks = async () => {
    try {
      const data = await getParsingTasks()
      setTasks(data)
      
      // Загружаем статусы
      for (const task of data) {
        if (task.status === 'pending') {
          const status = await getTaskStatus(task.task_id)
          setStatusMap(prev => ({ ...prev, [task.task_id]: status }))
        }
      }
    } catch (err) {
      setError('Ошибка загрузки задач')
    }
  }

  const handleParse = async (taskId: number) => {
    try {
      setLoading(true)
      await parseTask(taskId, selectedMethod)
      setSuccess(`✅ Парсинг запущен методом: ${selectedMethod}`)
      setTimeout(() => loadTasks(), 2000)
    } catch (err) {
      setError('Ошибка парсинга')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div>
      <h2 style={{ marginBottom: '20px' }}>🛡️ Модерация</h2>

      <div className="card" style={styles.methodCard}>
        <h3 style={{ marginBottom: '16px' }}>Выберите метод парсинга</h3>
        <div style={{ marginBottom: '16px' }}>
          {(['background_task', 'celery', 'patchright'] as const).map((method) => (
            <label key={method} style={{ display: 'block', marginBottom: '10px', cursor: 'pointer' }}>
              <input
                type="radio"
                value={method}
                checked={selectedMethod === method}
                onChange={(e) => setSelectedMethod(e.target.value as any)}
                style={{ marginRight: '8px', cursor: 'pointer' }}
              />
              <strong>{method}</strong>
              <div style={{ fontSize: '12px', color: '#6b7280', marginLeft: '24px' }}>
                {method === 'background_task' && '⚡ Встроено в FastAPI (быстро, просто)'}
                {method === 'celery' && '📦 Очередь Redis (надёжно, масштабируется)'}
                {method === 'patchright' && '🛡️ Лучше обходит капчу Яндекса'}
              </div>
            </label>
          ))}
        </div>
      </div>

      <h3 style={{ marginTop: '40px', marginBottom: '16px' }}>Задачи на парсинг</h3>

      {tasks.length === 0 ? (
        <p style={{ color: '#6b7280' }}>Нет задач на парсинг. Загрузите заявку в User Cabinet и отправьте на модерацию.</p>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="table">
            <thead>
              <tr>
                <th>ID</th>
                <th>Позиция</th>
                <th>Запрос</th>
                <th>Статус</th>
                <th>Найдено ссылок</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {tasks.map((task) => {
                const status = statusMap[task.task_id] || {}
                return (
                  <tr key={task.task_id}>
                    <td>{task.task_id}</td>
                    <td>{task.item_name}</td>
                    <td style={{ maxWidth: '300px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                      {task.search_query}
                    </td>
                    <td>
                      <span className={`badge badge-${getStatusBadge(task.status)}`}>
                        {task.status}
                      </span>
                    </td>
                    <td>{status.urls_found || 0}</td>
                    <td>
                      <button
                        onClick={() => handleParse(task.task_id)}
                        disabled={loading}
                        className="btn btn-primary"
                        style={{ padding: '6px 12px', fontSize: '12px', opacity: loading ? 0.6 : 1 }}
                      >
                        {loading ? '⏳' : '🔍'} Парсить
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

const styles: Record<string, React.CSSProperties> = {
  methodCard: {
    background: 'white',
    padding: '20px',
    borderRadius: '8px',
  },
}

function getStatusBadge(status: string): string {
  switch (status) {
    case 'pending': return 'warning'
    case 'approved': return 'success'
    case 'rejected': return 'danger'
    case 'needs_review': return 'primary'
    default: return 'primary'
  }
}'''

    # ================ .gitkeep файлы для пустых папок ================
    files_to_create['frontend/src/components/.gitkeep'] = ''
    files_to_create['frontend/src/services/.gitkeep'] = ''
    files_to_create['frontend/src/stores/.gitkeep'] = ''
    files_to_create['frontend/src/types/.gitkeep'] = ''

    # Создаём все файлы
    created_count = 0
    failed_count = 0

    for file_path, content in files_to_create.items():
        full_path = os.path.join(BASE_DIR, file_path)
        if create_file(full_path, content):
            print(f"✅ {file_path}")
            created_count += 1
        else:
            failed_count += 1

    print(f"\n{'='*60}")
    print(f"✅ Создано: {created_count} файлов")
    if failed_count > 0:
        print(f"❌ Ошибок: {failed_count}")
    print(f"{'='*60}\n")

    print("🎉 Фронтенд структура полностью создана!\n")
    print("Следующие шаги:")
    print("  1. cd frontend")
    print("  2. npm install")
    print("  3. npm run dev")
    print("\nОткрой http://localhost:3000 в браузере!")

if __name__ == '__main__':
    main()
