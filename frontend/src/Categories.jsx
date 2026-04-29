import React, { useState, useEffect, useRef } from 'react';
import { Link } from 'react-router-dom';
import Sortable from 'sortablejs';
import * as api from './api';

const Categories = ({ currentUser }) => {
    const [categories, setCategories] = useState([]);
    const [newCategoryName, setNewCategoryName] = useState("");
    const listRef = useRef(null);

    const fetchCategories = async () => {
        try {
            const data = await api.getCategories();
            setCategories(data.categories);
        } catch (err) {
            console.error("取得エラー:", err);
        }
    };

    useEffect(() => {
        fetchCategories();
    }, []);

    useEffect(() => {
        if (currentUser?.is_admin && listRef.current && categories.length > 0) {
            const sortable = Sortable.create(listRef.current, {
                animation: 150,
                handle: '.list-group-item',
                ghostClass: 'sortable-ghost',
                onEnd: async () => {
                    const newOrder = Array.from(listRef.current.children).map(li => parseInt(li.dataset.id));
                    try {
                        await api.reorderCategories(newOrder);
                    } catch (err) {
                        console.error("順序更新エラー:", err);
                    }
                }
            });
            return () => sortable.destroy();
        }
    }, [currentUser, categories]);

    const handleAddCategory = async (e) => {
        e.preventDefault();
        try {
            const data = await api.addCategory(newCategoryName);
            if (data.status === 'success') {
                setNewCategoryName("");
                fetchCategories();
            } else {
                alert(data.message);
            }
        } catch (err) {
            console.error("追加エラー:", err);
            alert("カテゴリの追加に失敗しました");
        }
    };

    const handleDelete = async (id) => {
        if (window.confirm('削除しますか？')) {
            try {
                const data = await api.deleteCategory(id);
                if (data.status === 'success') {
                    fetchCategories();
                } else {
                    alert(data.message);
                }
            } catch (err) {
                console.error("削除エラー:", err);
                alert("削除に失敗しました");
            }
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