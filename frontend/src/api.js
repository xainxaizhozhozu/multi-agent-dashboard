/**
 * 前端 API 请求模块
 * 
 * 封装 axios，统一配置：
 * - Base URL（开发时通过 Vite proxy 代理到后端）
 * - 错误处理
 * - 请求/响应拦截
 */

import axios from 'axios';

// ── 创建 axios 实例 ───────────────────────────────
const api = axios.create({
  baseURL: '/api/v1',       // 相对路径，由 Vite dev server 代理
  timeout: 60000,           // 60秒超时（Agent 推理可能需要较长时间）
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── 请求拦截器（自动附加 token）────────────────────
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ── 响应拦截器（统一错误处理）──────────────────────
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (error.response) {
      // 服务器返回了错误状态码
      console.error(`API Error ${error.response.status}:`, error.response.data);
      return Promise.reject(error.response.data);
    } else if (error.code === 'ECONNABORTED') {
      console.error('请求超时，请稍后重试');
      return Promise.reject({ detail: '请求超时，请检查网络连接' });
    } else {
      console.error('网络错误，请检查后端服务是否启动');
      return Promise.reject({ detail: '网络连接失败，请确保后端运行在 localhost:8000' });
    }
  }
);

// ── 看板数据接口 ──────────────────────────────────
export const dashboardApi = {
  /** 获取整体统计摘要 */
  getStats() {
    return api.get('/dashboard/stats');
  },
  /** 获取月度趋势 */
  getMonthlyTrend() {
    return api.get('/dashboard/trends/monthly');
  },
  /** 获取日趋势 */
  getDailyTrend() {
    return api.get('/dashboard/trends/daily');
  },
  /** 按地区分析 */
  getByRegion() {
    return api.get('/dashboard/analysis/by-region');
  },
  /** 按品类分析 */
  getByCategory() {
    return api.get('/dashboard/analysis/by-category');
  },
};

// ── Agent 交互接口 ────────────────────────────────
export const agentApi = {
  /** 发送问题给 Agent 处理 */
  async chat(query, sessionId = '') {
    return await api.post('/agent/chat', { query, session_id: sessionId });
  },
  
  /** 查看 Agent 系统状态 */
  status() {
    return api.get('/agent/status');
  },
};

export default api;
