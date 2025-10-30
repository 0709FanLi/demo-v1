/**
 * 知识库管理主页面
 */
import React, { useState, useEffect } from 'react';
import { getKnowledgeList, getKnowledgeCount, deleteKnowledge, getKnowledgeDetail } from '../services/api';
import { KnowledgeSearchResult } from '../types';
import KnowledgePanel from '../components/KnowledgePanel';
import KnowledgeForm from '../components/knowledge/KnowledgeForm';
import ImportModal from '../components/import_export/ImportModal';
import ConfirmDialog from '../components/common/ConfirmDialog';
import { useMessage } from '../components/common/Message';
import '../styles/App.css';

const KnowledgeManagement: React.FC = () => {
  const [knowledgeList, setKnowledgeList] = useState<KnowledgeSearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [knowledgeCount, setKnowledgeCount] = useState(0);
  const [showAddPanel, setShowAddPanel] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [editingDocId, setEditingDocId] = useState<string | null>(null);
  const [viewingDocId, setViewingDocId] = useState<string | null>(null);
  const [viewingDetail, setViewingDetail] = useState<any>(null);
  const [deleteConfirm, setDeleteConfirm] = useState<{ isOpen: boolean; docId: string | null }>({
    isOpen: false,
    docId: null,
  });
  
  const { showSuccess, showError, MessageContainer } = useMessage();

  useEffect(() => {
    loadKnowledgeList();
    loadKnowledgeCount();
  }, []);

  const loadKnowledgeList = async () => {
    setLoading(true);
    try {
      const data = await getKnowledgeList(100, 0);
      setKnowledgeList(data);
    } catch (error) {
      console.error('加载知识列表失败:', error);
      showError('加载知识列表失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  const loadKnowledgeCount = async () => {
    try {
      const data = await getKnowledgeCount();
      setKnowledgeCount(data.total);
    } catch (error) {
      console.error('加载知识库统计失败:', error);
    }
  };

  const handleViewDetail = async (docId: string) => {
    try {
      const detail = await getKnowledgeDetail(docId);
      setViewingDetail(detail);
      setViewingDocId(docId);
    } catch (error) {
      console.error('加载详情失败:', error);
      showError('加载详情失败，请稍后重试');
    }
  };

  const handleEdit = (docId: string) => {
    setEditingDocId(docId);
  };

  const handleDeleteClick = (docId: string) => {
    setDeleteConfirm({ isOpen: true, docId });
  };

  const handleDeleteConfirm = async () => {
    if (!deleteConfirm.docId) return;

    try {
      await deleteKnowledge(deleteConfirm.docId);
      showSuccess('知识删除成功！');
      loadKnowledgeList();
      loadKnowledgeCount();
      setDeleteConfirm({ isOpen: false, docId: null });
    } catch (error) {
      console.error('删除失败:', error);
      showError('删除失败，请稍后重试');
      setDeleteConfirm({ isOpen: false, docId: null });
    }
  };

  const handleDeleteCancel = () => {
    setDeleteConfirm({ isOpen: false, docId: null });
  };

  const filteredList = knowledgeList.filter((item) => {
    if (!searchQuery.trim()) return true;
    const query = searchQuery.toLowerCase();
    return (
      item.content.toLowerCase().includes(query) ||
      item.category.toLowerCase().includes(query)
    );
  });

  const getDocId = (metadata: any): string => {
    if (metadata?.id) {
      return metadata.id.split('_chunk_')[0];
    }
    return '';
  };

  return (
    <div style={{ minHeight: '100vh', background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <header style={{
        background: 'rgba(255, 255, 255, 0.1)',
        backdropFilter: 'blur(10px)',
        padding: '20px 32px',
        borderBottom: '1px solid rgba(255, 255, 255, 0.2)',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
      }}>
        <h1 style={{ margin: 0, color: 'white', fontSize: '24px', fontWeight: 'bold' }}>
          📚 知识库管理
        </h1>
        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <span style={{ color: 'rgba(255, 255, 255, 0.9)', fontSize: '14px' }}>
            共 {knowledgeCount} 条知识
          </span>
          <button
            onClick={() => setShowImportModal(true)}
            style={{
              padding: '8px 16px',
              background: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
              marginRight: '8px',
            }}
          >
            📤 导入文件
          </button>
          <button
            onClick={() => setShowAddPanel(true)}
            style={{
              padding: '8px 16px',
              background: 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer',
              fontSize: '14px',
              fontWeight: '500',
            }}
          >
            ➕ 添加知识
          </button>
        </div>
      </header>

      <div style={{ padding: '24px 32px' }}>
        <div style={{ marginBottom: '24px' }}>
          <input
            type="text"
            placeholder="搜索知识内容或分类..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              maxWidth: '500px',
              padding: '12px 16px',
              borderRadius: '8px',
              border: '1px solid rgba(255, 255, 255, 0.3)',
              background: 'rgba(255, 255, 255, 0.1)',
              color: 'white',
              fontSize: '14px',
              backdropFilter: 'blur(10px)',
            }}
          />
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', color: 'white', padding: '40px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
            <p>加载中...</p>
          </div>
        ) : filteredList.length === 0 ? (
          <div style={{ textAlign: 'center', color: 'white', padding: '40px' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📭</div>
            <p>{searchQuery ? '没有找到匹配的知识' : '知识库暂无内容'}</p>
            {!searchQuery && (
              <button
                onClick={() => setShowAddPanel(true)}
                style={{
                  marginTop: '16px',
                  padding: '10px 20px',
                  background: 'rgba(255, 255, 255, 0.2)',
                  color: 'white',
                  border: 'none',
                  borderRadius: '8px',
                  cursor: 'pointer',
                }}
              >
                添加第一条知识
              </button>
            )}
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '20px' }}>
            {filteredList.map((item, index) => {
              const docId = getDocId(item.metadata);
              const contentPreview = item.content.length > 150
                ? item.content.substring(0, 150) + '...'
                : item.content;

              return (
                <div
                  key={index}
                  style={{
                    background: 'rgba(255, 255, 255, 0.15)',
                    borderRadius: '12px',
                    padding: '20px',
                    backdropFilter: 'blur(10px)',
                    border: '1px solid rgba(255, 255, 255, 0.2)',
                    transition: 'transform 0.2s',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '12px' }}>
                    <div>
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
                      {item.metadata?.created_at && (
                        <span
                          style={{
                            color: 'rgba(255, 255, 255, 0.7)',
                            fontSize: '12px',
                            marginLeft: '8px',
                          }}
                        >
                          📅 {new Date(item.metadata.created_at).toLocaleDateString('zh-CN')}
                        </span>
                      )}
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => docId && handleViewDetail(docId)}
                        style={{
                          background: 'rgba(59, 130, 246, 0.8)',
                          border: 'none',
                          color: 'white',
                          padding: '6px 12px',
                          borderRadius: '6px',
                          fontSize: '12px',
                          cursor: 'pointer',
                        }}
                      >
                        👁️ 详情
                      </button>
                      <button
                        onClick={() => docId && handleEdit(docId)}
                        style={{
                          background: 'rgba(34, 197, 94, 0.8)',
                          border: 'none',
                          color: 'white',
                          padding: '6px 12px',
                          borderRadius: '6px',
                          fontSize: '12px',
                          cursor: 'pointer',
                        }}
                      >
                        ✏️ 编辑
                      </button>
                      <button
                        onClick={() => docId && handleDeleteClick(docId)}
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
                          e.currentTarget.style.transform = 'scale(1.05)';
                        }}
                        onMouseLeave={(e) => {
                          e.currentTarget.style.background = 'rgba(239, 68, 68, 0.8)';
                          e.currentTarget.style.transform = 'scale(1)';
                        }}
                      >
                        🗑️ 删除
                      </button>
                    </div>
                  </div>

                  <div
                    style={{
                      color: 'white',
                      fontSize: '14px',
                      lineHeight: '1.7',
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word',
                      marginBottom: '12px',
                    }}
                  >
                    {contentPreview}
                  </div>

                  {item.content.length > 150 && (
                    <button
                      onClick={() => docId && handleViewDetail(docId)}
                      style={{
                        background: 'rgba(255, 255, 255, 0.2)',
                        border: 'none',
                        color: 'white',
                        padding: '6px 16px',
                        borderRadius: '6px',
                        fontSize: '12px',
                        cursor: 'pointer',
                      }}
                    >
                      查看完整内容
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      <KnowledgePanel
        isOpen={showAddPanel}
        onClose={() => setShowAddPanel(false)}
        onSuccess={() => {
          loadKnowledgeList();
          loadKnowledgeCount();
          setShowAddPanel(false);
        }}
      />

      {editingDocId && (
        <KnowledgeForm
          docId={editingDocId}
          isOpen={!!editingDocId}
          onClose={() => setEditingDocId(null)}
          onSuccess={() => {
            loadKnowledgeList();
            loadKnowledgeCount();
          }}
        />
      )}

      {viewingDocId && viewingDetail && (
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
            zIndex: 2000,
            backdropFilter: 'blur(8px)',
          }}
          onClick={() => {
            setViewingDocId(null);
            setViewingDetail(null);
          }}
        >
          <div
            style={{
              background: 'white',
              borderRadius: '20px',
              width: '90%',
              maxWidth: '900px',
              maxHeight: '90vh',
              display: 'flex',
              flexDirection: 'column',
              boxShadow: '0 20px 60px rgba(0, 0, 0, 0.4)',
              overflow: 'hidden',
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div style={{ padding: '24px 32px', borderBottom: '1px solid #e5e7eb' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h2 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold', color: '#333' }}>
                  📚 知识详情
                </h2>
                <button
                  onClick={() => {
                    setViewingDocId(null);
                    setViewingDetail(null);
                  }}
                  style={{
                    background: 'rgba(0, 0, 0, 0.05)',
                    border: 'none',
                    fontSize: '24px',
                    width: '32px',
                    height: '32px',
                    borderRadius: '8px',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                  }}
                >
                  ×
                </button>
              </div>
            </div>

            <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
              <div style={{ marginBottom: '20px' }}>
                <div style={{ display: 'flex', gap: '12px', alignItems: 'center', marginBottom: '16px' }}>
                  <span
                    style={{
                      background: '#e0e7ff',
                      color: '#4f46e5',
                      padding: '6px 16px',
                      borderRadius: '20px',
                      fontSize: '14px',
                      fontWeight: 'bold',
                    }}
                  >
                    {viewingDetail.category}
                  </span>
                  {viewingDetail.title && (
                    <h3 style={{ margin: 0, fontSize: '20px', fontWeight: 'bold', color: '#333' }}>
                      {viewingDetail.title}
                    </h3>
                  )}
                </div>
                {viewingDetail.tags && viewingDetail.tags.length > 0 && (
                  <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginBottom: '16px' }}>
                    {viewingDetail.tags.map((tag: string, idx: number) => (
                      <span
                        key={idx}
                        style={{
                          background: '#f3f4f6',
                          color: '#6b7280',
                          padding: '4px 12px',
                          borderRadius: '20px',
                          fontSize: '12px',
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
                <div style={{ color: '#6b7280', fontSize: '14px', marginBottom: '20px' }}>
                  <span>创建时间: {new Date(viewingDetail.created_at).toLocaleString('zh-CN')}</span>
                  {viewingDetail.updated_at && (
                    <span style={{ marginLeft: '16px' }}>
                      更新时间: {new Date(viewingDetail.updated_at).toLocaleString('zh-CN')}
                    </span>
                  )}
                </div>
              </div>

              <div
                style={{
                  background: '#f9fafb',
                  borderRadius: '12px',
                  padding: '20px',
                  lineHeight: '1.8',
                  color: '#333',
                  whiteSpace: 'pre-wrap',
                  wordBreak: 'break-word',
                }}
              >
                {viewingDetail.content}
              </div>

              {viewingDetail.chunks && viewingDetail.chunks.length > 1 && (
                <div style={{ marginTop: '24px' }}>
                  <h4 style={{ marginBottom: '12px', color: '#333', fontSize: '16px' }}>
                    分块信息 ({viewingDetail.chunks.length} 个分块)
                  </h4>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                    {viewingDetail.chunks.map((chunk: any, idx: number) => (
                      <div
                        key={idx}
                        style={{
                          background: '#f3f4f6',
                          padding: '12px',
                          borderRadius: '8px',
                          fontSize: '13px',
                          color: '#6b7280',
                        }}
                      >
                        <strong>分块 {chunk.chunk_index + 1}:</strong> {chunk.content.substring(0, 100)}...
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div style={{ padding: '20px 32px', borderTop: '1px solid #e5e7eb', display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
              <button
                onClick={() => {
                  setViewingDocId(null);
                  setViewingDetail(null);
                }}
                style={{
                  padding: '10px 20px',
                  borderRadius: '8px',
                  border: '1px solid #d1d5db',
                  background: 'white',
                  color: '#333',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                }}
              >
                关闭
              </button>
              <button
                onClick={() => {
                  setViewingDocId(null);
                  setViewingDetail(null);
                  handleEdit(viewingDocId);
                }}
                style={{
                  padding: '10px 20px',
                  borderRadius: '8px',
                  border: 'none',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  color: 'white',
                  cursor: 'pointer',
                  fontSize: '14px',
                  fontWeight: '500',
                }}
              >
                ✏️ 编辑
              </button>
            </div>
          </div>
        </div>
      )}

      <ImportModal
        isOpen={showImportModal}
        onClose={() => setShowImportModal(false)}
        onSuccess={() => {
          loadKnowledgeList();
          loadKnowledgeCount();
        }}
      />

      <ConfirmDialog
        isOpen={deleteConfirm.isOpen}
        title="确认删除"
        message="确定要删除这条知识吗？删除后无法恢复。"
        confirmText="删除"
        cancelText="取消"
        onConfirm={handleDeleteConfirm}
        onCancel={handleDeleteCancel}
        type="danger"
      />

      <MessageContainer />
    </div>
  );
};

export default KnowledgeManagement;

