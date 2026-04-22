from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.db import (
    get_db_connection, get_all_equipment, get_all_categories, 
    get_equipment_by_id, get_user_borrowed_equipment, get_user_history
)
from app.utils import admin_required
from app.constants import (
    EQUIPMENT_STATUS_AVAILABLE, EQUIPMENT_STATUS_BORROWED,
    ERROR_MESSAGES, SUCCESS_MESSAGES,
    HTTP_OK, HTTP_BAD_REQUEST, HTTP_NOT_FOUND, HTTP_SERVER_ERROR
)
import datetime
import cloudinary.uploader
import psycopg2

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/api/equipment', methods=['GET'])
def index():
    """全備品を取得（検索・カテゴリフィルタ対応）"""
    search_query = request.args.get('q')
    category_filter = request.args.get('category')
    
    items = get_all_equipment(search_query=search_query, category_filter=category_filter)
    categories = get_all_categories()
    
    return jsonify({'items': items, 'categories': categories}), HTTP_OK

@equipment_bp.route('/api/mypage', methods=['GET'])
@login_required
def mypage():
    """ユーザーが借りてる備品と履歴を取得"""
    current_items = get_user_borrowed_equipment(current_user.username)
    history_items = get_user_history(current_user.id)
    
    return jsonify({'current_items': current_items, 'history_items': history_items}), HTTP_OK

@equipment_bp.route('/api/add', methods=['POST'])
@login_required
@admin_required
def add_item():
    """新規備品を追加（管理者のみ）"""
    try:
        # 写真アップロードを含むため request.form を使用
        id_val = request.form['id']
        name = request.form['name']
        category = request.form['category']
        
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and file.filename != '':
                upload_result = cloudinary.uploader.upload(file)
                image_url = upload_result['secure_url']
        
        conn = get_db_connection()
        if not conn:
            return jsonify({'status': 'error', 'message': 'DB接続エラー'}), HTTP_SERVER_ERROR
        
        cur = conn.cursor()
        try:
            cur.execute(
                'INSERT INTO equipment (id, name, category, status, borrower, image_filename) VALUES (%s, %s, %s, %s, %s, %s)',
                (id_val, name, category, EQUIPMENT_STATUS_AVAILABLE, '', image_url)
            )
            conn.commit()
            return jsonify({
                'status': 'success', 
                'message': SUCCESS_MESSAGES['item_added'].format(name=name)
            }), HTTP_OK
        except psycopg2.IntegrityError:
            conn.rollback()
            return jsonify({
                'status': 'error', 
                'message': f"ID {id_val} {ERROR_MESSAGES['id_already_exists']}"
            }), HTTP_BAD_REQUEST
        finally:
            cur.close()
    except Exception as e:
        return jsonify({'status': 'error', 'message': f"エラー: {str(e)}"}), HTTP_SERVER_ERROR

@equipment_bp.route('/api/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_item(id):
    """備品情報を編集（管理者のみ）"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB接続エラー'}), HTTP_SERVER_ERROR
    
    cur = conn.cursor()
    try:
        if request.method == 'GET':
            item = get_equipment_by_id(id)
            categories = get_all_categories()
            if item:
                return jsonify({'item': item, 'categories': categories}), HTTP_OK
            return jsonify({'status': 'error', 'message': ERROR_MESSAGES['equipment_not_found']}), HTTP_NOT_FOUND

        if request.method == 'POST':
            new_id = request.form['id']
            name = request.form['name']
            category = request.form['category']
            
            current_item = get_equipment_by_id(id)
            new_image_url = current_item['image_filename'] if current_item else None
            
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    upload_result = cloudinary.uploader.upload(file)
                    new_image_url = upload_result['secure_url']

            cur.execute(
                'UPDATE equipment SET id = %s, name = %s, category = %s, image_filename = %s WHERE id = %s', 
                (new_id, name, category, new_image_url, id)
            )
            conn.commit()
            return jsonify({'status': 'success', 'message': SUCCESS_MESSAGES['item_updated']}), HTTP_OK
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'status': 'error', 'message': ERROR_MESSAGES['duplicate_id']}), HTTP_BAD_REQUEST
    except Exception as e:
        conn.rollback()
        return jsonify({'status': 'error', 'message': f"エラー: {str(e)}"}), HTTP_SERVER_ERROR
    finally:
        cur.close()

@equipment_bp.route('/api/borrow/<int:id>', methods=['POST'])
@login_required
def borrow_item(id):
    """備品を借りる"""
    borrower_name = current_user.username
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    
    item = get_equipment_by_id(id)
    if not item or item['status'] == EQUIPMENT_STATUS_BORROWED:
        return jsonify({'status': 'error', 'message': ERROR_MESSAGES['already_borrowed']}), HTTP_BAD_REQUEST

    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB接続エラー'}), HTTP_SERVER_ERROR
    
    cur = conn.cursor()
    try:
        cur.execute(
            'UPDATE equipment SET status = %s, borrower = %s WHERE id = %s', 
            (EQUIPMENT_STATUS_BORROWED, borrower_name, id)
        )
        cur.execute(
            'INSERT INTO history (user_id, equipment_id, equipment_name, borrow_date, return_date) VALUES (%s, %s, %s, %s, %s)', 
            (current_user.id, id, item['name'], now, None)
        )
        conn.commit()
        return jsonify({
            'status': 'success', 
            'message': SUCCESS_MESSAGES['item_borrowed'].format(borrower=borrower_name)
        }), HTTP_OK
    finally:
        cur.close()

@equipment_bp.route('/api/return/<int:id>', methods=['POST'])
@login_required
def return_item(id):
    """備品を返却する"""
    item = get_equipment_by_id(id)
    if not item or item['borrower'] != current_user.username:
        return jsonify({'status': 'error', 'message': ERROR_MESSAGES['not_borrower']}), HTTP_BAD_REQUEST

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB接続エラー'}), HTTP_SERVER_ERROR
    
    cur = conn.cursor()
    try:
        cur.execute(
            'UPDATE equipment SET status = %s, borrower = %s WHERE id = %s', 
            (EQUIPMENT_STATUS_AVAILABLE, '', id)
        )
        cur.execute(
            'UPDATE history SET return_date = %s WHERE user_id = %s AND equipment_id = %s AND return_date IS NULL', 
            (now, current_user.id, id)
        )
        conn.commit()
        return jsonify({'status': 'success', 'message': SUCCESS_MESSAGES['item_returned']}), HTTP_OK
    finally:
        cur.close()

@equipment_bp.route('/api/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_item(id):
    """備品を削除（管理者のみ）"""
    conn = get_db_connection()
    if not conn:
        return jsonify({'status': 'error', 'message': 'DB接続エラー'}), HTTP_SERVER_ERROR
    
    cur = conn.cursor()
    try:
        cur.execute('DELETE FROM equipment WHERE id = %s', (id,))
        conn.commit()
        return jsonify({'status': 'success', 'message': SUCCESS_MESSAGES['item_deleted']}), HTTP_OK
    finally:
        cur.close()