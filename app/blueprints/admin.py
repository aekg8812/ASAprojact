from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.db import get_db_connection
from app.utils import admin_required
import psycopg2

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/all_status', methods=['GET'])
@login_required
def all_status():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT id, username, is_admin FROM users ORDER BY id')
    users = [dict(row) for row in cur.fetchall()]
    
    cur.execute('''
        SELECT h.*, u.username 
        FROM history h 
        LEFT JOIN users u ON h.user_id = u.id 
        ORDER BY h.id DESC
    ''')
    all_history = [dict(row) for row in cur.fetchall()]
    cur.close()
    
    return jsonify({'users': users, 'all_history': all_history})

@admin_bp.route('/api/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        return jsonify({'status': 'error', 'message': '自分自身を削除することはできません。'}), 400

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT username FROM users WHERE id = %s', (user_id,))
        target_user = cur.fetchone()
        if not target_user:
            return jsonify({'status': 'error', 'message': 'ユーザーが見つかりません。'}), 404

        cur.execute('UPDATE equipment SET status = %s, borrower = %s WHERE borrower = %s', 
                    ('在庫あり', '', target_user['username']))
        cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
        return jsonify({'status': 'success', 'message': f'ユーザー「{target_user["username"]}」を削除しました。'})
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': f'削除エラー: {str(e)}'}), 500
    finally:
        cur.close()

# --- カテゴリ管理 ---

@admin_bp.route('/api/categories', methods=['GET'])
@login_required
def manage_categories():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM categories ORDER BY display_order')
    categories = [dict(row) for row in cur.fetchall()]
    cur.close()
    return jsonify({'categories': categories})

@admin_bp.route('/api/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    data = request.json
    name = data.get('name')
    if name:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT MAX(display_order) FROM categories')
        result = cur.fetchone()
        max_order = result['max'] if result['max'] is not None else 0
        new_order = max_order + 1
        try:
            cur.execute('INSERT INTO categories (name, display_order) VALUES (%s, %s)', (name, new_order))
            conn.commit()
            return jsonify({'status': 'success', 'message': 'カテゴリを追加しました。'})
        except psycopg2.IntegrityError:
            conn.rollback()
            return jsonify({'status': 'error', 'message': '追加エラー'}), 400
        finally:
            cur.close()
    return jsonify({'status': 'error', 'message': 'カテゴリ名が空です'}), 400

@admin_bp.route('/api/categories/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM categories WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    return jsonify({'status': 'success', 'message': 'カテゴリを削除しました。'})

@admin_bp.route('/api/categories/reorder', methods=['POST'])
@login_required
@admin_required
def reorder_categories():
    new_order = request.json.get('order')
    conn = get_db_connection()
    cur = conn.cursor()
    for index, category_id in enumerate(new_order):
        cur.execute('UPDATE categories SET display_order = %s WHERE id = %s', (index, category_id))
    conn.commit()
    cur.close()
    return jsonify({'status': 'success'})