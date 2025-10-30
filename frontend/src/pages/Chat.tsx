/**
 * RAG 对话页面组件 - 重构版
 * 现代化的对话界面设计
 */
import React, { useState, useEffect, useRef } from 'react';
import { chatWithRAG, chatWithImage, getKnowledgeCount } from '../services/api';
import { Message, ChatRequest } from '../types';
import KnowledgePanel from '../components/KnowledgePanel';
import KnowledgeListModal from '../components/KnowledgeListModal';
import { useMessage } from '../components/common/Message';
import '../styles/Chat.css';

interface ChatProps {
  onKnowledgeCountChange?: (count: number) => void;
}

const Chat: React.FC<ChatProps> = ({ onKnowledgeCountChange }) => {
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
  const { showError, MessageContainer } = useMessage();

  // 加载知识库统计
  useEffect(() => {
    loadKnowledgeCount();
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, loading]);

  const loadKnowledgeCount = async () => {
    try {
      const data = await getKnowledgeCount();
      setKnowledgeCount(data.total);
      if (onKnowledgeCountChange) {
        onKnowledgeCountChange(data.total);
      }
    } catch (error) {
      console.error('加载知识库统计失败:', error);
    }
  };

  const handleImageSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedImage(file);
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

      if (selectedImage) {
        response = await chatWithImage(userMessage.content || '描述这张图片', selectedImage);
        handleRemoveImage();
      } else {
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
      showError(`对话失败: ${error.response?.data?.detail || error.message}`);
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
    <div className="chat-page">
      {/* 顶部工具栏 */}
      <div className="chat-toolbar">
        <div className="toolbar-left">
          <div className="toolbar-title">
            <span className="toolbar-icon">🧬</span>
            <span>抗衰老专家咨询</span>
          </div>
        </div>
        <div className="toolbar-right">
          <button
            className="toolbar-btn knowledge-btn"
            onClick={() => setShowKnowledgeListModal(true)}
            title="查看知识库"
          >
            <span>📚</span>
            <span>知识库: {knowledgeCount} 条</span>
          </button>
          <button
            className="toolbar-btn add-btn"
            onClick={() => setShowKnowledgePanel(true)}
            title="添加知识"
          >
            <span>➕</span>
            <span>添加知识</span>
          </button>
        </div>
      </div>

      {/* 聊天消息区域 */}
      <div className="chat-messages" ref={chatContainerRef}>
        {messages.length === 0 && (
          <div className="welcome-screen">
            <div className="welcome-icon">🧬</div>
            <h2 className="welcome-title">您好！我是抗衰老领域专家</h2>
            <p className="welcome-subtitle">
              我精通细胞生物学、营养学、运动科学和再生医学
              <br />
              可以为您提供基于科学证据的抗衰老建议和健康管理方案
            </p>
            <div className="welcome-features">
              <div className="feature-item">
                <span className="feature-icon">🔬</span>
                <span>科学严谨</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">💊</span>
                <span>个性化建议</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📊</span>
                <span>数据分析</span>
              </div>
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div key={message.id} className={`message-item ${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? '👤' : '🧬'}
            </div>
            <div className="message-content-wrapper">
              <div className={`message-bubble ${message.role}`}>
                {message.imageUrl && (
                  <div className="message-image-container">
                    <img src={message.imageUrl} alt="用户上传" className="message-image" />
                  </div>
                )}
                <div className="message-text">{message.content}</div>
                {message.role === 'assistant' && (
                  <div className="message-footer">
                    {message.confidence && (
                      <span className={`confidence-badge confidence-${message.confidence}`}>
                        {message.confidence}置信度
                      </span>
                    )}
                    <span className="message-time">
                      {new Date(message.timestamp).toLocaleTimeString('zh-CN', {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </div>
                )}
              </div>
            </div>
          </div>
        ))}

        {loading && (
          <div className="message-item assistant">
            <div className="message-avatar">🧬</div>
            <div className="message-content-wrapper">
              <div className="message-bubble assistant loading-bubble">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* 输入区域 */}
      <div className="chat-input-area">
        {imagePreview && (
          <div className="image-preview-wrapper">
            <img src={imagePreview} alt="预览" className="preview-image" />
            <button className="preview-remove-btn" onClick={handleRemoveImage}>
              ×
            </button>
          </div>
        )}

        <div className="input-area">
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            style={{ display: 'none' }}
            onChange={handleImageSelect}
          />
          <button
            className="icon-btn image-btn"
            onClick={() => fileInputRef.current?.click()}
            title="上传图片"
          >
            📷
          </button>

          <div className="input-box">
            <textarea
              className="message-textarea"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="请输入您的健康问题... (Shift+Enter 换行)"
              disabled={loading}
              rows={1}
            />
          </div>

          <button
            className={`icon-btn send-btn ${loading || (!inputText.trim() && !selectedImage) ? 'disabled' : ''}`}
            onClick={handleSend}
            disabled={loading || (!inputText.trim() && !selectedImage)}
            title="发送"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>

      <KnowledgePanel
        isOpen={showKnowledgePanel}
        onClose={() => setShowKnowledgePanel(false)}
        onSuccess={() => {
          loadKnowledgeCount();
          setShowKnowledgePanel(false);
        }}
      />

      <KnowledgeListModal
        isOpen={showKnowledgeListModal}
        onClose={() => setShowKnowledgeListModal(false)}
        onRefresh={loadKnowledgeCount}
      />

      <MessageContainer />
    </div>
  );
};

export default Chat;
