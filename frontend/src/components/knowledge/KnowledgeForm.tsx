/**
 * 知识编辑表单组件
 */
import React, { useState, useEffect } from 'react';
import { updateKnowledge, getKnowledgeDetail } from '../../services/api';
import { KnowledgeUpdate, KnowledgeDetail } from '../../types';
import { useMessage } from '../common/Message';

interface KnowledgeFormProps {
  docId: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const KnowledgeForm: React.FC<KnowledgeFormProps> = ({
  docId,
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [loading, setLoading] = useState(false);
  const [fetching, setFetching] = useState(false);
  const [formData, setFormData] = useState<KnowledgeUpdate>({
    content: '',
    category: '',
    title: '',
    tags: [],
  });
  
  const { showSuccess, showError, MessageContainer } = useMessage();

  useEffect(() => {
    if (isOpen && docId) {
      loadKnowledgeDetail();
    }
  }, [isOpen, docId]);

  const loadKnowledgeDetail = async () => {
    setFetching(true);
    try {
      const detail = await getKnowledgeDetail(docId);
      setFormData({
        content: detail.content,
        category: detail.category,
        title: detail.title || '',
        tags: detail.tags || [],
      });
    } catch (error) {
      console.error('加载知识详情失败:', error);
      showError('加载知识详情失败，请稍后重试');
    } finally {
      setFetching(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.content?.trim()) {
      showError('请输入知识内容');
      return;
    }

    if (!formData.category?.trim()) {
      showError('请输入知识分类');
      return;
    }

    setLoading(true);

    try {
      await updateKnowledge(docId, formData);
      showSuccess('知识更新成功！');
      onSuccess();
      onClose();
    } catch (error: any) {
      console.error('更新失败:', error);
      showError(`更新失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleTagsChange = (value: string) => {
    const tags = value.split(',').map((tag) => tag.trim()).filter((tag) => tag.length > 0);
    setFormData({ ...formData, tags });
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
        zIndex: 2000,
        backdropFilter: 'blur(8px)',
      }}
      onClick={onClose}
    >
      <div
        style={{
          background: 'white',
          borderRadius: '20px',
          width: '90%',
          maxWidth: '800px',
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
              ✏️ 编辑知识
            </h2>
            <button
              onClick={onClose}
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
          {fetching ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>⏳</div>
              <p>加载中...</p>
            </div>
          ) : (
            <form onSubmit={handleSubmit}>
              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#333' }}>
                  🏷️ 知识分类 *
                </label>
                <input
                  type="text"
                  value={formData.category || ''}
                  onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                  placeholder="例如：NAD+与抗衰老、NMN补充指南"
                  required
                  style={{
                    width: '100%',
                    padding: '12px',
                    borderRadius: '8px',
                    border: '1px solid #d1d5db',
                    fontSize: '14px',
                  }}
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#333' }}>
                  📝 知识标题（可选）
                </label>
                <input
                  type="text"
                  value={formData.title || ''}
                  onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                  placeholder="知识标题"
                  style={{
                    width: '100%',
                    padding: '12px',
                    borderRadius: '8px',
                    border: '1px solid #d1d5db',
                    fontSize: '14px',
                  }}
                />
              </div>

              <div style={{ marginBottom: '20px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#333' }}>
                  📝 知识内容 *
                </label>
                <textarea
                  value={formData.content || ''}
                  onChange={(e) => setFormData({ ...formData, content: e.target.value })}
                  placeholder="请输入知识内容..."
                  required
                  rows={10}
                  style={{
                    width: '100%',
                    padding: '12px',
                    borderRadius: '8px',
                    border: '1px solid #d1d5db',
                    fontSize: '14px',
                    fontFamily: 'inherit',
                    resize: 'vertical',
                  }}
                />
              </div>

              <div style={{ marginBottom: '24px' }}>
                <label style={{ display: 'block', marginBottom: '8px', fontWeight: '500', color: '#333' }}>
                  🔖 标签（用逗号分隔）
                </label>
                <input
                  type="text"
                  value={(formData.tags || []).join(', ')}
                  onChange={(e) => handleTagsChange(e.target.value)}
                  placeholder="例如：NMN, 抗衰老, 营养补充"
                  style={{
                    width: '100%',
                    padding: '12px',
                    borderRadius: '8px',
                    border: '1px solid #d1d5db',
                    fontSize: '14px',
                  }}
                />
                    {(formData.tags || []).length > 0 && (
                      <div style={{ marginTop: '8px', display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
                        {formData.tags!.map((tag: string, idx: number) => (
                      <span
                        key={idx}
                        style={{
                          background: '#e0e7ff',
                          color: '#4f46e5',
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
              </div>

              <div style={{ display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
                <button
                  type="button"
                  onClick={onClose}
                  disabled={loading}
                  style={{
                    padding: '10px 20px',
                    borderRadius: '8px',
                    border: '1px solid #d1d5db',
                    background: 'white',
                    color: '#333',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    fontWeight: '500',
                  }}
                >
                  取消
                </button>
                <button
                  type="submit"
                  disabled={loading || !formData.content?.trim() || !formData.category?.trim()}
                  style={{
                    padding: '10px 20px',
                    borderRadius: '8px',
                    border: 'none',
                    background: loading
                      ? '#9ca3af'
                      : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                    color: 'white',
                    cursor: loading ? 'not-allowed' : 'pointer',
                    fontSize: '14px',
                    fontWeight: '500',
                  }}
                >
                  {loading ? '更新中...' : '更新知识'}
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
      <MessageContainer />
    </div>
  );
};

export default KnowledgeForm;

