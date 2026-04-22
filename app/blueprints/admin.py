from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.db import (
    get_db_connection, get_all_users, get_all_categories, 
    get_all_history, get_user_borrowed_equipment
)
from app.utils import admin_required
from app.constants import (
    EQUIPMENT_STATUS_AVAILABLE,
    ERROR_MESSAGES, SUCCESS_MESSAGES,
    HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_CONFLICT, HTTP_SERVER_ERROR
)
import psycopg2

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/api/all_status', methods=['GET'])
@login_required
@admin_required
def all_status():
    """全ユーザーと全履歴を取得（管理者のみ）"""
    users = get_all_users()
    all_history = get_all_history()
    
    return jsonify({'users': users, 'all_history': all_history}), HTTP_OK

@admin_bp.route('/api/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    """ユーザーを削除（管理者のみ）"""
    if user_id == current_user.id:
        return jsonify({'status': 'error', 'message': ERROR_MESSAGES['cannot_delete_self']}), HTTP_BAD_REQUEST

    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB接続エラー'}), HTTP_SERVER_ERROR
    
    cur = conn.cursor()
    try:
        cur.execute('SELECT username FROM users WHERE id = %s', (user_id,))
        target_user = cur.fetchone()
        if not target_user:
            return jsonify({'status': 'error', 'message': ERROR_MESSAGES['user_not_found']}), HTTP_NOT_FOUND

        # ユーザーの借用中の備品を全て返却状態に
        cur.execute(
            'UPDATE equipment SET status = %s, borrower = %s WHERE borrower = %s', 
            (EQUIPMENT_STATUS_AVAILABLE, '', target_user['username'])
        )
        cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
        return jsonify({
            'status': 'success', 
            'message': SUCCESS_MESSAGES['user_deleted'].format(username=target_user['username'])
        }), HTTP_OK
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': f'削除エラー: {str(e)}'}), HTTP_SERVER_ERROR
    finally:
        cur.close()

# ========== カテゴリ管理 ==========

@admin_bp.route('/api/categories', methods=['GET'])
@login_required
def manage_categories():
    """カテゴリ一覧を取得"""
    categories = get_all_categories()
    return jsonify({'categories': categories}), HTTP_OK

@admin_bp.route('/api/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    """カテゴリを追加（管理者のみ）"""
    data = request.json
    name = data.get('name')
    if not name:
        return jsonify({'status': 'error', 'message': 'カテゴリ名が空です'}), HTTP_BAD_REQUEST
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB接続エラー'}), HTTP_SERVER_ERROR
    
    cur = conn.cursor()
    try:
        cur.execute('SELECT MAX(display_order) FROM categories')
        result = cur.fetchone()
        max_order = result['max'] if result['max'] is not None else 0
        new_order = max_order + 1
        
        cur.execute(
            'INSERT INTO categories (name, display_order) VALUES (%s, %s)', 
            (name, new_order)
        )
        conn.commit()
        return jsonify({'status': 'success', 'message': SUCCESS_MESSAGES['category_added']}), HTTP_OK
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'status': 'error', 'message': 'カテゴリ名が重複しています'}), HTTP_CONFLICT
    finally:
        cur.close()

@admin_bp.route('/api/categories/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_category(id):
    """カテゴリを削除（管理者のみ）"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB接続エラー'}), HTTP_SERVER_ERROR
    
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM categories WHERE id = %s', (id,))
        conn.commit()
        return jsonify({'status': 'success', 'message': SUCCESS_MESSAGES['category_deleted']}), HTTP_OK
    finally:
        cur.close()

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