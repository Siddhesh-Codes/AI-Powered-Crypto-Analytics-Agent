// API Configuration
const getApiUrl = (): string => {
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL.replace(/\/$/, '');
  }
  return 'http://localhost:8000';
};

const getWsUrl = (): string => {
  if (process.env.REACT_APP_WS_URL) {
    return process.env.REACT_APP_WS_URL;
  }
  const apiUrl = getApiUrl();
  return apiUrl.replace(/^http/, 'ws');
};

export const API_BASE_URL = getApiUrl();
export const WS_BASE_URL = getWsUrl();

export const API_CONFIG = {
  BASE_URL: API_BASE_URL,
  WS_URL: WS_BASE_URL
};

export default API_CONFIG;

