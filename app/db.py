import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app, g
from .config import Config

def get_db_connection():
    """Flask リクエストコンテキスト内でDB接続を管理"""
    if 'db' not in g:
        if Config.DATABASE_URL:
            g.db = psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            print("警告: DATABASE_URLが設定されていません")
            return None
    return g.db

def close_db(e=None):
    """リクエスト終了時にDB接続をクローズ"""
    db = g.pop('db', None)
    if db is not None:
        try:
            db.close()
        except Exception as ex:
            print(f"DB クローズエラー: {ex}")

# app/db.py に追記

# app/db.py

def upsert_line_user(line_id, display_name, picture_url):
    """
    LINE IDを基にユーザーを検索し、存在しなければ新規作成、
    存在すれば名前と画像を更新します。
    """
    conn = get_db_connection()
    cur = conn.cursor()
    
    # ---------------------------------------------------------
    # 【一時的な措置】LINEの表示名で管理者を判定する
    # ※実際のLINEの表示名と完全に一致させる必要があります
    # ---------------------------------------------------------
    TEMP_ADMIN_NAMES = ["井手彩翔", "河田"] # ← お二人の実際のLINE名に変更してください
    
    # 名前がリストにあれば True、なければ False
    is_temp_admin = display_name in TEMP_ADMIN_NAMES

    # SQL: 新規作成時に is_admin を判定。更新時は既存の権限を奪わないように調整。
    sql = """
    INSERT INTO users (username, line_id, picture_url, is_admin)
    VALUES (%s, %s, %s, %s)
    ON CONFLICT (line_id) DO UPDATE 
    SET username = EXCLUDED.username,
        picture_url = EXCLUDED.picture_url,
        is_admin = users.is_admin OR EXCLUDED.is_admin
    RETURNING id, username, line_id, picture_url, is_admin;
    """
    
    try:
        cur.execute(sql, (display_name, line_id, picture_url, is_temp_admin))
        user = cur.fetchone()
        conn.commit()
        return user
    except Exception as e:
        conn.rollback()
        print(f"Error upserting line user: {e}")
        return None
    finally:
        cur.close()


# ========== ユーザー関連 ==========
def get_user_by_username(username):
    """ユーザー名からユーザー情報を取得"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE username = %s', (username,))
        user = cur.fetchone()
        return dict(user) if user else None
    finally:
        cur.close()

def get_user_by_id(user_id):
    """ユーザーIDからユーザー情報を取得"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user = cur.fetchone()
        return dict(user) if user else None
    finally:
        cur.close()

def get_all_users():
    """全ユーザー情報を取得"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute('SELECT id, username, is_admin FROM users ORDER BY id')
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()

# ========== 備品関連 ==========
def get_equipment_by_id(equipment_id):
    """備品IDから備品情報を取得"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM equipment WHERE id = %s', (equipment_id,))
        item = cur.fetchone()
        return dict(item) if item else None
    finally:
        cur.close()

def get_all_equipment(search_query=None, category_filter=None):
    """
    全備品を取得（検索・フィルタ対応）
    
    Args:
        search_query: 名前検索用クエリ
        category_filter: カテゴリでのフィルタ
    
    Returns:
        備品の辞書リスト
    """
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        if search_query:
            cur.execute(
                'SELECT * FROM equipment WHERE name LIKE %s ORDER BY id',
                ('%' + search_query + '%',)
            )
        elif category_filter:
            cur.execute(
                'SELECT * FROM equipment WHERE category = %s ORDER BY id',
                (category_filter,)
            )
        else:
            cur.execute('SELECT * FROM equipment ORDER BY id')
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()

def get_user_borrowed_equipment(username):
    """ユーザーが現在借りている備品を取得"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM equipment WHERE borrower = %s', (username,))
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()

# ========== カテゴリ関連 ==========
def get_all_categories():
    """全カテゴリを取得（表示順序順）"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute('SELECT * FROM categories ORDER BY display_order')
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()

# ========== 履歴関連 ==========
def get_user_history(user_id):
    """ユーザーの借用履歴を取得"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute(
            'SELECT * FROM history WHERE user_id = %s ORDER BY id DESC',
            (user_id,)
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()

def get_all_history():
    """全借用履歴を取得（全ユーザー分）"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        cur = conn.cursor()
        cur.execute('''
            SELECT h.*, u.username 
            FROM history h 
            LEFT JOIN users u ON h.user_id = u.id 
            ORDER BY h.id DESC
        ''')
        return [dict(row) for row in cur.fetchall()]
    finally:
        cur.close()

def init_db():
    """データベーステーブルの初期化と定義"""
    from .constants import DEFAULT_CATEGORIES
    
    conn = psycopg2.connect(Config.DATABASE_URL) if Config.DATABASE_URL else None
    if conn is None: 
        return
    
    try:
        cur = conn.cursor()
        
        # テーブル作成
        cur.execute('''
            CREATE TABLE IF NOT EXISTS equipment (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                category TEXT,
                status TEXT DEFAULT '在庫あり',
                borrower TEXT,
                image_filename TEXT 
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                display_order INTEGER DEFAULT 0
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL
            )
        ''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id SERIAL PRIMARY KEY,
                user_id INTEGER,
                equipment_id INTEGER,
                equipment_name TEXT,
                borrow_date TEXT,
                return_date TEXT
            )
        ''')

        # マイグレーション
        try:
            cur.execute("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE;")
        except psycopg2.errors.DuplicateColumn:
            conn.rollback() 
        except Exception as e:
            conn.rollback()
            print(f"カラム追加スキップ: {e}")

       
            conn.commit()
        
        # カテゴリ初期データ
        cur.execute('SELECT count(*) FROM categories')
        if cur.fetchone()[0] == 0:
            for i, name in enumerate(DEFAULT_CATEGORIES):
                cur.execute('INSERT INTO categories (name, display_order) VALUES (%s, %s)', (name, i))

        conn.commit()
    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()