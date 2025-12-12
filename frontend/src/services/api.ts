import axios from 'axios'
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
  api.get(`/suppliers/${id}`).then(r => r.data)