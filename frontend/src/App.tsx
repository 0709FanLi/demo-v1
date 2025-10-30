/**
 * 应用主入口
 * 支持知识库管理和对话两个页面切换
 */
import React, { useState } from 'react';
import Chat from './pages/Chat';
import KnowledgeManagement from './pages/KnowledgeManagement';
import './styles/App.css';

type Page = 'knowledge' | 'chat';

const App: React.FC = () => {
  const [currentPage, setCurrentPage] = useState<Page>('knowledge');
  const [knowledgeCount, setKnowledgeCount] = useState(0);

  return (
    <div>
      {/* 导航栏 */}
      <nav style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 1000,
        background: 'rgba(255, 255, 255, 0.95)',
        backdropFilter: 'blur(10px)',
        borderBottom: '1px solid rgba(0, 0, 0, 0.1)',
        padding: '12px 32px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
      }}>
        <div style={{ display: 'flex', gap: '24px', alignItems: 'center' }}>
          <h2 style={{ margin: 0, fontSize: '20px', fontWeight: 'bold', color: '#333' }}>
            🧬 AI-RAG 知识库系统
          </h2>
          <div style={{ display: 'flex', gap: '8px' }}>
            <button
              onClick={() => setCurrentPage('knowledge')}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: 'none',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                background: currentPage === 'knowledge'
                  ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  : 'rgba(0, 0, 0, 0.05)',
                color: currentPage === 'knowledge' ? 'white' : '#333',
                transition: 'all 0.2s',
              }}
            >
              📚 知识库管理
            </button>
            <button
              onClick={() => setCurrentPage('chat')}
              style={{
                padding: '8px 16px',
                borderRadius: '8px',
                border: 'none',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '500',
                background: currentPage === 'chat'
                  ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
                  : 'rgba(0, 0, 0, 0.05)',
                color: currentPage === 'chat' ? 'white' : '#333',
                transition: 'all 0.2s',
              }}
            >
              💬 智能对话
            </button>
          </div>
        </div>
        {knowledgeCount > 0 && (
          <div style={{ color: '#666', fontSize: '14px' }}>
            📚 知识库: {knowledgeCount} 条
          </div>
        )}
      </nav>

      {/* 页面内容 */}
      <div style={{ marginTop: '60px' }}>
        {currentPage === 'knowledge' && (
          <KnowledgeManagement />
        )}
        {currentPage === 'chat' && (
          <Chat onKnowledgeCountChange={setKnowledgeCount} />
        )}
      </div>
    </div>
  );
};

export default App;
