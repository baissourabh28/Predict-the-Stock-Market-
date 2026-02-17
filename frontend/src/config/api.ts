// API Configuration
export const API_CONFIG = {
  baseURL: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  apiVersion: process.env.REACT_APP_API_VERSION || 'v1',
  timeout: 30000,
  enableMockData: process.env.REACT_APP_ENABLE_MOCK_DATA === 'true',
};

export const getApiUrl = (endpoint: string): string => {
  return `${API_CONFIG.baseURL}/api/${API_CONFIG.apiVersion}${endpoint}`;
};

export default API_CONFIG;
