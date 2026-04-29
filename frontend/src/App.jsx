import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import liff from '@line/liff';

// コンポーネントとAPIの読み込み
import Dashboard from './Dashboard';
import Login from './Login';
import MyPage from './MyPage';
import AllStatus from './AllStatus';
import Categories from './Categories';
import EditEquipment from './EditEquipment';
import { getCurrentUser, lineLogin } from './api';

function App() {
  const [currentUser, setCurrentUser] = useState({ is_authenticated: false });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initApp = async () => {
      try {
        // 1. まずは既存のセッション（Cookie）があるか確認
        const data = await getCurrentUser();
        if (data.is_authenticated) {
          setCurrentUser(data);
          setLoading(false);
          return;
        }

        // 2. セッションがなければ LIFF を初期化
        await liff.init({ liffId: import.meta.env.VITE_LIFF_ID });

        // 3. LINEログイン済み（リダイレクト後）であればバックエンドに通知
        if (liff.isLoggedIn()) {
          const idToken = liff.getIDToken();
          if (idToken) {
            const loginRes = await lineLogin(idToken);
            if (loginRes.status === 'success') {
              setCurrentUser({ is_authenticated: true, ...loginRes.user });
            }
          }
        }
      } catch (err) {
        console.error("初期化エラー:", err);
      } finally {
        setLoading(false);
      }
    };

    initApp();
  }, []);

  if (loading) return <div className="text-center mt-5"><div className="spinner-border"></div></div>;

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Dashboard currentUser={currentUser} setCurrentUser={setCurrentUser} />} />
        <Route path="/login" element={<Login setCurrentUser={setCurrentUser} />} />
        <Route path="/mypage" element={<MyPage currentUser={currentUser} setCurrentUser={setCurrentUser} />} />
        <Route path="/all_status" element={<AllStatus currentUser={currentUser} />} />
        <Route path="/categories" element={<Categories currentUser={currentUser} />} />
        <Route path="/edit/:id" element={<EditEquipment currentUser={currentUser} />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;