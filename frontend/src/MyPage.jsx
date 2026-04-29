import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import * as api from './api';

const MyPage = ({ currentUser, setCurrentUser }) => {
    const [currentItems, setCurrentItems] = useState([]);
    const [historyItems, setHistoryItems] = useState([]);
    const navigate = useNavigate();

    const fetchMyData = async () => {
        try {
            const data = await api.getMyPage();
            setCurrentItems(data.current_items);
            setHistoryItems(data.history_items);
        } catch (err) {
            console.error("データ取得エラー:", err);
        }
    };

    useEffect(() => {
        fetchMyData();
    }, []);

    const handleReturn = async (id) => {
        try {
            const data = await api.returnEquipment(id);
            if (data.status === 'success') {
                fetchMyData();
            } else {
                alert(data.message);
            }
        } catch (err) {
            console.error("返却エラー:", err);
            alert("通信エラーが発生しました");
        }
    };

    const handleDeleteAccount = async (e) => {
        e.preventDefault();
        if (window.confirm('【警告】\n本当にアカウントを削除しますか？\nこの操作は取り消せません。')) {
            try {
                const data = await api.deleteAccount();
                alert(data.message);
                if (data.status === 'success') {
                    setCurrentUser({ is_authenticated: false });
                    navigate('/');
                }
            } catch (err) {
                console.error("削除エラー:", err);
                alert("通信エラーが発生しました");
            }
        }
    };

    const handleLogout = async () => {
        try {
            const data = await api.logout();
            if (data.status === 'success') {
                setCurrentUser({ is_authenticated: false });
                navigate('/login');
            }
        } catch (err) {
            console.error("ログアウトエラー:", err);
        }
    };

    return (
        <div className="bg-light min-vh-100 pb-5">
            <nav className="navbar navbar-dark bg-dark mb-4">
                <div className="container">
                    <span className="navbar-brand mb-0 h1"><i className="bi bi-person-circle"></i> マイページ</span>
                    <Link to="/" className="btn btn-outline-light btn-sm">トップに戻る</Link>
                </div>
            </nav>
            <div className="container">
                <div className="row">
                    {/* 左側：プロフィール情報 */}
                    <div className="col-md-4 mb-4">
                        <div className="card shadow-sm text-center p-4">
                            <div className="mb-3"><i className="bi bi-person-circle" style={{fontSize: '3rem', color: '#555'}}></i></div>
                            <h4>{currentUser.username}</h4>
                            {currentUser.is_admin && <span className="badge bg-danger mb-2">管理者</span>}
                            <p className="text-muted">会員ID: {currentUser.id}</p>
                            <div className="d-grid gap-2">
                                <button onClick={handleLogout} className="btn btn-outline-danger">ログアウト</button>
                                <form onSubmit={handleDeleteAccount}>
                                    <button type="submit" className="btn btn-danger w-100">アカウント削除</button>
                                </form>
                            </div>
                        </div>
                    </div>

                    {/* 右側：借りている備品と履歴 */}
                    <div className="col-md-8">
                        {/* 現在借りている備品 */}
                        <div className="card shadow-sm mb-4">
                            <div className="card-header bg-primary text-white"><i className="bi bi-handbag"></i> 現在借りている備品</div>
                            <div className="card-body">
                                {currentItems.length > 0 ? (
                                    <ul className="list-group">
                                        {currentItems.map(item => (
                                            <li key={item.id} className="list-group-item d-flex justify-content-between align-items-center">
                                                <span><strong>{item.name}</strong><span className="badge bg-secondary ms-2">{item.category}</span></span>
                                                <button onClick={() => handleReturn(item.id)} className="btn btn-sm btn-outline-success">返却する</button>
                                            </li>
                                        ))}
                                    </ul>
                                ) : (
                                    <p className="text-muted mb-0">現在借りているものはありません。</p>
                                )}
                            </div>
                        </div>

                        {/* 過去の貸出履歴 */}
                        <div className="card shadow-sm">
                            <div className="card-header bg-secondary text-white"><i className="bi bi-clock-history"></i> 貸出履歴</div>
                            <div className="table-responsive">
                                <table className="table table-hover mb-0" style={{fontSize: '0.9rem'}}>
                                    <thead><tr><th>備品名</th><th>借りた日</th><th>返した日</th><th>状態</th></tr></thead>
                                    <tbody>
                                        {historyItems.length > 0 ? historyItems.map((log, idx) => (
                                            <tr key={idx}>
                                                <td>{log.equipment_name}</td>
                                                <td>{log.borrow_date}</td>
                                                <td>{log.return_date ? log.return_date : <span className="text-danger">未返却</span>}</td>
                                                <td>{log.return_date ? <span className="badge bg-light text-dark border">完了</span> : <span className="badge bg-danger">貸出中</span>}</td>
                                            </tr>
                                        )) : <tr><td colSpan="4" className="text-center text-muted py-3">履歴はまだありません。</td></tr>}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MyPage;