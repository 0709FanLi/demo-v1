/**
 * 知识库管理面板组件
 */

import React, { useState } from 'react';
import { addKnowledge } from '../services/api';
import { KnowledgeItem } from '../types';

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
  const [category, setCategory] = useState('通用');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!content.trim()) {
      alert('请输入知识内容');
      return;
    }

    setLoading(true);

    try {
      const knowledge: KnowledgeItem = {
        content: content.trim(),
        category: category.trim(),
      };

      await addKnowledge(knowledge);
      alert('知识添加成功！');

      // 重置表单
      setContent('');
      setCategory('通用');

      onSuccess();
    } catch (error: any) {
      console.error('添加知识失败:', error);
      alert(`添加失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`knowledge-panel ${isOpen ? 'open' : ''}`}>
      <div className="panel-header">
        <h2 className="panel-title">添加知识</h2>
        <button className="close-btn" onClick={onClose}>
          ×
        </button>
      </div>

      <div className="panel-content">
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">知识分类</label>
            <input
              type="text"
              className="form-input"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="例如：产品介绍、售后政策"
            />
          </div>

          <div className="form-group">
            <label className="form-label">知识内容 *</label>
            <textarea
              className="form-textarea"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              placeholder="请输入知识内容，支持多行文本..."
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

        <div style={{ marginTop: '24px', padding: '16px', background: '#f5f5f5', borderRadius: '8px' }}>
          <h3 style={{ fontSize: '14px', marginBottom: '8px' }}>💡 使用提示</h3>
          <ul style={{ fontSize: '12px', color: '#666', lineHeight: '1.6', paddingLeft: '20px' }}>
            <li>添加的知识会被用于RAG对话</li>
            <li>建议按主题分类，便于管理</li>
            <li>内容应准确、完整、易懂</li>
            <li>支持批量添加（API接口）</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default KnowledgePanel;

