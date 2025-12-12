import React, { useState, useEffect } from 'react'
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
}