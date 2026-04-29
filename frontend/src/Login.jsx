import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import liff from '@line/liff';
import { lineLogin } from './api'; // 先ほど更新したAPI関数
import './Login.css'; // 必要に応じてスタイルを読み込む

const Login = ({ setCurrentUser }) => { 
  const [isInitialized, setIsInitialized] = useState(false);
  const [liffError, setLiffError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const initLiff = async () => {
      try {
        await liff.init({ liffId: import.meta.env.VITE_LIFF_ID });
        setIsInitialized(true);

        if (liff.isLoggedIn()) {
          const idToken = liff.getIDToken();
          if (idToken) {
            const response = await lineLogin(idToken);
            
            if (response.status === 'success') {
              // ✅ 2. ここを追加！ アプリ全体にユーザー情報をセットする
              setCurrentUser({
                is_authenticated: true,
                ...response.user
              });
              
              // ログイン成功したらダッシュボードへ
              navigate('/');            // ✅ 変更後（App.jsx のパスに合わせる
            } else {
              setLiffError(response.message || 'ログインに失敗しました');
            }
          }
        }
      } catch (error) {
        console.error('LIFF Initialization failed', error);
        setLiffError('LIFFの初期化に失敗しました。');
      }
    };
    initLiff();
  }, [navigate, setCurrentUser]); // setCurrentUser を依存関係に追加

  const handleLoginClick = () => {
    if (!isInitialized) return;
    
    // LINEのログイン画面（または認可画面）へリダイレクト
    if (!liff.isLoggedIn()) {
      liff.login();
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h1>ASAproject (CampKit)</h1>
        <p>備品管理システムへようこそ</p>

        {liffError && <p className="error-message" style={{ color: 'red' }}>{liffError}</p>}

        {!isInitialized ? (
          <p>読み込み中...</p>
        ) : (
          <button 
            onClick={handleLoginClick} 
            style={{
              backgroundColor: '#06C755', // LINE公式グリーン
              color: 'white',
              border: 'none',
              padding: '12px 24px',
              fontSize: '16px',
              fontWeight: 'bold',
              borderRadius: '8px',
              cursor: 'pointer',
              width: '100%',
              marginTop: '20px'
            }}
          >
            LINEでログイン
          </button>
        )}
      </div>
    </div>
  );
};

export default Login;