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
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('API request failed:', error);
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
  saveExchangeSettings: (data) => post('/api/settings/exchange/', data),
  saveAISettings: (data) => post('/api/settings/ai/', data),
};


