/**
 * 类型定义文件
 */

// 消息类型
export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  imageUrl?: string;
  timestamp: number;
  confidence?: '高' | '中' | '低';
  sources?: string[];
}

// 对话请求
export interface ChatRequest {
  question: string;
  image_url?: string;
  image_base64?: string;
  use_knowledge_base?: boolean;
  history?: {
    role: string;
    content: string;
  }[];
}

// 对话响应
export interface ChatResponse {
  answer: string;
  confidence: '高' | '中' | '低';
  knowledge_sources: string[];
  model_used: string;
  has_image: boolean;
}

// 知识库条目
export interface KnowledgeItem {
  content: string;
  category: string;
  title?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

// 知识库搜索结果
export interface KnowledgeSearchResult {
  content: string;
  category: string;
  score: number;
  metadata: {
    created_at?: string;
    id?: string;
    [key: string]: any;
  };
}

// 知识库详情
export interface KnowledgeDetail {
  doc_id: string;
  content: string;
  category: string;
  title?: string;
  tags?: string[];
  created_at: string;
  updated_at?: string;
  metadata: Record<string, any>;
  chunks: Array<{
    chunk_index: number;
    content: string;
    id: string;
  }>;
}

// 知识库更新请求
export interface KnowledgeUpdate {
  content?: string;
  category?: string;
  title?: string;
  tags?: string[];
  metadata?: Record<string, any>;
}

