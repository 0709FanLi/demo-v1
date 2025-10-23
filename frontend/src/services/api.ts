/**
 * API服务封装
 * 调用后端接口
 */

import axios, { AxiosInstance } from 'axios';
import { ChatRequest, ChatResponse, KnowledgeItem } from '../types';

// API基础URL（可通过环境变量配置）
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// 创建axios实例
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60秒超时
  headers: {
    'Content-Type': 'application/json',
  },
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    console.log('API请求:', config.method?.toUpperCase(), config.url);
    return config;
  },
  (error) => {
    console.error('请求错误:', error);
    return Promise.reject(error);
  }
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => {
    console.log('API响应:', response.status, response.data);
    return response;
  },
  (error) => {
    console.error('响应错误:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

/**
 * RAG对话接口
 */
export const chatWithRAG = async (request: ChatRequest): Promise<ChatResponse> => {
  const response = await apiClient.post<ChatResponse>('/api/v1/chat/', request);
  return response.data;
};

/**
 * 图文对话接口（文件上传）
 */
export const chatWithImage = async (
  question: string,
  imageFile: File,
  useKnowledge: boolean = true
): Promise<ChatResponse> => {
  const formData = new FormData();
  formData.append('question', question);
  formData.append('image', imageFile);
  formData.append('use_knowledge_base', String(useKnowledge));

  const response = await apiClient.post<ChatResponse>(
    '/api/v1/chat/with-image',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    }
  );
  return response.data;
};

/**
 * 简单对话接口
 */
export const chatSimple = async (
  question: string,
  useKnowledge: boolean = true
): Promise<{ question: string; answer: string }> => {
  const response = await apiClient.get('/api/v1/chat/simple', {
    params: { question, use_knowledge: useKnowledge },
  });
  return response.data;
};

/**
 * 添加知识条目
 */
export const addKnowledge = async (knowledge: KnowledgeItem): Promise<any> => {
  const response = await apiClient.post('/api/v1/knowledge/add', knowledge);
  return response.data;
};

/**
 * 批量添加知识
 */
export const addKnowledgeBatch = async (knowledgeList: KnowledgeItem[]): Promise<any> => {
  const response = await apiClient.post('/api/v1/knowledge/add-batch', knowledgeList);
  return response.data;
};

/**
 * 搜索知识
 */
export const searchKnowledge = async (
  query: string,
  topK: number = 3
): Promise<any> => {
  const response = await apiClient.get('/api/v1/knowledge/search', {
    params: { query, top_k: topK },
  });
  return response.data;
};

/**
 * 获取知识库统计
 */
export const getKnowledgeCount = async (): Promise<{ total: number; message: string }> => {
  const response = await apiClient.get('/api/v1/knowledge/count');
  return response.data;
};

/**
 * 健康检查
 */
export const healthCheck = async (): Promise<any> => {
  const response = await apiClient.get('/health');
  return response.data;
};

