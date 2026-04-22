from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db_connection, get_user_by_username, get_user_by_id
from app.models import User
from app.constants import ERROR_MESSAGES, SUCCESS_MESSAGES, HTTP_OK, HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED, HTTP_NOT_FOUND, HTTP_SERVER_ERROR
import psycopg2

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    """現在のログイン状態を確認"""
    if current_user.is_authenticated:
        return jsonify({
            'is_authenticated': True,
            'id': current_user.id,
            'username': current_user.username,
            'is_admin': current_user.is_admin
        }), HTTP_OK
    return jsonify({'is_authenticated': False}), HTTP_UNAUTHORIZED

@auth_bp.route('/register', methods=['POST'])
def register():
    """新規ユーザー登録"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    confirm_password = data.get('confirm_password')

    if password != confirm_password:
        return jsonify({'status': 'error', 'message': ERROR_MESSAGES['password_mismatch']}), HTTP_BAD_REQUEST
    
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB接続エラー'}), HTTP_SERVER_ERROR
    
    cur = conn.cursor()
    try:
        hashed_password = generate_password_hash(password)
        cur.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)', 
                   (username, hashed_password, False))
        conn.commit()
        return jsonify({'status': 'success', 'message': SUCCESS_MESSAGES['register_complete']}), HTTP_OK
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'status': 'error', 'message': ERROR_MESSAGES['username_exists']}), HTTP_BAD_REQUEST
    finally:
        cur.close()

@auth_bp.route('/login', methods=['POST'])
def login():
    """ユーザーログイン"""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    user_data = get_user_by_username(username)
    
    if user_data and check_password_hash(user_data['password_hash'], password):
        is_admin = user_data.get('is_admin', False)
        user = User(user_data['id'], user_data['username'], user_data['password_hash'], is_admin)
        login_user(user)
        return jsonify({
            'status': 'success', 
            'message': SUCCESS_MESSAGES['login_success'],
            'user': {'id': user.id, 'username': user.username, 'is_admin': user.is_admin}
        }), HTTP_OK
    else:
        return jsonify({'status': 'error', 'message': ERROR_MESSAGES['invalid_credentials']}), HTTP_UNAUTHORIZED

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    """ユーザーログアウト"""
    logout_user()
    return jsonify({'status': 'success', 'message': SUCCESS_MESSAGES['logout_success']}), HTTP_OK

@auth_bp.route('/reset_password', methods=['POST'])
def reset_password():
    """パスワードリセット"""
    data = request.json
    step = data.get('step')

    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB接続エラー'}), HTTP_SERVER_ERROR

    cur = conn.cursor()
    try:
        if step == 'check_user':
            username = data.get('username')
            user = get_user_by_username(username)
            if user:
                return jsonify({'status': 'success', 'user_id': user['id'], 'username': username}), HTTP_OK
            else:
                return jsonify({'status': 'error', 'message': ERROR_MESSAGES['user_not_found']}), HTTP_NOT_FOUND
                
        elif step == 'reset_pass':
            user_id = data.get('user_id')
            new_password = data.get('new_password')
            confirm_password = data.get('confirm_password')
            
            if new_password != confirm_password:
                return jsonify({'status': 'error', 'message': ERROR_MESSAGES['password_mismatch']}), HTTP_BAD_REQUEST
                
            new_hash = generate_password_hash(new_password)
            cur.execute('UPDATE users SET password_hash = %s WHERE id = %s', (new_hash, user_id))
            conn.commit()
            return jsonify({'status': 'success', 'message': SUCCESS_MESSAGES['password_reset']}), HTTP_OK
    finally:
        cur.close()

@auth_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    """ユーザーアカウント削除"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB接続エラー'}), HTTP_SERVER_ERROR
    
    cur = conn.cursor()
    try:
        cur.execute('SELECT count(*) FROM equipment WHERE borrower = %s', (current_user.username,))
        borrowing_count = cur.fetchone()['count']
        
        if borrowing_count > 0:
            return jsonify({
                'status': 'error', 
                'message': ERROR_MESSAGES['has_borrowed_items'] + f' ({borrowing_count} 個)'
            }), HTTP_BAD_REQUEST
        
        cur.execute('DELETE FROM users WHERE id = %s', (current_user.id,))
        conn.commit()
        logout_user()
        return jsonify({'status': 'success', 'message': SUCCESS_MESSAGES['account_deleted']}), HTTP_OK
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': f'削除中にエラーが発生しました: {str(e)}'}), HTTP_SERVER_ERROR
    finally:
        cur.close()