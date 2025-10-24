/**
 * 知识库列表查看模态框组件
 */

import React, { useState, useEffect } from 'react';
import { getKnowledgeList, deleteKnowledge } from '../services/api';

interface KnowledgeListModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRefresh?: () => void;
}

interface KnowledgeItem {
  content: string;
  category: string;
  score: number;
  metadata: {
    created_at: string;
    id: string;
  };
}

const KnowledgeListModal: React.FC<KnowledgeListModalProps> = ({
  isOpen,
  onClose,
  onRefresh,
}) => {
  const [knowledgeList, setKnowledgeList] = useState<KnowledgeItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [expandedId, setExpandedId] = useState<string | null>(null);

  useEffect(() => {
    if (isOpen) {
      loadKnowledgeList();
    }
  }, [isOpen]);

  const loadKnowledgeList = async () => {
    setLoading(true);
    try {
      const data = await getKnowledgeList(100, 0);
      setKnowledgeList(data);
    } catch (error) {
      console.error('加载知识列表失败:', error);
      alert('加载知识列表失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    if (!window.confirm('确定要删除这条知识吗？')) {
      return;
    }

    try {
      await deleteKnowledge(docId);
      alert('删除成功！');
      loadKnowledgeList();
      if (onRefresh) onRefresh();
    } catch (error) {
      console.error('删除失败:', error);
      alert('删除失败，请稍后重试');
    }
  };

  const toggleExpand = (id: string) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (!isOpen) return null;

  return (
    <div
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: 'rgba(0, 0, 0, 0.7)',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        zIndex: 1000,
        backdropFilter: 'blur(8px)',
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          borderRadius: '20px',
          width: '90%',
          maxWidth: '900px',
          maxHeight: '85vh',
          display: 'flex',
          flexDirection: 'column',
          boxShadow: '0 20px 60px rgba(0, 0, 0, 0.4)',
          border: '1px solid rgba(255, 255, 255, 0.2)',
        }}
        onClick={(e) => e.stopPropagation()}
      >
        {/* 头部 */}
        <div
          style={{
            padding: '24px 32px',
            borderBottom: '1px solid rgba(255, 255, 255, 0.15)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div>
            <h2
              style={{
                fontSize: '26px',
                fontWeight: 'bold',
                color: 'white',
                margin: 0,
                marginBottom: '6px',
              }}
            >
              📚 知识库内容
            </h2>
            <p style={{ margin: 0, color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px' }}>
              共 {knowledgeList.length} 条知识条目
            </p>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              border: 'none',
              color: 'white',
              fontSize: '28px',
              width: '40px',
              height: '40px',
              borderRadius: '10px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
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

        {/* 内容区域 */}
        <div
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '24px 32px',
          }}
        >
          {loading ? (
            <div style={{ textAlign: 'center', color: 'white', padding: '40px' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
              <p>加载中...</p>
            </div>
          ) : knowledgeList.length === 0 ? (
            <div style={{ textAlign: 'center', color: 'white', padding: '40px' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
              <p style={{ fontSize: '16px', opacity: 0.8 }}>知识库暂无内容</p>
              <p style={{ fontSize: '14px', opacity: 0.6, marginTop: '8px' }}>
                点击右上角"添加知识"按钮添加内容
              </p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              {knowledgeList.map((item, index) => {
                const isExpanded = expandedId === item.metadata.id;
                const contentPreview =
                  item.content.length > 150
                    ? item.content.substring(0, 150) + '...'
                    : item.content;

                return (
                  <div
                    key={item.metadata.id}
                    style={{
                      background: 'rgba(255, 255, 255, 0.15)',
                      borderRadius: '12px',
                      padding: '20px',
                      backdropFilter: 'blur(10px)',
                      border: '1px solid rgba(255, 255, 255, 0.2)',
                      transition: 'all 0.3s',
                    }}
                  >
                    {/* 头部信息 */}
                    <div
                      style={{
                        display: 'flex',
                        justifyContent: 'space-between',
                        alignItems: 'flex-start',
                        marginBottom: '12px',
                      }}
                    >
                      <div style={{ flex: 1 }}>
                        <div
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                            marginBottom: '8px',
                          }}
                        >
                          <span
                            style={{
                              background: 'rgba(255, 255, 255, 0.25)',
                              color: 'white',
                              padding: '4px 12px',
                              borderRadius: '20px',
                              fontSize: '12px',
                              fontWeight: 'bold',
                            }}
                          >
                            {item.category}
                          </span>
                          <span
                            style={{
                              color: 'rgba(255, 255, 255, 0.7)',
                              fontSize: '12px',
                            }}
                          >
                            📅 {new Date(item.metadata.created_at).toLocaleDateString('zh-CN')}
                          </span>
                        </div>
                      </div>
                      <button
                        onClick={() => handleDelete(item.metadata.id.split('_chunk_')[0])}
                        style={{
                          background: 'rgba(239, 68, 68, 0.8)',
                          border: 'none',
                          color: 'white',
                          padding: '6px 12px',
                          borderRadius: '6px',
                          fontSize: '12px',
                          cursor: 'pointer',
                          transition: 'all 0.2s',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = 'rgba(239, 68, 68, 1)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = 'rgba(239, 68, 68, 0.8)';
                        }}
                      >
                        🗑️ 删除
                      </button>
                    </div>

                    {/* 内容 */}
                    <div
                      style={{
                        color: 'white',
                        fontSize: '14px',
                        lineHeight: '1.7',
                        whiteSpace: 'pre-wrap',
                        wordBreak: 'break-word',
                      }}
                    >
                      {isExpanded ? item.content : contentPreview}
                    </div>

                    {/* 展开/收起按钮 */}
                    {item.content.length > 150 && (
                      <button
                        onClick={() => toggleExpand(item.metadata.id)}
                        style={{
                          background: 'rgba(255, 255, 255, 0.2)',
                          border: 'none',
                          color: 'white',
                          padding: '6px 16px',
                          borderRadius: '6px',
                          fontSize: '12px',
                          cursor: 'pointer',
                          marginTop: '12px',
                          transition: 'all 0.2s',
                        }}
                        onMouseEnter={(e) => {
                          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                        }}
                      >
                        {isExpanded ? '收起 ▲' : '查看完整内容 ▼'}
                      </button>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* 底部操作栏 */}
        <div
          style={{
            padding: '20px 32px',
            borderTop: '1px solid rgba(255, 255, 255, 0.15)',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
          }}
        >
          <div style={{ color: 'rgba(255, 255, 255, 0.8)', fontSize: '14px' }}>
            💡 提示：点击删除按钮可以移除知识条目
          </div>
          <button
            onClick={loadKnowledgeList}
            disabled={loading}
            style={{
              background: 'rgba(255, 255, 255, 0.2)',
              border: 'none',
              color: 'white',
              padding: '10px 20px',
              borderRadius: '8px',
              fontSize: '14px',
              cursor: loading ? 'not-allowed' : 'pointer',
              fontWeight: '500',
              transition: 'all 0.2s',
            }}
            onMouseEnter={(e) => {
              if (!loading) {
                e.currentTarget.style.background = 'rgba(255, 255, 255, 0.3)';
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
            }}
          >
            {loading ? '刷新中...' : '🔄 刷新'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default KnowledgeListModal;

