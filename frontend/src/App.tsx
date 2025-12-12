import React, { useState, useEffect } from 'react';

interface Position {
  pos: number;
  name: string;
  unit: string;
  qty: number;
}

interface Supplier {
  id: number;
  name: string;
  inn: string;
  url: string;
  rating: number;
}

interface Request {
  id: number;
  filename: string;
  status: string;
  items: Position[];
  parsing_confidence: number;
  db_contacts: any[];
}

interface Task {
  id: number;
  request_id: number;
  filename: string;
  status: string;
  items_count: number;
  confidence: number;
}

export default function App() {
  const [cabinet, setCabinet] = useState<'user' | 'moderator'>('user');
  const [requests, setRequests] = useState<Request[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [selectedRequest, setSelectedRequest] = useState<Request | null>(null);
  const [selectedTask, setSelectedTask] = useState<any>(null);
  const [expandedPositions, setExpandedPositions] = useState<Set<number>>(new Set());
  const [positionSuppliers, setPositionSuppliers] = useState<Record<number, Supplier[]>>({});
  const [loading, setLoading] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const API_URL = 'http://127.0.0.1:8000/api/v1';

  // ============ USER CABINET ============

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (!selectedFile) return;

    setFile(selectedFile);
    setLoading(true);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch(`${API_URL}/user/upload-and-create`, {
        method: 'POST',
        body: formData,
      });
      const data = await response.json();
      
      if (data.success) {
        fetchUserRequests();
      }
    } catch (error) {
      console.error('Upload error:', error);
      alert('Ошибка загрузки файла');
    } finally {
      setLoading(false);
      e.target.value = '';
    }
  };

  const fetchUserRequests = async () => {
    try {
      const response = await fetch(`${API_URL}/user/requests`);
      const data = await response.json();
      setRequests(data);
    } catch (error) {
      console.error('Fetch error:', error);
    }
  };

  const handleRequestClick = async (request: Request) => {
    const response = await fetch(`${API_URL}/user/requests/${request.id}`);
    const data = await response.json();
    setSelectedRequest(data);
    setExpandedPositions(new Set());
  };

  const handleSubmitRequest = async (requestId: number) => {
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/user/requests/${requestId}/submit`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (data.success) {
        fetchUserRequests();
        if (selectedRequest?.id === requestId) {
          const updatedRequest = await fetch(`${API_URL}/user/requests/${requestId}`);
          const updatedData = await updatedRequest.json();
          setSelectedRequest(updatedData);
        }
      }
    } catch (error) {
      console.error('Submit error:', error);
      alert('Ошибка отправки заявки');
    } finally {
      setLoading(false);
    }
  };

  const searchSuppliers = async (positionId: number, positionName: string) => {
    try {
      const response = await fetch(`${API_URL}/suppliers/search?keyword=${encodeURIComponent(positionName)}`);
      const data = await response.json();
      setPositionSuppliers(prev => ({
        ...prev,
        [positionId]: data.results || []
      }));
    } catch (error) {
      console.error('Search error:', error);
    }
  };

  const togglePositionExpand = async (positionId: number, positionName: string) => {
    const newExpanded = new Set(expandedPositions);
    
    if (newExpanded.has(positionId)) {
      newExpanded.delete(positionId);
    } else {
      newExpanded.add(positionId);
      // Ищем поставщиков для этой позиции, только если их ещё нет
      if (!positionSuppliers[positionId]) {
        await searchSuppliers(positionId, positionName);
      }
    }
    
    setExpandedPositions(newExpanded);
  };

  // ============ MODERATOR CABINET ============

  const fetchModeratorTasks = async () => {
    try {
      const response = await fetch(`${API_URL}/moderator/tasks`);
      const data = await response.json();
      setTasks(data);
    } catch (error) {
      console.error('Fetch tasks error:', error);
    }
  };

  const handleTaskClick = async (task: Task) => {
    const response = await fetch(`${API_URL}/moderator/tasks/${task.id}`);
    const data = await response.json();
    setSelectedTask(data);
    setExpandedPositions(new Set());
  };

  const handleApproveTask = async (taskId: number) => {
    try {
      const response = await fetch(`${API_URL}/moderator/tasks/${taskId}/approve`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (data.success) {
        fetchModeratorTasks();
        setSelectedTask(null);
      }
    } catch (error) {
      console.error('Approve error:', error);
      alert('Ошибка одобрения');
    }
  };

  const handleRejectTask = async (taskId: number) => {
    const reason = prompt('Причина отклонения:');
    if (!reason) return;

    try {
      const response = await fetch(`${API_URL}/moderator/tasks/${taskId}/reject`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ reason }),
      });
      const data = await response.json();
      
      if (data.success) {
        fetchModeratorTasks();
        setSelectedTask(null);
      }
    } catch (error) {
      console.error('Reject error:', error);
      alert('Ошибка отклонения');
    }
  };

  useEffect(() => {
    if (cabinet === 'user') {
      fetchUserRequests();
    } else {
      fetchModeratorTasks();
    }
  }, [cabinet]);

  // ============ RENDER ============

  return (
    <div style={{ minHeight: '100vh', backgroundColor: '#f5f5f5', padding: '20px', fontFamily: 'system-ui, -apple-system, sans-serif' }}>
      <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
        {/* Header */}
        <div style={{ marginBottom: '30px', textAlign: 'center' }}>
          <h1 style={{ fontSize: '32px', fontWeight: 'bold', marginBottom: '20px', color: '#333' }}>
            🏢 B2B Платформа
          </h1>
          
          <div style={{ display: 'flex', gap: '10px', justifyContent: 'center' }}>
            <button
              onClick={() => setCabinet('user')}
              style={{
                padding: '12px 24px',
                fontSize: '16px',
                fontWeight: '600',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                backgroundColor: cabinet === 'user' ? '#2563eb' : '#e0e0e0',
                color: cabinet === 'user' ? 'white' : '#333',
                transition: 'all 0.2s',
              }}
            >
              👤 Личный кабинет
            </button>
            <button
              onClick={() => setCabinet('moderator')}
              style={{
                padding: '12px 24px',
                fontSize: '16px',
                fontWeight: '600',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                backgroundColor: cabinet === 'moderator' ? '#2563eb' : '#e0e0e0',
                color: cabinet === 'moderator' ? 'white' : '#333',
                transition: 'all 0.2s',
              }}
            >
              ⚙️ Модератор
            </button>
          </div>
        </div>

        {/* USER CABINET */}
        {cabinet === 'user' && (
          <div>
            {!selectedRequest ? (
              <div>
                {/* Upload Section */}
                <div style={{
                  backgroundColor: 'white',
                  padding: '30px',
                  borderRadius: '12px',
                  marginBottom: '20px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                }}>
                  <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '15px', color: '#333' }}>
                    📤 Загрузить запрос
                  </h2>
                  <input
                    type="file"
                    accept=".docx,.pdf,.xlsx"
                    onChange={handleFileUpload}
                    disabled={loading}
                    style={{
                      padding: '10px',
                      fontSize: '14px',
                      border: '2px solid #ccc',
                      borderRadius: '8px',
                      cursor: loading ? 'not-allowed' : 'pointer',
                    }}
                  />
                  {loading && <p style={{ marginTop: '10px', color: '#666' }}>⏳ Загрузка...</p>}
                </div>

                {/* Requests List */}
                <div style={{
                  backgroundColor: 'white',
                  padding: '30px',
                  borderRadius: '12px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                }}>
                  <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '20px', color: '#333' }}>
                    📋 Ваши заявки
                  </h2>
                  {requests.length === 0 ? (
                    <p style={{ color: '#999' }}>Нет заявок</p>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                      {requests.map(req => (
                        <div
                          key={req.id}
                          onClick={() => handleRequestClick(req)}
                          style={{
                            padding: '15px',
                            borderLeft: '4px solid #2563eb',
                            backgroundColor: '#f9fafb',
                            borderRadius: '8px',
                            cursor: 'pointer',
                            transition: 'all 0.2s',
                            border: '1px solid #e0e0e0',
                          }}
                          onMouseEnter={(e) => {
                            e.currentTarget.style.backgroundColor = '#f0f4f8';
                          }}
                          onMouseLeave={(e) => {
                            e.currentTarget.style.backgroundColor = '#f9fafb';
                          }}
                        >
                          <div style={{ fontWeight: '600', color: '#333' }}>{req.filename}</div>
                          <div style={{ fontSize: '14px', color: '#666' }}>
                            Статус: <span style={{ fontWeight: '600' }}>{req.status}</span> | Позиций: {req.items?.length || 0}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div>
                {/* Back Button */}
                <button
                  onClick={() => setSelectedRequest(null)}
                  style={{
                    marginBottom: '20px',
                    padding: '10px 20px',
                    fontSize: '14px',
                    fontWeight: '600',
                    border: 'none',
                    borderRadius: '8px',
                    backgroundColor: '#e0e0e0',
                    cursor: 'pointer',
                    color: '#333',
                  }}
                >
                  ← Назад
                </button>

                {/* Request Details */}
                <div style={{
                  backgroundColor: 'white',
                  padding: '30px',
                  borderRadius: '12px',
                  marginBottom: '20px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                }}>
                  <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px', color: '#333' }}>
                    {selectedRequest.filename}
                  </h2>
                  <p style={{ color: '#666', marginBottom: '20px' }}>
                    Статус: <span style={{ fontWeight: '600', color: '#2563eb' }}>{selectedRequest.status}</span>
                  </p>

                  {selectedRequest.status === 'draft' && (
                    <button
                      onClick={() => handleSubmitRequest(selectedRequest.id)}
                      disabled={loading}
                      style={{
                        padding: '12px 24px',
                        fontSize: '16px',
                        fontWeight: '600',
                        border: 'none',
                        borderRadius: '8px',
                        backgroundColor: loading ? '#ccc' : '#2563eb',
                        color: 'white',
                        cursor: loading ? 'not-allowed' : 'pointer',
                      }}
                    >
                      {loading ? '⏳ Обработка...' : '🚀 Отправить на обработку'}
                    </button>
                  )}
                </div>

                {/* Positions Table with Inline Suppliers */}
                {selectedRequest.items && selectedRequest.items.length > 0 && (
                  <div style={{
                    backgroundColor: 'white',
                    padding: '30px',
                    borderRadius: '12px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    overflowX: 'auto',
                  }}>
                    <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '20px', color: '#333' }}>
                      📦 Позиции
                    </h2>

                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#f3f4f6', borderBottom: '2px solid #e5e7eb' }}>
                          <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#333', cursor: 'pointer' }}>№</th>
                          <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#333', cursor: 'pointer' }}>Наименование</th>
                          <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#333' }}>Ед.изм.</th>
                          <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#333' }}>Кол-во</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedRequest.items.map((position, index) => (
                          <React.Fragment key={position.pos}>
                            {/* Position Row */}
                            <tr
                              onClick={() => togglePositionExpand(position.pos, position.name)}
                              style={{
                                backgroundColor: expandedPositions.has(position.pos) ? '#e0e7ff' : '#fff',
                                borderBottom: '1px solid #e5e7eb',
                                cursor: 'pointer',
                                transition: 'all 0.2s',
                              }}
                              onMouseEnter={(e) => {
                                e.currentTarget.style.backgroundColor = '#f0f4f8';
                              }}
                              onMouseLeave={(e) => {
                                e.currentTarget.style.backgroundColor = expandedPositions.has(position.pos) ? '#e0e7ff' : '#fff';
                              }}
                            >
                              <td style={{ padding: '12px', color: '#333', fontWeight: '600' }}>
                                {expandedPositions.has(position.pos) ? '▼' : '▶'} {position.pos}
                              </td>
                              <td style={{ padding: '12px', color: '#333' }}>{position.name}</td>
                              <td style={{ padding: '12px', color: '#666' }}>{position.unit}</td>
                              <td style={{ padding: '12px', color: '#666', fontWeight: '600' }}>{position.qty}</td>
                            </tr>

                            {/* Suppliers Row */}
                            {expandedPositions.has(position.pos) && (
                              <tr style={{ backgroundColor: '#f0f9ff', borderBottom: '1px solid #e5e7eb' }}>
                                <td colSpan={4} style={{ padding: '20px' }}>
                                  <div style={{ marginLeft: '20px' }}>
                                    <h4 style={{ fontSize: '16px', fontWeight: '600', marginBottom: '15px', color: '#333' }}>
                                      🏭 Поставщики
                                    </h4>
                                    {positionSuppliers[position.pos] && positionSuppliers[position.pos].length > 0 ? (
                                      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '15px' }}>
                                        {positionSuppliers[position.pos].map(supplier => (
                                          <div
                                            key={supplier.id}
                                            style={{
                                              padding: '15px',
                                              backgroundColor: 'white',
                                              borderRadius: '8px',
                                              border: '1px solid #ddd',
                                              transition: 'all 0.2s',
                                            }}
                                            onMouseEnter={(e) => {
                                              e.currentTarget.style.boxShadow = '0 4px 12px rgba(0,0,0,0.1)';
                                              e.currentTarget.style.transform = 'translateY(-2px)';
                                            }}
                                            onMouseLeave={(e) => {
                                              e.currentTarget.style.boxShadow = 'none';
                                              e.currentTarget.style.transform = 'translateY(0)';
                                            }}
                                          >
                                            <div style={{ fontWeight: '600', fontSize: '15px', color: '#333', marginBottom: '8px' }}>
                                              {supplier.name}
                                            </div>
                                            <div style={{ fontSize: '13px', color: '#666' }}>
                                              <div>📌 ИНН: {supplier.inn}</div>
                                              <div>🌐 <a href={supplier.url} target="_blank" rel="noopener noreferrer" style={{ color: '#2563eb', textDecoration: 'none' }}>Сайт</a></div>
                                              <div>⭐ Рейтинг: {supplier.rating}/5</div>
                                            </div>
                                          </div>
                                        ))}
                                      </div>
                                    ) : (
                                      <p style={{ color: '#999' }}>Поставщики не найдены</p>
                                    )}
                                  </div>
                                </td>
                              </tr>
                            )}
                          </React.Fragment>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* MODERATOR CABINET */}
        {cabinet === 'moderator' && (
          <div>
            {!selectedTask ? (
              <div style={{
                backgroundColor: 'white',
                padding: '30px',
                borderRadius: '12px',
                boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
              }}>
                <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '20px', color: '#333' }}>
                  ⚙️ Задачи на модерацию
                </h2>
                {tasks.length === 0 ? (
                  <p style={{ color: '#999' }}>Нет задач</p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                    {tasks.map(task => (
                      <div
                        key={task.id}
                        onClick={() => handleTaskClick(task)}
                        style={{
                          padding: '15px',
                          borderLeft: '4px solid #f59e0b',
                          backgroundColor: '#fffbeb',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                          border: '1px solid #fde68a',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.backgroundColor = '#fef3c7';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.backgroundColor = '#fffbeb';
                        }}
                      >
                        <div style={{ fontWeight: '600', color: '#333' }}>{task.filename}</div>
                        <div style={{ fontSize: '14px', color: '#666' }}>
                          Позиций: {task.items_count} | Уверенность: {task.confidence}%
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div>
                <button
                  onClick={() => setSelectedTask(null)}
                  style={{
                    marginBottom: '20px',
                    padding: '10px 20px',
                    fontSize: '14px',
                    fontWeight: '600',
                    border: 'none',
                    borderRadius: '8px',
                    backgroundColor: '#e0e0e0',
                    cursor: 'pointer',
                    color: '#333',
                  }}
                >
                  ← Назад
                </button>

                <div style={{
                  backgroundColor: 'white',
                  padding: '30px',
                  borderRadius: '12px',
                  marginBottom: '20px',
                  boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                }}>
                  <h2 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '10px', color: '#333' }}>
                    {selectedTask.filename}
                  </h2>
                  <p style={{ color: '#666', marginBottom: '20px' }}>
                    Уверенность: {selectedTask.confidence}%
                  </p>

                  <div style={{ display: 'flex', gap: '10px' }}>
                    <button
                      onClick={() => handleApproveTask(selectedTask.id)}
                      style={{
                        padding: '12px 24px',
                        fontSize: '16px',
                        fontWeight: '600',
                        border: 'none',
                        borderRadius: '8px',
                        backgroundColor: '#16a34a',
                        color: 'white',
                        cursor: 'pointer',
                      }}
                    >
                      ✓ Одобрить
                    </button>
                    <button
                      onClick={() => handleRejectTask(selectedTask.id)}
                      style={{
                        padding: '12px 24px',
                        fontSize: '16px',
                        fontWeight: '600',
                        border: 'none',
                        borderRadius: '8px',
                        backgroundColor: '#dc2626',
                        color: 'white',
                        cursor: 'pointer',
                      }}
                    >
                      ✗ Отклонить
                    </button>
                  </div>
                </div>

                {selectedTask.items && selectedTask.items.length > 0 && (
                  <div style={{
                    backgroundColor: 'white',
                    padding: '30px',
                    borderRadius: '12px',
                    boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                    overflowX: 'auto',
                  }}>
                    <h2 style={{ fontSize: '20px', fontWeight: '600', marginBottom: '20px', color: '#333' }}>
                      📦 Распознанные позиции
                    </h2>

                    <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                      <thead>
                        <tr style={{ backgroundColor: '#f3f4f6', borderBottom: '2px solid #e5e7eb' }}>
                          <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#333' }}>№</th>
                          <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#333' }}>Наименование</th>
                          <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#333' }}>Ед.изм.</th>
                          <th style={{ padding: '12px', textAlign: 'left', fontWeight: '600', color: '#333' }}>Кол-во</th>
                        </tr>
                      </thead>
                      <tbody>
                        {selectedTask.items.map((item: Position) => (
                          <tr key={item.pos} style={{ borderBottom: '1px solid #e5e7eb' }}>
                            <td style={{ padding: '12px', color: '#333', fontWeight: '600' }}>{item.pos}</td>
                            <td style={{ padding: '12px', color: '#333' }}>{item.name}</td>
                            <td style={{ padding: '12px', color: '#666' }}>{item.unit}</td>
                            <td style={{ padding: '12px', color: '#666', fontWeight: '600' }}>{item.qty}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
