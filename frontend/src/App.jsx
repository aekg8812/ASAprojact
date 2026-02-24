import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';

// 各画面の読み込み
import Dashboard from './Dashboard';
import Login from './Login';
import Register from './Register';
import ResetPassword from './ResetPassword';
import MyPage from './MyPage';
import EditEquipment from './EditEquipment';
import AllStatus from './AllStatus';
import Categories from './Categories';

function App() {
  // 🌟 アプリ全体で共有する「現在のユーザー情報」
  const [currentUser, setCurrentUser] = useState({ is_authenticated: false });
  const [loading, setLoading] = useState(true);

  // アプリ起動時に、Flaskに「ログイン状態」を確認しに行く
  useEffect(() => {
    fetch('https://asa-app-ayato.onrender.com/auth/me', { credentials: 'include' })
      .then(res => res.json())
      .then(data => {
        if (data.is_authenticated) {
          setCurrentUser(data); // ログインしていれば情報をセット
        }
        setLoading(false);
      })
      .catch(err => {
        console.error("ログイン確認エラー:", err);
        setLoading(false);
      });
  }, []);

  // 読み込み中の一瞬だけ表示する画面
  if (loading) return <div className="d-flex justify-content-center mt-5"><div className="spinner-border text-primary"></div></div>;

  return (
    <BrowserRouter>
      <Routes>
        {/* 各画面に currentUser（ユーザー情報）と setCurrentUser（情報更新スイッチ）を渡す！ */}
        <Route path="/" element={<Dashboard currentUser={currentUser} setCurrentUser={setCurrentUser} />} />
        <Route path="/login" element={<Login setCurrentUser={setCurrentUser} />} />
        <Route path="/register" element={<Register />} />
        <Route path="/reset_password" element={<ResetPassword />} />
        <Route path="/mypage" element={<MyPage currentUser={currentUser} setCurrentUser={setCurrentUser} />} />
        <Route path="/all_status" element={<AllStatus currentUser={currentUser} />} />
        <Route path="/categories" element={<Categories currentUser={currentUser} />} />
        <Route path="/edit/:id" element={<EditEquipment currentUser={currentUser} />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;