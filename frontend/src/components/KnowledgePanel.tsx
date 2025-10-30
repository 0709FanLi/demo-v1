/**
 * 知识库管理面板组件
 */

import React, { useState } from 'react';
import { addKnowledge } from '../services/api';
import { KnowledgeItem } from '../types';
import { useMessage } from './common/Message';

interface KnowledgePanelProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const KnowledgePanel: React.FC<KnowledgePanelProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [content, setContent] = useState('');
  const [category, setCategory] = useState('NAD+与抗衰老');
  const [loading, setLoading] = useState(false);
  
  const { showSuccess, showError, MessageContainer } = useMessage();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!content.trim()) {
      showError('请输入知识内容');
      return;
    }

    setLoading(true);

    try {
      const knowledge: KnowledgeItem = {
        content: content.trim(),
        category: category.trim(),
      };

      await addKnowledge(knowledge);
      showSuccess('知识添加成功！');

      // 重置表单
      setContent('');
      setCategory('NAD+与抗衰老');

      onSuccess();
    } catch (error: any) {
      console.error('添加知识失败:', error);
      showError(`添加失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`knowledge-panel ${isOpen ? 'open' : ''}`}>
      <div className="panel-header">
        <h2 className="panel-title">🧬 添加抗衰老知识</h2>
        <button className="close-btn" onClick={onClose}>
          ×
        </button>
      </div>

      <div className="panel-content">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">🏷️ 知识分类</label>
            <input
              type="text"
              className="form-input"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="例如：NAD+与抗衰老、NMN补充指南、线粒体健康"
            />
          </div>

          <div className="form-group">
            <label className="form-label">📝 知识内容 *</label>
            <textarea
              className="form-textarea"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="请输入抗衰老相关的科学知识，建议包含研究来源、具体建议和注意事项..."
              required
            />
          </div>

          <button
            type="submit"
            className="submit-btn"
            disabled={loading || !content.trim()}
          >
            {loading ? '添加中...' : '添加知识'}
          </button>
        </form>

        <div style={{ marginTop: '24px', padding: '16px', background: 'linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%)', borderRadius: '8px', border: '1px solid #10b981' }}>
          <h3 style={{ fontSize: '14px', marginBottom: '8px', color: '#047857', fontWeight: 'bold' }}>💡 知识添加建议</h3>
          <ul style={{ fontSize: '12px', color: '#065f46', lineHeight: '1.8', paddingLeft: '20px' }}>
            <li>📚 <strong>引用来源</strong>：注明研究出处（如 Nature, Cell 等）</li>
            <li>💊 <strong>具体建议</strong>：包含剂量、时间、使用方法</li>
            <li>⚠️ <strong>安全提醒</strong>：说明副作用和注意事项</li>
            <li>🎯 <strong>分类清晰</strong>：便于专业知识检索</li>
            <li>🔬 <strong>科学严谨</strong>：基于循证医学证据</li>
          </ul>
        </div>
      </div>
      <MessageContainer />
    </div>
  );
};

export default KnowledgePanel;

