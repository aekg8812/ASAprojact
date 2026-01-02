import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app, g
from .config import Config

def get_db_connection():
    if 'db' not in g:
        if Config.DATABASE_URL:
            g.db = psycopg2.connect(Config.DATABASE_URL, cursor_factory=RealDictCursor)
        else:
            print("警告: DATABASE_URLが設定されていません")
            return None
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    conn = psycopg2.connect(Config.DATABASE_URL) if Config.DATABASE_URL else None
    if conn is None: return
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

    # 管理者権限設定
    if Config.ADMIN_USERNAMES:
        for name in Config.ADMIN_USERNAMES:
            cur.execute("UPDATE users SET is_admin = TRUE WHERE username = %s", (name,))
        conn.commit()
    
    # カテゴリ初期データ
    cur.execute('SELECT count(*) FROM categories')
    if cur.fetchone()[0] == 0:
        default_categories = ['テント・タープ', '寝具', '調理器具', '照明', 'その他']
        for i, name in enumerate(default_categories):
            cur.execute('INSERT INTO categories (name, display_order) VALUES (%s, %s)', (name, i))

    conn.commit()
    cur.close()
    conn.close()