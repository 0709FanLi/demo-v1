/**
 * RAG智能对话应用主组件
 */

import React, { useState, useEffect, useRef } from 'react';
import { chatWithRAG, chatWithImage, getKnowledgeCount } from './services/api';
import { Message, ChatRequest } from './types';
import KnowledgePanel from './components/KnowledgePanel';
import KnowledgeListModal from './components/KnowledgeListModal';
import './styles/App.css';

const App: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [knowledgeCount, setKnowledgeCount] = useState(0);
  const [showKnowledgePanel, setShowKnowledgePanel] = useState(false);
  const [showKnowledgeListModal, setShowKnowledgeListModal] = useState(false);

  const chatContainerRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // 加载知识库统计
  useEffect(() => {
    loadKnowledgeCount();
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const loadKnowledgeCount = async () => {
    try {
      const data = await getKnowledgeCount();
      setKnowledgeCount(data.total);
    } catch (error) {
      console.error('加载知识库统计失败:', error);
    }
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);

      // 生成预览
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleRemoveImage = () => {
    setSelectedImage(null);
    setImagePreview(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSend = async () => {
    if (!inputText.trim() && !selectedImage) {
      return;
    }

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputText.trim(),
      imageUrl: imagePreview || undefined,
      timestamp: Date.now(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputText('');
    setLoading(true);

    try {
      let response;

      // 如果有图片，使用图文对话接口
      if (selectedImage) {
        response = await chatWithImage(userMessage.content || '描述这张图片', selectedImage);
        handleRemoveImage();
      } else {
        // 纯文本对话
        const request: ChatRequest = {
          question: userMessage.content,
          use_knowledge_base: true,
          history: messages.slice(-10).map((msg) => ({
            role: msg.role,
            content: msg.content,
          })),
        };
        response = await chatWithRAG(request);
      }

      // 添加助手回复
      const assistantMessage: Message = {
        id: `assistant-${Date.now()}`,
        role: 'assistant',
        content: response.answer,
        timestamp: Date.now(),
        confidence: response.confidence,
        sources: response.knowledge_sources,
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error: any) {
      console.error('对话失败:', error);

      const errorMessage: Message = {
        id: `error-${Date.now()}`,
        role: 'assistant',
        content: `抱歉，处理您的消息时出错了：${error.response?.data?.detail || error.message}`,
        timestamp: Date.now(),
        confidence: '低',
      };

      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="app">
      {/* 头部 */}
      <header className="app-header">
        <h1 className="app-title">🧬 抗衰老专家咨询</h1>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <span
            className="knowledge-status"
            onClick={() => setShowKnowledgeListModal(true)}
            style={{ cursor: 'pointer' }}
            title="点击查看知识库内容"
          >
            📚 知识库: {knowledgeCount} 条
          </span>
          <button
            onClick={() => setShowKnowledgePanel(true)}
            style={{
              padding: '6px 12px',
              background: 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              boxShadow: '0 2px 4px rgba(34, 197, 94, 0.2)',
            }}
          >
            ➕ 添加知识
          </button>
        </div>
      </header>

      {/* 聊天区域 */}
      <div className="chat-container" ref={chatContainerRef}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', color: 'white', marginTop: '50px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🧬</div>
            <h2 style={{ fontSize: '28px', fontWeight: 'bold', marginBottom: '12px' }}>
              您好！我是抗衰老领域专家
            </h2>
            <p style={{ marginTop: '16px', opacity: 0.95, fontSize: '16px', lineHeight: '1.6' }}>
              我精通细胞生物学、营养学、运动科学和再生医学<br />
              可以为您提供基于科学证据的抗衰老建议和健康管理方案
            </p>
            <div style={{ 
              marginTop: '24px', 
              display: 'flex', 
              justifyContent: 'center', 
              gap: '16px',
              flexWrap: 'wrap',
              padding: '0 20px'
            }}>
              <div style={{ 
                background: 'rgba(255, 255, 255, 0.15)', 
                padding: '12px 20px', 
                borderRadius: '12px',
                backdropFilter: 'blur(10px)'
              }}>
                💊 营养补充剂指导
              </div>
              <div style={{ 
                background: 'rgba(255, 255, 255, 0.15)', 
                padding: '12px 20px', 
                borderRadius: '12px',
                backdropFilter: 'blur(10px)'
              }}>
                🏃 运动与健康管理
              </div>
              <div style={{ 
                background: 'rgba(255, 255, 255, 0.15)', 
                padding: '12px 20px', 
                borderRadius: '12px',
                backdropFilter: 'blur(10px)'
              }}>
                🔬 最新研究解读
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message-wrapper ${message.role}`}>
            <div className={`message-bubble ${message.role}`}>
              {message.imageUrl && (
                <img
                  src={message.imageUrl}
                  alt="用户上传"
                  className="message-image"
                />
              )}
              <div>{message.content}</div>

              {message.role === 'assistant' && (
                <div className="message-meta">
                  {message.confidence && (
                    <span className={`confidence-badge confidence-${message.confidence}`}>
                      {message.confidence}
                    </span>
                  )}
                  <span>{new Date(message.timestamp).toLocaleTimeString()}</span>
                </div>
              )}

              {/* 暂时隐藏科学依据显示 */}
              {/* {message.sources && message.sources.length > 0 && (
                <div className="knowledge-sources">
                  <div className="knowledge-sources-title">🔬 科学依据：</div>
                  <ul>
                    {message.sources.map((source, idx) => (
                      <li key={idx}>{source}</li>
                    ))}
                  </ul>
                </div>
              )} */}
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-wrapper assistant">
            <div className="message-bubble assistant">
              <div className="loading-message">
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
                <div className="loading-dot"></div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 输入区域 */}
      <div className="input-container">
        {imagePreview && (
          <div className="image-preview-container">
            <img src={imagePreview} alt="预览" className="image-preview" />
            <button className="remove-image-btn" onClick={handleRemoveImage}>
              ×
            </button>
          </div>
        )}

        <div className="input-wrapper">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            style={{ display: 'none' }}
            onChange={handleImageSelect}
          />

          <button
            className="image-upload-btn"
            onClick={() => fileInputRef.current?.click()}
            title="上传检查报告或身体指标图片"
          >
            📊
          </button>

          <div className="textarea-wrapper">
            <textarea
              className="message-input"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="请输入您的健康问题... 例如：NMN 如何补充？(Shift+Enter 换行)"
              disabled={loading}
            />
          </div>

          <button
            className="send-btn"
            onClick={handleSend}
            disabled={loading || (!inputText.trim() && !selectedImage)}
            title="发送"
          >
            ➤
          </button>
        </div>
      </div>

      {/* 知识库管理面板 */}
      <KnowledgePanel
        isOpen={showKnowledgePanel}
        onClose={() => setShowKnowledgePanel(false)}
        onSuccess={() => {
          loadKnowledgeCount();
          setShowKnowledgePanel(false);
        }}
      />

      {/* 知识库列表查看模态框 */}
      <KnowledgeListModal
        isOpen={showKnowledgeListModal}
        onClose={() => setShowKnowledgeListModal(false)}
        onRefresh={loadKnowledgeCount}
      />
    </div>
  );
};

export default App;

