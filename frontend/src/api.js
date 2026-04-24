/**
 * API 通信用ユーティリティ
 * 環境に応じて自動的に BaseURL を切り替える
 */

// Viteの環境変数から BaseURL を取得
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

/**
 * API リクエストを送信するヘルパー関数
 * @param {string} endpoint - エンドポイント（例: '/auth/me'）
 * @param {object} options - fetch のオプション
 * @returns {Promise<Response>}
 */
export const apiCall = async (endpoint, options = {}) => {
  // credentials を指定してクッキーベースの認証に対応
  const defaultOptions = {
    credentials: 'include', // クッキーを含める
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  };

  const url = `${API_BASE_URL}${endpoint}`;
  
  console.log(`[API] ${options.method || 'GET'} ${url}`); // デバッグ用

  const response = await fetch(url, defaultOptions);
  return response;
};

/**
 * JSON レスポンスを返すラッパー
 */
export const apiCallJson = async (endpoint, options = {}) => {
  const response = await apiCall(endpoint, options);
  return response.json();
};

/**
 * 認証ユーザー情報を取得
 */
export const getCurrentUser = async () => {
  try {
    return await apiCallJson('/auth/me');
  } catch (error) {
    console.error('ユーザー情報取得エラー:', error);
    throw error;
  }
};

/**
 * ログイン
 */
export const login = async (username, password) => {
  return await apiCallJson('/login', {
    method: 'POST',
    body: JSON.stringify({ username, password }),
  });
};

/**
 * ログアウト
 */
export const logout = async () => {
  return await apiCallJson('/logout', {
    method: 'POST',
  });
};

/**
 * ユーザー登録
 */
export const register = async (username, password, confirm_password) => {
  return await apiCallJson('/register', {
    method: 'POST',
    body: JSON.stringify({ username, password, confirm_password }),
  });
};

/**
 * 備品一覧を取得
 */
export const getEquipment = async (searchQuery = '', categoryFilter = '') => {
  const params = new URLSearchParams();
  if (searchQuery) params.append('q', searchQuery);
  if (categoryFilter) params.append('category', categoryFilter);

  const queryString = params.toString();
  const url = queryString ? `/api/equipment?${queryString}` : '/api/equipment';
  return await apiCallJson(url);
};

/**
 * My Page 情報を取得
 */
export const getMyPage = async () => {
  return await apiCallJson('/api/mypage');
};

/**
 * 備品を借りる
 */
export const borrowEquipment = async (equipmentId) => {
  return await apiCallJson(`/api/borrow/${equipmentId}`, {
    method: 'POST',
  });
};

/**
 * 備品を返却
 */
export const returnEquipment = async (equipmentId) => {
  return await apiCallJson(`/api/return/${equipmentId}`, {
    method: 'POST',
  });
};

/**
 * 全ユーザー・全履歴を取得（管理者）
 */
export const getAllStatus = async () => {
  return await apiCallJson('/api/all_status');
};

/**
 * カテゴリ一覧を取得
 */
export const getCategories = async () => {
  return await apiCallJson('/api/categories');
};

export default {
  apiCall,
  apiCallJson,
  getCurrentUser,
  login,
  logout,
  register,
  getEquipment,
  getMyPage,
  borrowEquipment,
  returnEquipment,
  getAllStatus,
  getCategories,
};
