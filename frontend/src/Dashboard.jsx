import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Dashboard = ({ currentUser, setCurrentUser }) => {
    const [categories, setCategories] = useState([]);
    const [items, setItems] = useState([]);
    
    // 🌟 検索と絞り込み用の状態（新しく追加！）
    const [searchQuery, setSearchQuery] = useState("");
    const [activeCategory, setActiveCategory] = useState("全て"); 
    
    const navigate = useNavigate();

    const fetchItems = () => {
        // 本番環境のURL（もしローカル環境でテストする場合は localhost:5000 に戻してください）
        fetch('https://asa-app-ayato.onrender.com/api/equipment', { credentials: 'include' })
            .then(res => res.json())
            .then(data => {
                setItems(data.items);
                setCategories(data.categories);
            })
            .catch(error => console.error("データ取得エラー:", error));
    };

    useEffect(() => {
        fetchItems();
    }, []);

    const handleLogout = () => {
        fetch('https://asa-app-ayato.onrender.com/logout', { method: 'POST', credentials: 'include' })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                setCurrentUser({ is_authenticated: false });
                navigate('/login');
            }
        });
    };

    const handleBorrow = (id) => {
        fetch(`https://asa-app-ayato.onrender.com/api/borrow/${id}`, { method: 'POST', credentials: 'include' })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') fetchItems();
            else alert(data.message);
        });
    };

    const handleReturn = (id) => {
        fetch(`https://asa-app-ayato.onrender.com/api/return/${id}`, { method: 'POST', credentials: 'include' })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') fetchItems();
            else alert(data.message);
        });
    };

    const handleDelete = (id) => {
        if(window.confirm('本当に削除しますか？')) {
            fetch(`https://asa-app-ayato.onrender.com/api/delete/${id}`, { method: 'POST', credentials: 'include' })
            .then(res => res.json())
            .then(data => {
                if (data.status === 'success') fetchItems();
                else alert(data.message);
            });
        }
    };

    const handleAddItem = (e) => {
        e.preventDefault();
        const formData = new FormData(e.target); 

        fetch('https://asa-app-ayato.onrender.com/api/add', {
            method: 'POST',
            credentials: 'include',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                e.target.reset();
                fetchItems();
            } else {
                alert(data.message);
            }
        })
        .catch(err => alert("追加エラーが発生しました"));
    };

    // 🌟 【爆速検索のコアロジック】
    // items（全データ）の中から、条件に合うものだけを filteredItems として抽出する
    const filteredItems = items.filter(item => {
        // 1. カテゴリが一致しているか（「全て」なら無条件でOK）
        const matchCategory = activeCategory === "全て" || item.category === activeCategory;
        // 2. 検索文字が含まれているか（大文字・小文字を区別しない）
        const matchSearch = item.name.toLowerCase().includes(searchQuery.toLowerCase());
        
        return matchCategory && matchSearch; // 両方の条件を満たすものだけ残す！
    });

    return (
        <div className="bg-light min-vh-100 pb-5">
            <style>{`.thumbnail { width: 60px; height: 60px; object-fit: cover; border-radius: 4px; }`}</style>

            <nav className="navbar navbar-dark bg-dark mb-4">
                <div className="container">
                    <span className="navbar-brand mb-0 h1"><i className="bi bi-tree-fill"></i> CampKit 備品管理</span>
                    <div className="d-flex align-items-center gap-2">
                        {currentUser.is_authenticated ? (
                            <>
                                <span className="text-white me-2 d-none d-md-inline">ようこそ、{currentUser.username} さん</span>
                                <Link to="/all_status" className="btn btn-info btn-sm text-white"><i className="bi bi-bar-chart-fill"></i> 全体</Link>
                                <Link to="/mypage" className="btn btn-primary btn-sm"><i className="bi bi-person-circle"></i> マイページ</Link>
                                <Link to="/categories" className="btn btn-outline-light btn-sm"><i className="bi bi-gear-fill"></i> カテゴリ</Link>
                                <button onClick={handleLogout} className="btn btn-danger btn-sm">ログアウト</button>
                            </>
                        ) : (
                            <>
                                <Link to="/login" className="btn btn-success btn-sm">ログイン</Link>
                                <Link to="/register" className="btn btn-outline-light btn-sm">新規登録</Link>
                            </>
                        )}
                    </div>
                </div>
            </nav>

            <div className="container">
                {/* 検索バー */}
                <div className="row mb-3">
                    <div className="col-md-6">
                        <form className="d-flex gap-2" onSubmit={(e) => e.preventDefault()}>
                            <input 
                                type="text" 
                                className="form-control" 
                                placeholder="備品名で検索..." 
                                value={searchQuery} 
                                onChange={(e) => setSearchQuery(e.target.value)} // 文字を打つたびに一瞬で絞り込まれる！
                            />
                            {/* 「検索」ボタンを押さなくても絞り込まれますが、UXのために残しています */}
                            <button type="button" className="btn btn-primary"><i className="bi bi-search"></i> 検索</button>
                            <button type="button" className="btn btn-outline-secondary" onClick={() => setSearchQuery("")}>クリア</button>
                        </form>
                    </div>
                </div>

                {/* カテゴリ絞り込みボタン */}
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

                {currentUser.is_authenticated && currentUser.is_admin && (
                    <div className="card shadow-sm mb-4 border-danger">
                        <div className="card-header bg-danger text-white"><i className="bi bi-box-seam"></i> 新しい備品を登録（管理者のみ）</div>
                        <div className="card-body">
                            <form className="row g-3" onSubmit={handleAddItem}>
                                <div className="col-md-2"><label className="form-label">ID</label><input type="number" name="id" className="form-control" placeholder="No." required /></div>
                                <div className="col-md-4"><label className="form-label">備品名</label><input type="text" name="name" className="form-control" placeholder="例：コールマン テント" required /></div>
                                <div className="col-md-3"><label className="form-label">カテゴリ</label>
                                    <select name="category" className="form-select">
                                        {categories.map((cat, idx) => <option key={idx} value={cat.name}>{cat.name}</option>)}
                                    </select>
                                </div>
                                <div className="col-md-3"><label className="form-label">写真</label><input type="file" name="image" className="form-control" accept="image/*" /></div>
                                <div className="col-12"><button type="submit" className="btn btn-success w-100"><i className="bi bi-plus-lg"></i> 登録</button></div>
                            </form>
                        </div>
                    </div>
                )}

                <div className="card shadow-sm">
                    <div className="card-header bg-white"><i className="bi bi-list-ul"></i> 備品リスト</div>
                    <div className="table-responsive">
                        <table className="table table-hover align-middle mb-0">
                            <thead className="table-light">
                                <tr>
                                    <th>ID</th><th>写真</th><th>カテゴリ</th><th>備品名</th><th>状態</th><th>現在の持ち主</th><th>アクション</th>
                                    {currentUser.is_admin && <th>管理</th>}
                                </tr>
                            </thead>
                            <tbody>
                                {/* 🌟 items ではなく、絞り込み済みの filteredItems を表示する！ */}
                                {filteredItems.length > 0 ? (
                                    filteredItems.map(item => (
                                        <tr key={item.id}>
                                            <td>{item.id}</td>
                                            <td>{item.image_filename ? <img src={item.image_filename} className="thumbnail" alt="備品" /> : <span className="text-muted" style={{fontSize: '0.8rem'}}>No Image</span>}</td>
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
                                                    <span className="text-muted" style={{fontSize: '0.8rem'}}>要ログイン</span>
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
                                    <tr><td colSpan="8" className="text-center py-4">該当する備品が見つかりません...</td></tr>
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