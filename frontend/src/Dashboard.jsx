import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from './api'; // ✅ 共通APIユーティリティをインポート

const Dashboard = ({ currentUser, setCurrentUser }) => {
    const [categories, setCategories] = useState([]);
    const [items, setItems] = useState([]);
    const [searchQuery, setSearchQuery] = useState("");
    const [activeCategory, setActiveCategory] = useState("全て"); 
    const navigate = useNavigate();

    // --- データ取得関数 ---
    const fetchItems = async () => {
        try {
            // api.js の getEquipment を使用（内部で /api/equipment を叩く）
            const data = await api.getEquipment();
            setItems(data.items || []);
            setCategories(data.categories || []);
        } catch (error) {
            console.error("データ取得エラー:", error);
        }
    };

    useEffect(() => {
        fetchItems();
    }, []);

    // --- ログアウト処理 ---
    const handleLogout = async () => {
        try {
            const data = await api.logout();
            if (data.status === 'success') {
                setCurrentUser({ is_authenticated: false });
                navigate('/login');
            }
        } catch (error) {
            console.error("ログアウト失敗:", error);
        }
    };

    // --- 備品を借りる ---
    const handleBorrow = async (id) => {
        try {
            const data = await api.borrowEquipment(id);
            if (data.status === 'success') {
                fetchItems();
            } else {
                alert(data.message);
            }
        } catch (error) {
            alert("通信エラーが発生しました");
        }
    };

    // --- 備品を返却する ---
    const handleReturn = async (id) => {
        try {
            const data = await api.returnEquipment(id);
            if (data.status === 'success') {
                fetchItems();
            } else {
                alert(data.message);
            }
        } catch (error) {
            alert("通信エラーが発生しました");
        }
    };

    // --- 備品を削除（管理者） ---
    const handleDelete = async (id) => {
        if (window.confirm('本当に削除しますか？')) {
            try {
                // api.js に定義がない汎用リクエストも apiCallJson で可能
                const data = await api.apiCallJson(`/api/delete/${id}`, { method: 'POST' });
                if (data.status === 'success') {
                    fetchItems();
                } else {
                    alert(data.message);
                }
            } catch (error) {
                alert("削除中にエラーが発生しました");
            }
        }
    };

    // --- 備品を追加（管理者） ---
    const handleAddItem = async (e) => {
        e.preventDefault();
        const formData = new FormData(e.target); 

        try {
            // 画像(File)を含む場合は apiCall を使用
            const res = await api.apiCall('/api/add', {
                method: 'POST',
                body: formData,
                headers: {} // FormData送信時はブラウザに任せるため空にする
            });
            const data = await res.json();

            if (data.status === 'success') {
                alert(data.message);
                e.target.reset();
                fetchItems();
            } else {
                alert(data.message);
            }
        } catch (err) {
            alert("追加エラーが発生しました");
        }
    };

    // --- 検索・絞り込みロジック ---
    const filteredItems = items.filter(item => {
        const matchCategory = activeCategory === "全て" || item.category === activeCategory;
        const matchSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
        return matchCategory && matchSearch;
    });

    return (
        <div className="bg-light min-vh-100 pb-5">
            <style>{`.thumbnail { width: 60px; height: 60px; object-fit: cover; border-radius: 4px; }`}</style>

            {/* ナビゲーションバー */}
            <nav className="navbar navbar-dark bg-dark mb-4">
                <div className="container">
                    <span className="navbar-brand mb-0 h1"><i className="bi bi-tree-fill"></i> CampKit 備品管理</span>
                    <div className="d-flex align-items-center gap-2">
                        {currentUser.is_authenticated ? (
                            <>
                                {currentUser.picture_url && (
                                    <img 
                                        src={currentUser.picture_url} 
                                        alt="profile" 
                                        style={{ width: '30px', height: '30px', borderRadius: '50%' }} 
                                    />
                                )}
                                <span className="text-white me-2 d-none d-md-inline">ようこそ、{currentUser.username} さん</span>
                                <Link to="/all_status" className="btn btn-info btn-sm text-white"><i className="bi bi-bar-chart-fill"></i> 全体</Link>
                                <Link to="/mypage" className="btn btn-primary btn-sm"><i className="bi bi-person-circle"></i> マイページ</Link>
                                <Link to="/categories" className="btn btn-outline-light btn-sm"><i className="bi bi-gear-fill"></i> カテゴリ</Link>
                                <button onClick={handleLogout} className="btn btn-danger btn-sm">ログアウト</button>
                            </>
                        ) : (
                            <>
                                <Link to="/login" className="btn btn-success btn-sm">ログイン</Link>
                            </>
                        )}
                    </div>
                </div>
            </nav>

            <div className="container">
                {/* 検索・クリア */}
                <div className="row mb-3">
                    <div className="col-md-6">
                        <div className="d-flex gap-2">
                            <input 
                                type="text" 
                                className="form-control" 
                                placeholder="備品名で検索..." 
                                value={searchQuery} 
                                onChange={(e) => setSearchQuery(e.target.value)} 
                            />
                            <button type="button" className="btn btn-outline-secondary" onClick={() => setSearchQuery("")}>クリア</button>
                        </div>
                    </div>
                </div>

                {/* カテゴリ切り替え */}
                <div className="mb-4">
                    <div className="btn-group flex-wrap">
                        <button 
                            onClick={() => setActiveCategory("全て")} 
                            className={`btn ${activeCategory === "全て" ? "btn-dark" : "btn-outline-dark"}`}>
                            全て
                        </button>
                        {categories.map((cat, idx) => (
                            <button 
                                key={idx} 
                                onClick={() => setActiveCategory(cat.name)} 
                                className={`btn ${activeCategory === cat.name ? "btn-dark" : "btn-outline-dark"}`}>
                                {cat.name}
                            </button>
                        ))}
                    </div>
                </div>

                {/* 管理者用：備品追加フォーム */}
                {currentUser.is_authenticated && currentUser.is_admin && (
                    <div className="card shadow-sm mb-4 border-danger">
                        <div className="card-header bg-danger text-white"><i className="bi bi-box-seam"></i> 新しい備品を登録（管理者）</div>
                        <div className="card-body">
                            <form className="row g-3" onSubmit={handleAddItem}>
                                <div className="col-md-2"><label className="form-label">ID</label><input type="number" name="id" className="form-control" required /></div>
                                <div className="col-md-4"><label className="form-label">備品名</label><input type="text" name="name" className="form-control" required /></div>
                                <div className="col-md-3"><label className="form-label">カテゴリ</label>
                                    <select name="category" className="form-select">
                                        {categories.map((cat, idx) => <option key={idx} value={cat.name}>{cat.name}</option>)}
                                    </select>
                                </div>
                                <div className="col-md-3"><label className="form-label">写真</label><input type="file" name="image" className="form-control" accept="image/*" /></div>
                                <div className="col-12"><button type="submit" className="btn btn-success w-100">登録</button></div>
                            </form>
                        </div>
                    </div>
                )}

                {/* 備品一覧テーブル */}
                <div className="card shadow-sm">
                    <div className="card-header bg-white">備品リスト</div>
                    <div className="table-responsive">
                        <table className="table table-hover align-middle mb-0">
                            <thead className="table-light">
                                <tr>
                                    <th>ID</th><th>写真</th><th>カテゴリ</th><th>備品名</th><th>状態</th><th>現在の持ち主</th><th>アクション</th>
                                    {currentUser.is_admin && <th>管理</th>}
                                </tr>
                            </thead>
                            <tbody>
                                {filteredItems.length > 0 ? (
                                    filteredItems.map(item => (
                                        <tr key={item.id}>
                                            <td>{item.id}</td>
                                            <td>{item.image_filename ? <img src={item.image_filename} className="thumbnail" alt="item" /> : '-'}</td>
                                            <td><span className="badge bg-secondary">{item.category}</span></td>
                                            <td className="fw-bold">{item.name}</td>
                                            <td>{item.status === '貸出中' ? <span className="badge bg-danger">貸出中</span> : <span className="badge bg-success">在庫あり</span>}</td>
                                            <td>{item.borrower || '-'}</td>
                                            <td>
                                                {currentUser.is_authenticated ? (
                                                    item.status === '在庫あり' ? (
                                                        <button onClick={() => handleBorrow(item.id)} className="btn btn-sm btn-primary">借りる</button>
                                                    ) : item.borrower === currentUser.username ? (
                                                        <button onClick={() => handleReturn(item.id)} className="btn btn-sm btn-outline-success">返却</button>
                                                    ) : (
                                                        <button className="btn btn-sm btn-secondary" disabled>貸出中</button>
                                                    )
                                                ) : (
                                                    <span className="text-muted small">要ログイン</span>
                                                )}
                                            </td>
                                            {currentUser.is_admin && (
                                                <td>
                                                    <Link to={`/edit/${item.id}`} className="btn btn-sm btn-outline-warning me-1"><i className="bi bi-pencil"></i></Link>
                                                    <button onClick={() => handleDelete(item.id)} className="btn btn-sm btn-outline-secondary"><i className="bi bi-trash"></i></button>
                                                </td>
                                            )}
                                        </tr>
                                    ))
                                ) : (
                                    <tr><td colSpan="8" className="text-center py-4">該当する備品が見つかりません</td></tr>
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;