from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db_connection
from app.models import User
import psycopg2

auth_bp = Blueprint('auth', __name__)

# 👇 Reactが「今誰がログインしてる？」を確認するための新しいAPI
@auth_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    if current_user.is_authenticated:
        return jsonify({
            'is_authenticated': True,
            'id': current_user.id,
            'username': current_user.username,
            'is_admin': current_user.is_admin
        })
    return jsonify({'is_authenticated': False}), 401

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if password != confirm_password:
        return jsonify({'status': 'error', 'message': 'パスワード（確認用）が一致しません。'}), 400
    
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        hashed_password = generate_password_hash(password)
        cur.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)', (username, hashed_password, False))
        conn.commit()
        return jsonify({'status': 'success', 'message': '登録完了！ログインしてください。'})
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'status': 'error', 'message': 'そのユーザー名は既に使用されています。'}), 400
    finally:
        cur.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE username = %s', (username,))
    user_data = cur.fetchone()
    cur.close()
    
    if user_data and check_password_hash(user_data['password_hash'], password):
        is_admin = user_data.get('is_admin', False)
        user = User(user_data['id'], user_data['username'], user_data['password_hash'], is_admin)
        login_user(user)
        return jsonify({
            'status': 'success', 
            'message': 'ログインしました！',
            'user': {'id': user.id, 'username': user.username, 'is_admin': user.is_admin}
        })
    else:
        return jsonify({'status': 'error', 'message': 'ユーザー名またはパスワードが違います'}), 401

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'status': 'success', 'message': 'ログアウトしました。'})

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    data = request.json
    step = data.get('step')

    conn = get_db_connection()
    cur = conn.cursor()

    if step == 'check_user':
        username = data.get('username')
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        if user:
            return jsonify({'status': 'success', 'user_id': user['id'], 'username': username})
        else:
            return jsonify({'status': 'error', 'message': 'そのユーザー名は登録されていません。'}), 404
            
    elif step == 'reset_pass':
        user_id = data.get('user_id')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if new_password != confirm_password:
            cur.close()
            return jsonify({'status': 'error', 'message': '新しいパスワードが一致しません。'}), 400
            
        new_hash = generate_password_hash(new_password)
        cur.execute('UPDATE users SET password_hash = %s WHERE id = %s', (new_hash, user_id))
        conn.commit()
        cur.close()
        return jsonify({'status': 'success', 'message': 'パスワードを再設定しました。ログインしてください。'})

@auth_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT count(*) FROM equipment WHERE borrower = %s', (current_user.username,))
    borrowing_count = cur.fetchone()['count']
    
    if borrowing_count > 0:
        cur.close()
        return jsonify({'status': 'error', 'message': f'未返却の備品が {borrowing_count} 個あります。全て返却してから退会してください。'}), 400
        
    try:
        cur.execute('DELETE FROM users WHERE id = %s', (current_user.id,))
        conn.commit()
        logout_user()
        return jsonify({'status': 'success', 'message': 'アカウントを削除しました。ご利用ありがとうございました。'})
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': f'削除中にエラーが発生しました: {str(e)}'}), 500
    finally:
        cur.close()