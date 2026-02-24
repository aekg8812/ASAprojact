import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Register = () => {
    const [formData, setFormData] = useState({ username: '', password: '', confirm_password: '' });
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        setError(null);

        fetch('https://asa-app-ayato.onrender.com/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                navigate('/login');
            } else {
                setError(data.message);
            }
        })
        .catch(err => setError('通信エラーが発生しました'));
    };

    return (
        <div className="bg-light d-flex align-items-center justify-content-center" style={{ minHeight: '100vh' }}>
            <div className="card shadow p-4" style={{ width: '450px' }}>
                {/* 👇 ここが「CampKit 新規登録」に変わりました！ */}
                <h3 className="text-center mb-4">CampKit 新規登録</h3>
                {error && <div className="alert alert-danger">{error}</div>}
                
                <form onSubmit={handleSubmit}>
                    <div className="mb-3">
                        <label className="form-label">ユーザー名</label>
                        <input type="text" className="form-control" required value={formData.username} onChange={(e) => setFormData({...formData, username: e.target.value})} />
                    </div>
                    <div className="row">
                        <div className="col-md-6 mb-3">
                            <label className="form-label">パスワード</label>
                            <input type="password" className="form-control" required value={formData.password} onChange={(e) => setFormData({...formData, password: e.target.value})} />
                        </div>
                        <div className="col-md-6 mb-3">
                            <label className="form-label">確認用</label>
                            <input type="password" className="form-control" placeholder="もう一度" required value={formData.confirm_password} onChange={(e) => setFormData({...formData, confirm_password: e.target.value})} />
                        </div>
                    </div>
                    <button type="submit" className="btn btn-primary w-100">登録する</button>
                </form>
                <div className="mt-3 text-center">
                    <Link to="/login">既にアカウントをお持ちの方はこちら</Link>
                </div>
            </div>
        </div>
    );
};

export default Register;