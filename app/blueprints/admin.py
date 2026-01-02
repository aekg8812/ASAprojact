from flask import Blueprint, render_template, request, redirect, jsonify, flash, url_for
from flask_login import login_required, current_user
from app.db import get_db_connection
from app.utils import admin_required
import psycopg2

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/all_status')
@login_required
def all_status():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users ORDER BY id')
    users = cur.fetchall()
    cur.execute('''
        SELECT h.*, u.username 
        FROM history h 
        LEFT JOIN users u ON h.user_id = u.id 
        ORDER BY h.id DESC
    ''')
    all_history = cur.fetchall()
    cur.close()
    return render_template('admin/all_status.html', users=users, all_history=all_history)

@admin_bp.route('/delete_user/<int:user_id>', methods=['POST'])
@login_required
@admin_required
def delete_user(user_id):
    if user_id == current_user.id:
        flash('自分自身をこの画面から削除することはできません。（マイページから退会してください）', 'warning')
        return redirect(url_for('admin.all_status'))

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('SELECT username FROM users WHERE id = %s', (user_id,))
        target_user = cur.fetchone()
        if not target_user:
            flash('ユーザーが見つかりません。', 'danger')
            return redirect(url_for('admin.all_status'))

        cur.execute('UPDATE equipment SET status = %s, borrower = %s WHERE borrower = %s', 
                    ('在庫あり', '', target_user['username']))
        cur.execute('DELETE FROM users WHERE id = %s', (user_id,))
        conn.commit()
        flash(f'ユーザー「{target_user["username"]}」を削除しました。', 'success')
    except Exception as e:
        conn.rollback()
        flash(f'削除エラー: {e}', 'danger')
    finally:
        cur.close()
    return redirect(url_for('admin.all_status'))

# --- カテゴリ管理 ---

@admin_bp.route('/categories')
@login_required
def manage_categories():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM categories ORDER BY display_order')
    categories = cur.fetchall()
    cur.close()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/add', methods=['POST'])
@login_required
@admin_required
def add_category():
    name = request.form['name']
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
        except psycopg2.IntegrityError:
            conn.rollback()
        cur.close()
    return redirect(url_for('admin.manage_categories'))

@admin_bp.route('/categories/delete/<int:id>')
@login_required
@admin_required
def delete_category(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM categories WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    return redirect(url_for('admin.manage_categories'))

@admin_bp.route('/categories/reorder', methods=['POST'])
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