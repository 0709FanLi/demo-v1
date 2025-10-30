/**
 * 消息提示组件（Toast）
 */
import React, { useEffect } from 'react';

export type MessageType = 'success' | 'error' | 'warning' | 'info';

interface MessageProps {
  type: MessageType;
  message: string;
  duration?: number;
  onClose: () => void;
}

const Message: React.FC<MessageProps> = ({
  type,
  message,
  duration = 3000,
  onClose,
}) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const getTypeConfig = () => {
    switch (type) {
      case 'success':
        return {
          icon: '✅',
          bg: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
          iconBg: 'rgba(16, 185, 129, 0.15)',
        };
      case 'error':
        return {
          icon: '❌',
          bg: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
          iconBg: 'rgba(239, 68, 68, 0.15)',
        };
      case 'warning':
        return {
          icon: '⚠️',
          bg: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
          iconBg: 'rgba(245, 158, 11, 0.15)',
        };
      default:
        return {
          icon: 'ℹ️',
          bg: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
          iconBg: 'rgba(59, 130, 246, 0.15)',
        };
    }
  };

  const config = getTypeConfig();

  return (
    <div
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        zIndex: 4000,
        animation: 'slideInRight 0.3s ease-out',
      }}
    >
      <div
        style={{
          background: config.bg,
          borderRadius: '12px',
          padding: '16px 20px',
          boxShadow: '0 10px 30px rgba(0, 0, 0, 0.2)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
          minWidth: '300px',
          maxWidth: '500px',
          color: 'white',
          backdropFilter: 'blur(10px)',
        }}
      >
        <div
          style={{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            background: config.iconBg,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '18px',
            flexShrink: 0,
          }}
        >
          {config.icon}
        </div>
        <div style={{ flex: 1, fontSize: '14px', fontWeight: '500', lineHeight: '1.5' }}>
          {message}
        </div>
        <button
          onClick={onClose}
          style={{
            background: 'rgba(255, 255, 255, 0.2)',
            border: 'none',
            color: 'white',
            fontSize: '20px',
            width: '24px',
            height: '24px',
            borderRadius: '4px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            transition: 'all 0.2s',
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
          }}
        >
          ×
        </button>
      </div>
      <style>{`
        @keyframes slideInRight {
          from {
            opacity: 0;
            transform: translateX(100%);
          }
          to {
            opacity: 1;
            transform: translateX(0);
          }
        }
      `}</style>
    </div>
  );
};

// 消息管理器 Hook
export const useMessage = () => {
  const [messages, setMessages] = React.useState<Array<{ id: number; type: MessageType; message: string }>>([]);

  const showMessage = (type: MessageType, message: string, duration?: number) => {
    const id = Date.now();
    setMessages((prev) => [...prev, { id, type, message }]);
    
    setTimeout(() => {
      setMessages((prev) => prev.filter((msg) => msg.id !== id));
    }, duration || 3000);
  };

  const MessageContainer = () => (
    <>
      {messages.map((msg) => (
        <Message
          key={msg.id}
          type={msg.type}
          message={msg.message}
          onClose={() => {
            setMessages((prev) => prev.filter((m) => m.id !== msg.id));
          }}
        />
      ))}
    </>
  );

  return {
    showSuccess: (message: string, duration?: number) => showMessage('success', message, duration),
    showError: (message: string, duration?: number) => showMessage('error', message, duration),
    showWarning: (message: string, duration?: number) => showMessage('warning', message, duration),
    showInfo: (message: string, duration?: number) => showMessage('info', message, duration),
    MessageContainer,
  };
};

export default Message;

