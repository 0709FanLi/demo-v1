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
  metadata?: Record<string, any>;
}

