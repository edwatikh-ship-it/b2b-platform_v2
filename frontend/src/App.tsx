import React from 'react'

function App() {
  return (
    <div style={{ padding: '20px', fontFamily: 'Arial' }}>
      <h1>✅ B2B Platform работает!</h1>
      <p>Фронтенд успешно загрузился на React</p>
      
      <div style={{ 
        backgroundColor: '#f0f0f0', 
        padding: '20px', 
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        <h2>📊 Два кабинета:</h2>
        <button style={{
          padding: '10px 20px',
          margin: '10px',
          backgroundColor: '#2563eb',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer'
        }}>
          👤 User Cabinet
        </button>
        <button style={{
          padding: '10px 20px',
          margin: '10px',
          backgroundColor: '#10b981',
          color: 'white',
          border: 'none',
          borderRadius: '6px',
          cursor: 'pointer'
        }}>
          🛡️ Moderator Cabinet
        </button>
      </div>

      <p style={{ color: '#666', marginTop: '20px' }}>
        Backend API: <code>http://127.0.0.1:8000/api/v1</code>
      </p>
    </div>
  )
}

export default App
