import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const ResetPassword = () => {
    const [step, setStep] = useState('input_user');
    const [userId, setUserId] = useState(null);
    const [username, setUsername] = useState('');
    const [passwords, setPasswords] = useState({ new: '', confirm: '' });
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    // ステップ1：ユーザーが存在するかチェック
    const handleCheckUser = (e) => {
        e.preventDefault();
        setError(null);
        fetch('https://asa-app-ayato.onrender.com/reset_password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ step: 'check_user', username: username })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                setUserId(data.user_id);
                setStep('new_pass');
            } else {
                setError(data.message);
            }
        });
    };

    // ステップ2：新しいパスワードを登録
    const handleReset = (e) => {
        e.preventDefault();
        setError(null);
        fetch('https://asa-app-ayato.onrender.com/reset_password', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                step: 'reset_pass', 
                user_id: userId, 
                new_password: passwords.new, 
                confirm_password: passwords.confirm 
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                navigate('/login');
            } else {
                setError(data.message);
            }
        });
    };

    return (
        <div className="bg-light d-flex align-items-center justify-content-center" style={{ height: '100vh' }}>
            <div className="card shadow p-4" style={{ width: '450px' }}>
                <h4 className="text-center mb-4"><i className="bi bi-key-fill"></i> パスワード再設定</h4>
                {error && <div className="alert alert-danger">{error}</div>}

                {step === 'input_user' ? (
                    <form onSubmit={handleCheckUser}>
                        <div className="mb-3">
                            <label className="form-label">ユーザー名</label>
                            <input type="text" className="form-control" placeholder="登録したユーザー名" required value={username} onChange={(e) => setUsername(e.target.value)} />
                        </div>
                        <button type="submit" className="btn btn-primary w-100">次へ</button>
                    </form>
                ) : (
                    <form onSubmit={handleReset}>
                        <p className="mb-3 text-center">対象ユーザー: <strong>{username}</strong></p>
                        <div className="mb-3">
                            <label className="form-label">新しいパスワード</label>
                            <input type="password" className="form-control" required value={passwords.new} onChange={(e) => setPasswords({...passwords, new: e.target.value})} />
                        </div>
                        <div className="mb-3">
                            <label className="form-label">確認用</label>
                            <input type="password" className="form-control" required value={passwords.confirm} onChange={(e) => setPasswords({...passwords, confirm: e.target.value})} />
                        </div>
                        <button type="submit" className="btn btn-danger w-100">変更を保存してログイン</button>
                    </form>
                )}
                <div className="mt-3 text-center">
                    <Link to="/login" className="text-secondary text-decoration-none"><i className="bi bi-arrow-left"></i> ログイン画面に戻る</Link>
                </div>
            </div>
        </div>
    );
};

export default ResetPassword;