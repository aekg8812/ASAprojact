import React, { useState, useEffect } from 'react';
import { Link, useNavigate, useParams } from 'react-router-dom';

const EditEquipment = ({ currentUser }) => {
    const { id } = useParams(); // URLから備品IDを取得
    const navigate = useNavigate();
    const [categories, setCategories] = useState([]);
    const [item, setItem] = useState({ id: '', name: '', category: '', image_filename: null });
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // 現在の備品データを取得
        fetch(`https://asa-app-ayato.onrender.com/api/edit/${id}`, { credentials: 'include' })
            .then(res => res.json())
            .then(data => {
                if (data.item) {
                    setItem(data.item);
                    setCategories(data.categories);
                } else {
                    alert('データが見つかりません');
                    navigate('/');
                }
                setLoading(false);
            })
            .catch(err => console.error(err));
    }, [id, navigate]);

    const handleSubmit = (e) => {
        e.preventDefault();
        const formData = new FormData(e.target);

        fetch(`https://asa-app-ayato.onrender.com/api/edit/${id}`, {
            method: 'POST',
            credentials: 'include',
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                alert(data.message);
                navigate('/');
            } else {
                alert(data.message);
            }
        });
    };

    if (loading) return <div className="text-center mt-5">読み込み中...</div>;

    return (
        <div className="bg-light min-vh-100 pt-5 pb-5">
            <div className="container" style={{ maxWidth: '600px' }}>
                <div className="card shadow">
                    <div className="card-header bg-warning text-dark"><i className="bi bi-pencil-square"></i> 備品情報を編集</div>
                    <div className="card-body">
                        <form onSubmit={handleSubmit}>
                            <div className="mb-3">
                                <label className="form-label">ID</label>
                                <input type="number" name="id" className="form-control" value={item.id} onChange={(e) => setItem({...item, id: e.target.value})} required />
                            </div>
                            <div className="mb-3">
                                <label className="form-label">備品名</label>
                                <input type="text" name="name" className="form-control" value={item.name} onChange={(e) => setItem({...item, name: e.target.value})} required />
                            </div>
                            <div className="mb-3">
                                <label className="form-label">カテゴリ</label>
                                <select name="category" className="form-select" value={item.category} onChange={(e) => setItem({...item, category: e.target.value})}>
                                    {categories.map((cat, idx) => <option key={idx} value={cat.name}>{cat.name}</option>)}
                                </select>
                            </div>
                            <div className="mb-4">
                                <label className="form-label">写真の変更</label>
                                {item.image_filename && (
                                    <div className="mb-2">
                                        <img src={item.image_filename} alt="現在の写真" style={{ maxHeight: '150px', borderRadius: '8px', border: '1px solid #ddd' }} />
                                    </div>
                                )}
                                <input type="file" name="image" className="form-control" accept="image/*" />
                            </div>
                            <div className="d-flex gap-2">
                                <button type="submit" className="btn btn-warning w-100">更新する</button>
                                <Link to="/" className="btn btn-secondary w-100">キャンセル</Link>
                            </div>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default EditEquipment;