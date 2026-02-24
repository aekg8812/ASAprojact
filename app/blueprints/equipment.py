from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app.db import get_db_connection
from app.utils import admin_required
import datetime
import cloudinary.uploader
import psycopg2

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/api/equipment', methods=['GET'])
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    search_query = request.args.get('q')
    category_filter = request.args.get('category')
    
    if search_query:
        cur.execute('SELECT * FROM equipment WHERE name LIKE %s ORDER BY id', ('%' + search_query + '%',))
    elif category_filter:
        cur.execute('SELECT * FROM equipment WHERE category = %s ORDER BY id', (category_filter,))
    else:
        cur.execute('SELECT * FROM equipment ORDER BY id')
    items = [dict(row) for row in cur.fetchall()]

    cur.execute('SELECT * FROM categories ORDER BY display_order')
    categories = [dict(row) for row in cur.fetchall()]
    cur.close()
    
    return jsonify({'items': items, 'categories': categories})

@equipment_bp.route('/api/mypage', methods=['GET'])
@login_required
def mypage():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM equipment WHERE borrower = %s', (current_user.username,))
    current_items = [dict(row) for row in cur.fetchall()]
    
    cur.execute('SELECT * FROM history WHERE user_id = %s ORDER BY id DESC', (current_user.id,))
    history_items = [dict(row) for row in cur.fetchall()]
    cur.close()
    
    return jsonify({'current_items': current_items, 'history_items': history_items})

@equipment_bp.route('/api/add', methods=['POST'])
@login_required
@admin_required
def add_item():
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
        cur = conn.cursor()
        cur.execute('INSERT INTO equipment (id, name, category, status, borrower, image_filename) VALUES (%s, %s, %s, %s, %s, %s)',
                     (id_val, name, category, '在庫あり', '', image_url))
        conn.commit()
        cur.close()
        return jsonify({'status': 'success', 'message': f'備品「{name}」を追加しました。'})
    except psycopg2.IntegrityError:
        return jsonify({'status': 'error', 'message': f"ID {id_val} は既に存在するため登録できません。"}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': f"エラー: {str(e)}"}), 500

@equipment_bp.route('/api/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_item(id):
    conn = get_db_connection()
    cur = conn.cursor()
    
    if request.method == 'GET':
        cur.execute('SELECT * FROM equipment WHERE id = %s', (id,))
        item = cur.fetchone()
        cur.execute('SELECT * FROM categories ORDER BY display_order')
        categories = cur.fetchall()
        cur.close()
        if item:
            return jsonify({'item': dict(item), 'categories': [dict(row) for row in categories]})
        return jsonify({'status': 'error', 'message': '見つかりません'}), 404

    if request.method == 'POST':
        try:
            new_id = request.form['id']
            name = request.form['name']
            category = request.form['category']
            
            cur.execute('SELECT image_filename FROM equipment WHERE id = %s', (id,))
            current_item = cur.fetchone()
            new_image_url = current_item['image_filename'] if current_item else None
            
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    upload_result = cloudinary.uploader.upload(file)
                    new_image_url = upload_result['secure_url']

            cur.execute('UPDATE equipment SET id = %s, name = %s, category = %s, image_filename = %s WHERE id = %s', 
                         (new_id, name, category, new_image_url, id))
            conn.commit()
            return jsonify({'status': 'success', 'message': '備品情報を更新しました。'})
        except psycopg2.IntegrityError:
            conn.rollback()
            return jsonify({'status': 'error', 'message': "IDが重複しています"}), 400
        except Exception as e:
            conn.rollback()
            return jsonify({'status': 'error', 'message': f"エラー: {str(e)}"}), 500
        finally:
            cur.close()

@equipment_bp.route('/api/borrow/<int:id>', methods=['POST'])
@login_required
def borrow_item(id):
    borrower_name = current_user.username
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT status, name FROM equipment WHERE id = %s', (id,))
    item = cur.fetchone()
    
    if not item or item['status'] == '貸出中':
        cur.close()
        return jsonify({'status': 'error', 'message': 'タッチの差で貸出中になりました。'}), 400

    cur.execute('UPDATE equipment SET status = %s, borrower = %s WHERE id = %s', ('貸出中', borrower_name, id))
    cur.execute('INSERT INTO history (user_id, equipment_id, equipment_name, borrow_date, return_date) VALUES (%s, %s, %s, %s, %s)', 
                 (current_user.id, id, item['name'], now, None))
    conn.commit()
    cur.close()
    return jsonify({'status': 'success', 'message': f'{borrower_name} さんとして借りました！'})

@equipment_bp.route('/api/return/<int:id>', methods=['POST'])
@login_required
def return_item(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM equipment WHERE id = %s', (id,))
    item = cur.fetchone()
    
    if not item or item['borrower'] != current_user.username:
        cur.close()
        return jsonify({'status': 'error', 'message': '他人が借りている備品を返却することはできません。'}), 400

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    cur.execute('UPDATE equipment SET status = %s, borrower = %s WHERE id = %s', ('在庫あり', '', id))
    cur.execute('UPDATE history SET return_date = %s WHERE user_id = %s AND equipment_id = %s AND return_date IS NULL', (now, current_user.id, id))
    conn.commit()
    cur.close()
    return jsonify({'status': 'success', 'message': '返却しました！'})

@equipment_bp.route('/api/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def delete_item(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM equipment WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    return jsonify({'status': 'success', 'message': '備品を削除しました。'})