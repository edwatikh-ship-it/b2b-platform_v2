import React, { useState, useEffect } from 'react'
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
}