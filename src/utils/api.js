/**
 * API 工具函数
 * 用于与 Django 后端通信
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * 通用请求函数
 */
async function request(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
    },
  };

  const config = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  try {
    const response = await fetch(url, config);
    const data = await response.json();
    
    if (!response.ok) {
      // 如果响应包含错误消息，抛出包含消息的错误
      const errorMessage = data.message || data.error || `HTTP error! status: ${response.status}`;
      const error = new Error(errorMessage);
      error.response = response;
      error.data = data;
      throw error;
    }
    
    return data;
  } catch (error) {
    // 如果是网络错误或其他错误，保留原始错误
    if (!error.response) {
      console.error('API request failed:', error);
    }
    throw error;
  }
}

/**
 * GET 请求
 */
export function get(endpoint) {
  return request(endpoint, { method: 'GET' });
}

/**
 * POST 请求
 */
export function post(endpoint, data) {
  return request(endpoint, {
    method: 'POST',
    body: JSON.stringify(data),
  });
}

/**
 * PUT 请求
 */
export function put(endpoint, data) {
  return request(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data),
  });
}

/**
 * DELETE 请求
 */
export function del(endpoint) {
  return request(endpoint, { method: 'DELETE' });
}

// API 端点
export const api = {
  // 健康检查
  health: () => get('/api/health/'),
  
  // 仪表盘
  getDashboard: () => get('/api/dashboard/'),
  
  // 策略
  getStrategies: () => get('/api/strategies/'),
  createStrategy: (data) => post('/api/strategy/create/', data),
  
  // 设置
  getExchangeSettings: (exchange = 'binance') => get(`/api/settings/exchange/get/?exchange=${exchange}`),
  saveExchangeSettings: (data) => post('/api/settings/exchange/', data),
  getAISettings: (provider = 'deepseek') => get(`/api/settings/ai/get/?provider=${provider}`),
  saveAISettings: (data) => post('/api/settings/ai/', data),
  
  // Prompt
  getPromptsList: () => get('/api/prompts/'),
  getPrompt: (name) => get(`/api/prompt/${name}/`),
  savePrompt: (data) => post('/api/prompt/', data),
  deletePrompt: (name) => del(`/api/prompt/${name}/delete/`),
  
  // Plans
  getPlans: () => get('/api/plans/'),
  createPlan: (data) => post('/api/plan/create/', data),
};


