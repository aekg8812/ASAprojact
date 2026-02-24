import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import Sortable from 'sortablejs';

const Categories = ({ currentUser }) => {
    const [categories, setCategories] = useState([]);
    const [newCategoryName, setNewCategoryName] = useState("");
    const listRef = useRef(null);

    const fetchCategories = () => {
        fetch('http://localhost:5000/api/categories', { credentials: 'include' })
            .then(res => res.json())
            .then(data => setCategories(data.categories))
            .catch(err => console.error("取得エラー:", err));
    };

    useEffect(() => {
        fetchCategories();
    }, []);

    // 🌟 ドラッグ＆ドロップの並び替え処理（本物）
    useEffect(() => {
        if (currentUser?.is_admin && listRef.current && categories.length > 0) {
            const sortable = Sortable.create(listRef.current, {
                animation: 150,
                handle: '.list-group-item',
                ghostClass: 'sortable-ghost',
                onEnd: () => {
                    const newOrder = Array.from(listRef.current.children).map(li => parseInt(li.dataset.id));
                    fetch('http://localhost:5000/api/categories/reorder', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        credentials: 'include',
                        body: JSON.stringify({ order: newOrder })
                    });
                }
            });
            return () => sortable.destroy();
        }
    }, [currentUser, categories]);

    const handleAddCategory = (e) => {
        e.preventDefault();
        fetch('http://localhost:5000/api/categories/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ name: newCategoryName })
        })
        .then(res => res.json())
        .then(data => {
            if(data.status === 'success') {
                setNewCategoryName("");
                fetchCategories();
            } else {
                alert(data.message);
            }
        });
    };

    const handleDelete = (id) => {
        if (window.confirm('削除しますか？')) {
            fetch(`http://localhost:5000/api/categories/delete/${id}`, { method: 'POST', credentials: 'include' })
            .then(() => fetchCategories());
        }
    };

    return (
        <div className="bg-light min-vh-100 pt-5 pb-5">
            <style>{`
                .draggable-item { cursor: grab; }
                .draggable-item:active { cursor: grabbing; }
                .sortable-ghost { opacity: 0.4; background-color: #f0f0f0; }
            `}</style>

            <div className="container" style={{ maxWidth: '600px' }}>
                <div className="card shadow">
                    <div className="card-header bg-secondary text-white d-flex justify-content-between align-items-center">
                        <span><i className="bi bi-tags-fill"></i> カテゴリ管理</span>
                        <Link to="/" className="btn btn-sm btn-light">トップに戻る</Link>
                    </div>
                    <div className="card-body">
                        {currentUser?.is_admin ? (
                            <>
                                <form onSubmit={handleAddCategory} className="input-group mb-4">
                                    <input type="text" className="form-control" placeholder="新しいカテゴリ名" required value={newCategoryName} onChange={(e) => setNewCategoryName(e.target.value)} />
                                    <button type="submit" className="btn btn-success"><i className="bi bi-plus-lg"></i> 追加</button>
                                </form>
                            </>
                        ) : (
                            <div className="alert alert-warning py-2">閲覧モードです。追加・削除は管理者のみ可能です。</div>
                        )}

                        <ul className="list-group" ref={listRef}>
                            {categories.map(category => (
                                <li key={category.id} data-id={category.id} className={`list-group-item d-flex justify-content-between align-items-center ${currentUser?.is_admin ? 'draggable-item' : ''}`}>
                                    <div>
                                        {currentUser?.is_admin ? <i className="bi bi-grip-vertical text-muted me-2"></i> : <i className="bi bi-tag-fill text-muted me-2"></i>}
                                        {category.name}
                                    </div>
                                    {currentUser?.is_admin && (
                                        <button onClick={() => handleDelete(category.id)} className="btn btn-sm btn-outline-danger border-0"><i className="bi bi-trash"></i></button>
                                    )}
                                </li>
                            ))}
                        </ul>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Categories;