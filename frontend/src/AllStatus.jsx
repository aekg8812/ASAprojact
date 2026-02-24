import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const AllStatus = ({ currentUser }) => {
    const [users, setUsers] = useState([]);
    const [allHistory, setAllHistory] = useState([]);

    const fetchAllData = () => {
        fetch('https://asa-app-ayato.onrender.com/api/all_status', { credentials: 'include' })
            .then(res => res.json())
            .then(data => {
                setUsers(data.users);
                setAllHistory(data.all_history);
            })
            .catch(err => console.error("データ取得エラー:", err));
    };

    useEffect(() => {
        fetchAllData();
    }, []);

    const handleDeleteUser = (userId) => {
        if (window.confirm('【管理者権限】\n本当にこのユーザーを削除しますか？\n（貸出中の備品は強制返却されます）')) {
            fetch(`https://asa-app-ayato.onrender.com/api/delete_user/${userId}`, { method: 'POST', credentials: 'include' })
            .then(res => res.json())
            .then(data => {
                alert(data.message);
                if (data.status === 'success') fetchAllData();
            });
        }
    };

    return (
        <div className="bg-light min-vh-100 pb-5">
            <nav className="navbar navbar-dark bg-dark mb-4">
                <div className="container">
                    <span className="navbar-brand mb-0 h1"><i className="bi bi-bar-chart-fill"></i> 全体状況</span>
                    <Link to="/" className="btn btn-outline-light btn-sm">トップに戻る</Link>
                </div>
            </nav>

            <div className="container">
                <div className="row">
                    <div className="col-md-4 mb-4">
                        <div className="card shadow-sm">
                            <div className="card-header bg-info text-white"><i className="bi bi-people-fill"></i> 会員リスト</div>
                            <ul className="list-group list-group-flush">
                                {users.map(user => (
                                    <li key={user.id} className="list-group-item d-flex justify-content-between align-items-center">
                                        <div>
                                            <i className="bi bi-person"></i> {user.username}
                                            {user.is_admin && <span className="badge bg-danger ms-1" style={{ fontSize: '0.7em' }}>Admin</span>}
                                        </div>
                                        <div className="d-flex align-items-center gap-2">
                                            <span className="badge bg-light text-dark border">ID: {user.id}</span>
                                            {currentUser?.is_admin && currentUser.id !== user.id && (
                                                <button onClick={() => handleDeleteUser(user.id)} className="btn btn-sm btn-outline-danger border-0"><i className="bi bi-x-circle-fill"></i></button>
                                            )}
                                        </div>
                                    </li>
                                ))}
                            </ul>
                        </div>
                    </div>

                    <div className="col-md-8">
                        <div className="card shadow-sm">
                            <div className="card-header bg-secondary text-white"><i className="bi bi-clock-history"></i> 全体の貸出・返却履歴</div>
                            <div className="table-responsive">
                                <table className="table table-hover mb-0" style={{ fontSize: '0.9rem' }}>
                                    <thead className="table-light">
                                        <tr><th>借りた人</th><th>備品名</th><th>貸出日</th><th>返却日</th><th>状態</th></tr>
                                    </thead>
                                    <tbody>
                                        {allHistory.map((log, index) => (
                                            <tr key={index}>
                                                <td>{log.username ? <strong>{log.username}</strong> : <span className="text-muted fst-italic">退会済み</span>}</td>
                                                <td>{log.equipment_name}</td>
                                                <td>{log.borrow_date}</td>
                                                <td>{log.return_date ? log.return_date : <span className="text-danger">未返却</span>}</td>
                                                <td>{log.return_date ? <span className="badge bg-light text-dark border">完了</span> : <span className="badge bg-danger">貸出中</span>}</td>
                                            </tr>
                                        ))}
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

export default AllStatus;