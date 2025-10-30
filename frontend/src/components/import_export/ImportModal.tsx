/**
 * 文件上传导入组件
 */
import React, { useState, useRef } from 'react';
import { importKnowledge } from '../../services/api';
import { useMessage } from '../common/Message';

interface ImportModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: () => void;
}

const ImportModal: React.FC<ImportModalProps> = ({ isOpen, onClose, onSuccess }) => {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [importResult, setImportResult] = useState<any>(null);
  const [previewData, setPreviewData] = useState<any[]>([]);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  const { showSuccess, showError, MessageContainer } = useMessage();

  const handleFileSelect = (selectedFile: File) => {
    // 验证文件类型
    const allowedExtensions = ['.json', '.csv', '.xlsx', '.xls', '.txt', '.md', '.pdf'];
    const fileExt = selectedFile.name.toLowerCase().substring(selectedFile.name.lastIndexOf('.'));
    
    if (!allowedExtensions.includes(fileExt)) {
      showError(`不支持的文件格式。支持格式：${allowedExtensions.join(', ')}`);
      return;
    }

    // 验证文件大小（最大 10MB）
    if (selectedFile.size > 10 * 1024 * 1024) {
      showError('文件大小不能超过 10MB');
      return;
    }

    setFile(selectedFile);
    setImportResult(null);
    setPreviewData([]);
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);

    const droppedFile = e.dataTransfer.files[0];
    if (droppedFile) {
      handleFileSelect(droppedFile);
    }
  };

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      handleFileSelect(selectedFile);
    }
  };

  const handleImport = async () => {
    if (!file) {
      showError('请先选择文件');
      return;
    }

    setLoading(true);
    try {
      const result = await importKnowledge(file);
      setImportResult(result);
      setPreviewData(result.preview || []);

      if (result.success_count > 0) {
        showSuccess(`成功导入 ${result.success_count} 条知识！`);
        if (result.failed_count > 0) {
          showError(`有 ${result.failed_count} 条导入失败，请查看详情`);
        }
        setTimeout(() => {
          onSuccess();
          handleClose();
        }, 2000);
      } else {
        showError('导入失败，没有成功导入任何知识');
      }
    } catch (error: any) {
      console.error('导入失败:', error);
      showError(`导入失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setFile(null);
    setImportResult(null);
    setPreviewData([]);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    onClose();
  };

  const getFileIcon = (filename: string) => {
    const ext = filename.toLowerCase().substring(filename.lastIndexOf('.'));
    const iconMap: Record<string, string> = {
      '.json': '📄',
      '.csv': '📊',
      '.xlsx': '📗',
      '.xls': '📗',
      '.txt': '📝',
      '.md': '📖',
      '.pdf': '📕',
    };
    return iconMap[ext] || '📎';
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(2) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB';
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
      onClick={handleClose}
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
        {/* 头部 */}
        <div style={{ padding: '24px 32px', borderBottom: '1px solid #e5e7eb' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h2 style={{ margin: 0, fontSize: '24px', fontWeight: 'bold', color: '#333' }}>
              📤 导入知识库文件
            </h2>
            <button
              onClick={handleClose}
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

        {/* 内容区域 */}
        <div style={{ flex: 1, overflowY: 'auto', padding: '24px 32px' }}>
          {/* 文件上传区域 */}
          <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            style={{
              border: `2px dashed ${isDragging ? '#667eea' : '#d1d5db'}`,
              borderRadius: '12px',
              padding: '40px',
              textAlign: 'center',
              background: isDragging ? '#f0f4ff' : '#f9fafb',
              transition: 'all 0.3s',
              cursor: 'pointer',
            }}
            onClick={() => fileInputRef.current?.click()}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept=".json,.csv,.xlsx,.xls,.txt,.md,.pdf"
              style={{ display: 'none' }}
              onChange={handleFileInputChange}
            />

            {!file ? (
              <>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>📎</div>
                <p style={{ fontSize: '16px', color: '#374151', marginBottom: '8px' }}>
                  点击或拖拽文件到此处上传
                </p>
                <p style={{ fontSize: '14px', color: '#6b7280' }}>
                  支持格式：JSON, CSV, Excel, TXT, Markdown, PDF
                </p>
                <p style={{ fontSize: '12px', color: '#9ca3af', marginTop: '8px' }}>
                  最大文件大小：10MB
                </p>
              </>
            ) : (
              <div>
                <div style={{ fontSize: '48px', marginBottom: '16px' }}>
                  {getFileIcon(file.name)}
                </div>
                <p style={{ fontSize: '16px', color: '#374151', fontWeight: '500', marginBottom: '4px' }}>
                  {file.name}
                </p>
                <p style={{ fontSize: '14px', color: '#6b7280' }}>
                  {formatFileSize(file.size)}
                </p>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setFile(null);
                    setImportResult(null);
                    setPreviewData([]);
                    if (fileInputRef.current) {
                      fileInputRef.current.value = '';
                    }
                  }}
                  style={{
                    marginTop: '12px',
                    padding: '6px 16px',
                    background: '#ef4444',
                    color: 'white',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontSize: '14px',
                  }}
                >
                  重新选择
                </button>
              </div>
            )}
          </div>

          {/* 预览数据 */}
          {previewData.length > 0 && (
            <div style={{ marginTop: '24px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 'bold', color: '#333', marginBottom: '12px' }}>
                预览数据（前5条）
              </h3>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                {previewData.map((item: any, idx: number) => (
                  <div
                    key={idx}
                    style={{
                      background: '#f9fafb',
                      padding: '12px',
                      borderRadius: '8px',
                      border: '1px solid #e5e7eb',
                    }}
                  >
                    <div style={{ display: 'flex', gap: '8px', marginBottom: '4px' }}>
                      <span
                        style={{
                          background: '#e0e7ff',
                          color: '#4f46e5',
                          padding: '2px 8px',
                          borderRadius: '4px',
                          fontSize: '12px',
                        }}
                      >
                        {item.category || '未分类'}
                      </span>
                      {item.title && (
                        <span style={{ fontSize: '14px', fontWeight: '500', color: '#333' }}>
                          {item.title}
                        </span>
                      )}
                    </div>
                    <p
                      style={{
                        fontSize: '13px',
                        color: '#6b7280',
                        margin: 0,
                        lineHeight: '1.5',
                      }}
                    >
                      {item.content.substring(0, 100)}
                      {item.content.length > 100 ? '...' : ''}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 导入结果 */}
          {importResult && (
            <div style={{ marginTop: '24px' }}>
              <h3 style={{ fontSize: '16px', fontWeight: 'bold', color: '#333', marginBottom: '12px' }}>
                导入结果
              </h3>
              <div
                style={{
                  background: '#f0fdf4',
                  border: '1px solid #86efac',
                  borderRadius: '8px',
                  padding: '16px',
                }}
              >
                <div style={{ display: 'flex', gap: '24px', marginBottom: '12px' }}>
                  <div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#16a34a' }}>
                      {importResult.success_count}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>成功</div>
                  </div>
                  {importResult.failed_count > 0 && (
                    <div>
                      <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#ef4444' }}>
                        {importResult.failed_count}
                      </div>
                      <div style={{ fontSize: '12px', color: '#6b7280' }}>失败</div>
                    </div>
                  )}
                  <div>
                    <div style={{ fontSize: '24px', fontWeight: 'bold', color: '#374151' }}>
                      {importResult.total_count}
                    </div>
                    <div style={{ fontSize: '12px', color: '#6b7280' }}>总计</div>
                  </div>
                </div>

                {importResult.errors.length > 0 && (
                  <div style={{ marginTop: '12px' }}>
                    <div style={{ fontSize: '14px', fontWeight: '500', color: '#dc2626', marginBottom: '8px' }}>
                      错误详情：
                    </div>
                    <div style={{ maxHeight: '150px', overflowY: 'auto' }}>
                      {importResult.errors.map((error: any, idx: number) => (
                        <div
                          key={idx}
                          style={{
                            fontSize: '12px',
                            color: '#6b7280',
                            padding: '4px 0',
                          }}
                        >
                          第 {error.row} 行: {error.error}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* 格式说明 */}
          <div style={{ marginTop: '24px', padding: '16px', background: '#fef3c7', borderRadius: '8px' }}>
            <h4 style={{ fontSize: '14px', fontWeight: 'bold', color: '#92400e', marginBottom: '8px' }}>
              💡 格式说明
            </h4>
            <ul style={{ fontSize: '12px', color: '#78350f', paddingLeft: '20px', margin: 0, lineHeight: '1.8' }}>
              <li>
                <strong>JSON</strong>：数组格式，每项包含 content（必填）和 category（可选）
                <a
                  href="/templates/knowledge_template.json"
                  download="knowledge_template.json"
                  style={{ marginLeft: '8px', color: '#2563eb', textDecoration: 'underline', cursor: 'pointer' }}
                  onClick={(e) => e.stopPropagation()}
                >
                  📥 下载模板
                </a>
              </li>
              <li>
                <strong>CSV</strong>：第一行为表头（content, category, title, tags）
                <a
                  href="/templates/knowledge_template.csv"
                  download="knowledge_template.csv"
                  style={{ marginLeft: '8px', color: '#2563eb', textDecoration: 'underline', cursor: 'pointer' }}
                  onClick={(e) => e.stopPropagation()}
                >
                  📥 下载模板
                </a>
              </li>
              <li>
                <strong>Excel</strong>：表头格式同 CSV，tags 列用逗号分隔
                <span style={{ marginLeft: '8px', color: '#6b7280', fontSize: '11px' }}>
                  （参考 CSV 模板）
                </span>
              </li>
              <li>
                <strong>TXT</strong>：每行一条知识，可用"分类|内容"格式
                <a
                  href="/templates/knowledge_template.txt"
                  download="knowledge_template.txt"
                  style={{ marginLeft: '8px', color: '#2563eb', textDecoration: 'underline', cursor: 'pointer' }}
                  onClick={(e) => e.stopPropagation()}
                >
                  📥 下载模板
                </a>
              </li>
              <li>
                <strong>Markdown</strong>：# 分类名称，## 知识标题，后跟内容
                <a
                  href="/templates/knowledge_template.md"
                  download="knowledge_template.md"
                  style={{ marginLeft: '8px', color: '#2563eb', textDecoration: 'underline', cursor: 'pointer' }}
                  onClick={(e) => e.stopPropagation()}
                >
                  📥 下载模板
                </a>
              </li>
              <li>
                <strong>PDF</strong>：自动提取每页文本，每页作为一条知识
                <span style={{ marginLeft: '8px', color: '#6b7280', fontSize: '11px' }}>
                  （无需模板，直接上传 PDF 文件）
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* 底部操作栏 */}
        <div style={{ padding: '20px 32px', borderTop: '1px solid #e5e7eb', display: 'flex', gap: '12px', justifyContent: 'flex-end' }}>
          <button
            onClick={handleClose}
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
            onClick={handleImport}
            disabled={loading || !file}
            style={{
              padding: '10px 20px',
              borderRadius: '8px',
              border: 'none',
              background: loading || !file
                ? '#9ca3af'
                : 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              color: 'white',
              cursor: loading || !file ? 'not-allowed' : 'pointer',
              fontSize: '14px',
              fontWeight: '500',
            }}
          >
            {loading ? '导入中...' : '开始导入'}
          </button>
        </div>

        <MessageContainer />
      </div>
    </div>
  );
};

export default ImportModal;

