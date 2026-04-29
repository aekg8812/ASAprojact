import os
import requests
from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.db import get_db_connection, get_user_by_username, get_user_by_id, upsert_line_user
from app.models import User
from app.constants import ERROR_MESSAGES, SUCCESS_MESSAGES, HTTP_OK, HTTP_BAD_REQUEST, HTTP_UNAUTHORIZED, HTTP_SERVER_ERROR
import psycopg2

auth_bp = Blueprint('auth', __name__)

# Render環境変数（または.env）から取得
LINE_CLIENT_ID = os.environ.get('LINE_CLIENT_ID')

@auth_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    """現在のログイン状態を確認"""
    if current_user.is_authenticated:
        # DBから最新のユーザー情報を取得してpicture_urlなども返す
        user_data = get_user_by_id(current_user.id)
        return jsonify({
            'is_authenticated': True,
            'id': current_user.id,
            'username': current_user.username,
            'is_admin': current_user.is_admin,
            'picture_url': user_data.get('picture_url') if user_data else None
        }), HTTP_OK
    return jsonify({'is_authenticated': False}), HTTP_UNAUTHORIZED


@auth_bp.route('/auth/line-login', methods=['POST']) # ✅ /auth/ を先頭に付ける
def line_login():
    """LINE IDトークンを用いたログイン・新規登録 (Upsert)"""
    data = request.json
    id_token = data.get('idToken')

    if not id_token:
        return jsonify({'status': 'error', 'message': 'ID Token is missing'}), HTTP_BAD_REQUEST

    # 1. LINE APIでトークンを検証
    verify_url = 'https://api.line.me/oauth2/v2.1/verify'
    payload = {
        'id_token': id_token,
        'client_id': LINE_CLIENT_ID
    }
    response = requests.post(verify_url, data=payload)
    
    if response.status_code != 200:
        return jsonify({'status': 'error', 'message': 'Invalid ID token'}), HTTP_UNAUTHORIZED

    # 2. ユーザー情報の抽出
    user_data = response.json()
    line_user_id = user_data.get('sub')
    display_name = user_data.get('name')
    picture_url = user_data.get('picture')

    # 3. データベースへの保存・更新 (db.py の upsert_line_user を使用)
    db_user = upsert_line_user(line_user_id, display_name, picture_url)

    if not db_user:
        return jsonify({'status': 'error', 'message': 'ユーザーデータの保存に失敗しました'}), HTTP_SERVER_ERROR

    # 4. Flask-Login を使ってセッションを開始
    is_admin = db_user.get('is_admin', False)
    
    # 既存の User モデルに合わせてインスタンス化 (password_hash はもう使わないので None で渡す)
    user = User(db_user['id'], db_user['username'], None, is_admin)
    login_user(user)

    return jsonify({
        'status': 'success', 
        'message': 'LINEログインに成功しました',
        'user': {
            'id': user.id, 
            'username': user.username, 
            'is_admin': user.is_admin,
            'picture_url': db_user['picture_url']
        }
    }), HTTP_OK


@auth_bp.route('/auth/logout', methods=['POST'])
@login_required
def logout():
    """ユーザーログアウト"""
    logout_user()
    return jsonify({'status': 'success', 'message': SUCCESS_MESSAGES['logout_success']}), HTTP_OK


@auth_bp.route('/auth/delete_account', methods=['POST'])
@login_required
def delete_account():
    """ユーザーアカウント削除"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB接続エラー'}), HTTP_SERVER_ERROR
    
    cur = conn.cursor()
    try:
        # 借りている備品がないかチェック (username ベースでの照合)
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