from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.db import get_db_connection
from app.models import User
import psycopg2

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        if password != confirm_password:
            flash('パスワード（確認用）が一致しません。', 'danger')
            return render_template('auth/register.html')
        
        conn = get_db_connection()
        cur = conn.cursor()
        try:
            hashed_password = generate_password_hash(password)
            cur.execute('INSERT INTO users (username, password_hash, is_admin) VALUES (%s, %s, %s)', (username, hashed_password, False))
            conn.commit()
            flash('登録完了！ログインしてください。', 'success')
            return redirect(url_for('auth.login'))
        except psycopg2.IntegrityError:
            conn.rollback()
            flash('そのユーザー名は既に使用されています。', 'danger')
        finally:
            cur.close()
            
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user_data = cur.fetchone()
        cur.close()
        
        if user_data and check_password_hash(user_data['password_hash'], password):
            is_admin = user_data.get('is_admin', False)
            user = User(user_data['id'], user_data['username'], user_data['password_hash'], is_admin)
            login_user(user)
            flash('ログインしました！', 'success')
            return redirect('/')
        else:
            flash('ユーザー名またはパスワードが違います', 'danger')
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('ログアウトしました。', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST' and 'check_user' in request.form:
        username = request.form['username']
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        cur.close()
        if user:
            return render_template('auth/reset_password.html', step='new_pass', user_id=user['id'], username=username)
        else:
            flash('そのユーザー名は登録されていません。', 'danger')
            return redirect(url_for('auth.reset_password'))
            
    if request.method == 'POST' and 'reset_pass' in request.form:
        user_id = request.form['user_id']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        if new_password != confirm_password:
            flash('新しいパスワードが一致しません。', 'danger')
            return redirect(url_for('auth.reset_password'))
        conn = get_db_connection()
        cur = conn.cursor()
        new_hash = generate_password_hash(new_password)
        cur.execute('UPDATE users SET password_hash = %s WHERE id = %s', (new_hash, user_id))
        conn.commit()
        cur.close()
        flash('パスワードを再設定しました。ログインしてください。', 'success')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', step='input_user')

@auth_bp.route('/delete_account', methods=['POST'])
@login_required
def delete_account():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT count(*) FROM equipment WHERE borrower = %s', (current_user.username,))
    borrowing_count = cur.fetchone()['count']
    
    if borrowing_count > 0:
        flash(f'未返却の備品が {borrowing_count} 個あります。全て返却してから退会してください。', 'danger')
        cur.close()
        return redirect(url_for('equipment.mypage'))
    try:
        cur.execute('DELETE FROM users WHERE id = %s', (current_user.id,))
        conn.commit()
        cur.close()
        logout_user()
        flash('アカウントを削除しました。ご利用ありがとうございました。', 'info')
        return redirect('/')
    except Exception as e:
        cur.close()
        flash('削除中にエラーが発生しました。', 'danger')
        return redirect(url_for('equipment.mypage'))