import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Login = ({ setCurrentUser }) => {
    const [formData, setFormData] = useState({ username: '', password: '' });
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        setError(null);

        fetch('http://localhost:5000/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                setCurrentUser({
                    is_authenticated: true,
                    id: data.user.id,
                    username: data.user.username,
                    is_admin: data.user.is_admin
                });
                navigate('/');
            } else {
                setError(data.message || 'ログインに失敗しました');
            }
        })
        .catch(err => {
            console.error(err);
            setError('サーバーとの通信に失敗しました。');
        });
    };

    return (
        <div className="bg-light d-flex align-items-center justify-content-center" style={{ height: '100vh' }}>
            <div className="card shadow p-4" style={{ width: '400px' }}>
                {/* 👇 ここが「CampKit ログイン」に変わりました！ */}
                <h3 className="text-center mb-4">CampKit ログイン</h3>

                {error && <div className="alert alert-danger">{error}</div>}

                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label className="form-label">ユーザー名</label>
                        <input 
                            type="text" 
                            className="form-control" 
                            required 
                            value={formData.username}
                            onChange={(e) => setFormData({...formData, username: e.target.value})}
                        />
                    </div>
                    <div className="mb-3">
                        <label className="form-label">パスワード</label>
                        <input 
                            type="password" 
                            className="form-control" 
                            required 
                            value={formData.password}
                            onChange={(e) => setFormData({...formData, password: e.target.value})}
                        />
                    </div>
                    <button type="submit" className="btn btn-success w-100">ログイン</button>
                </form>

                <div className="mt-4 text-center">
                    <p className="mb-2"><Link to="/reset_password" className="link-secondary">パスワードを忘れた方はこちら</Link></p>
                    <hr />
                    <p className="mb-0"><Link to="/register" className="btn btn-outline-primary btn-sm">新規会員登録</Link></p>
                </div>
            </div>
        </div>
    );
};

export default Login;