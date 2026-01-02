from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.db import get_db_connection
from app.utils import admin_required
import datetime
import cloudinary.uploader
import psycopg2

equipment_bp = Blueprint('equipment', __name__)

@equipment_bp.route('/')
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
    items = cur.fetchall()

    cur.execute('SELECT * FROM categories ORDER BY display_order')
    categories = cur.fetchall()
    
    cur.close()
    # テンプレートのパス変更: equipment/index.html
    return render_template('equipment/index.html', items=items, categories=categories, q=search_query, current_category=category_filter)

@equipment_bp.route('/mypage')
@login_required
def mypage():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM equipment WHERE borrower = %s', (current_user.username,))
    current_items = cur.fetchall()
    cur.execute('SELECT * FROM history WHERE user_id = %s ORDER BY id DESC', (current_user.id,))
    history_items = cur.fetchall()
    cur.close()
    return render_template('equipment/mypage.html', current_items=current_items, history_items=history_items)

@equipment_bp.route('/add', methods=['POST'])
@login_required
@admin_required
def add_item():
    try:
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
        flash(f'備品「{name}」を追加しました。', 'success')
        return redirect('/')
    except psycopg2.IntegrityError:
        flash(f"エラー：ID {id_val} は既に存在するため登録できません。", 'danger')
        return redirect('/')
    except Exception as e:
        flash(f"アップロードエラー: {e}", 'danger')
        return redirect('/')

@equipment_bp.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_item(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM equipment WHERE id = %s', (id,))
    item = cur.fetchone()
    cur.execute('SELECT * FROM categories ORDER BY display_order')
    categories = cur.fetchall()

    if request.method == 'POST':
        try:
            new_id = request.form['id']
            name = request.form['name']
            category = request.form['category']
            new_image_url = item['image_filename']
            
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename != '':
                    upload_result = cloudinary.uploader.upload(file)
                    new_image_url = upload_result['secure_url']

            cur.execute('UPDATE equipment SET id = %s, name = %s, category = %s, image_filename = %s WHERE id = %s', 
                         (new_id, name, category, new_image_url, id))
            conn.commit()
            cur.close()
            flash('備品情報を更新しました。', 'success')
            return redirect('/')
        except psycopg2.IntegrityError:
            conn.rollback()
            cur.close()
            return render_template('equipment/edit.html', item=item, categories=categories, error=f"エラー：ID重複")
        except Exception as e:
            conn.rollback()
            cur.close()
            return render_template('equipment/edit.html', item=item, categories=categories, error=f"エラー: {e}")
    
    cur.close()
    return render_template('equipment/edit.html', item=item, categories=categories)

@equipment_bp.route('/borrow/<int:id>', methods=['POST'])
@login_required
def borrow_item(id):
    borrower_name = current_user.username
    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute('SELECT status FROM equipment WHERE id = %s', (id,))
    status = cur.fetchone()['status']
    if status == '貸出中':
        cur.close()
        flash('タッチの差で貸出中になりました。', 'warning')
        return redirect('/')

    cur.execute('UPDATE equipment SET status = %s, borrower = %s WHERE id = %s', ('貸出中', borrower_name, id))
    cur.execute('SELECT name FROM equipment WHERE id = %s', (id,))
    item_name = cur.fetchone()['name']
    cur.execute('INSERT INTO history (user_id, equipment_id, equipment_name, borrow_date, return_date) VALUES (%s, %s, %s, %s, %s)', 
                 (current_user.id, id, item_name, now, None))
    conn.commit()
    cur.close()
    flash(f'{borrower_name} さんとして借りました！', 'success')
    return redirect('/')

@equipment_bp.route('/return/<int:id>', methods=['POST'])
@login_required
def return_item(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM equipment WHERE id = %s', (id,))
    item = cur.fetchone()
    
    if item['borrower'] != current_user.username:
        cur.close()
        flash('エラー：他人が借りている備品を返却することはできません。', 'danger')
        return redirect('/')

    now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    cur.execute('UPDATE equipment SET status = %s, borrower = %s WHERE id = %s', ('在庫あり', '', id))
    cur.execute('UPDATE history SET return_date = %s WHERE user_id = %s AND equipment_id = %s AND return_date IS NULL', (now, current_user.id, id))
    conn.commit()
    cur.close()
    flash('返却しました！', 'success')
    return redirect('/')

@equipment_bp.route('/delete/<int:id>')
@login_required
@admin_required
def delete_item(id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('DELETE FROM equipment WHERE id = %s', (id,))
    conn.commit()
    cur.close()
    flash('備品を削除しました。', 'warning')
    return redirect('/')