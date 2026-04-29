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
    credentials: 'include', // ★これがFlask-Loginのセッション維持に必須
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
 * LINEログイン (新規登録 / ログイン兼用)
 * @param {string} idToken - LIFFから取得したIDトークン
 */
export const lineLogin = async (idToken) => {
  return await apiCallJson('/auth/line-login', { // ✅ /auth/ を先頭に付ける
    method: 'POST',
    body: JSON.stringify({ idToken }),
  });
};

/**
 * ログアウト ✅ エンドポイント修正
 */
export const logout = async () => {
  return await apiCallJson('/auth/logout', {
    method: 'POST',
  });
};

/**
 * アカウント削除 ✅ 新規追加
 */
export const deleteAccount = async () => {
  return await apiCallJson('/auth/delete_account', {
    method: 'POST',
  });
};

/**
 * ユーザーを削除（管理者）✅ 新規追加
 */
export const deleteUser = async (userId) => {
  return await apiCallJson(`/api/delete_user/${userId}`, {
    method: 'POST',
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
 * 備品の編集画面データを取得 ✅ 新規追加
 */
export const getEditEquipment = async (equipmentId) => {
  return await apiCallJson(`/api/edit/${equipmentId}`);
};

/**
 * 備品を更新（管理者） ✅ 新規追加
 */
export const updateEquipment = async (equipmentId, formData) => {
  const options = {
    method: 'POST',
    credentials: 'include',
    body: formData,
    headers: {},
  };
  
  const url = `${API_BASE_URL}/api/edit/${equipmentId}`;
  const response = await fetch(url, options);
  return response.json();
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

/**
 * カテゴリを追加（管理者） ✅ 新規追加
 */
export const addCategory = async (name) => {
  return await apiCallJson('/api/categories/add', {
    method: 'POST',
    body: JSON.stringify({ name }),
  });
};

/**
 * カテゴリを削除（管理者） ✅ 新規追加
 */
export const deleteCategory = async (categoryId) => {
  return await apiCallJson(`/api/categories/delete/${categoryId}`, {
    method: 'POST',
  });
};

/**
 * カテゴリの順序を変更 ✅ 新規追加
 */
export const reorderCategories = async (order) => {
  return await apiCallJson('/api/categories/reorder', {
    method: 'POST',
    body: JSON.stringify({ order }),
  });
};

/**
 * 備品を追加（管理者）✅ 新規追加
 */
export const addEquipment = async (formData) => {
  const options = {
    method: 'POST',
    credentials: 'include',
    body: formData,
    headers: {},
  };
  
  const url = `${API_BASE_URL}/api/add`;
  const response = await fetch(url, options);
  return response.json();
};

/**
 * 備品を削除（管理者）✅ 新規追加
 */
export const deleteEquipment = async (equipmentId) => {
  return await apiCallJson(`/api/delete/${equipmentId}`, {
    method: 'POST',
  });
};

export default {
  apiCall,
  apiCallJson,
  getCurrentUser,
  lineLogin,
  logout,
  deleteAccount,
  deleteUser,
  getEquipment,
  getEditEquipment,
  updateEquipment,
  getMyPage,
  borrowEquipment,
  returnEquipment,
  getAllStatus,
  getCategories,
  addCategory,
  deleteCategory,
  reorderCategories,
  addEquipment,
  deleteEquipment,
};