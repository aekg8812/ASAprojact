import os
import cloudinary
from flask import Flask
from flask_login import LoginManager
from .config import Config
from .db import init_db, close_db, get_db_connection
from .models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Cloudinary設定
    cloudinary.config(
        cloud_name = app.config['CLOUDINARY_CLOUD_NAME'],
        api_key = app.config['CLOUDINARY_API_KEY'],
        api_secret = app.config['CLOUDINARY_API_SECRET'],
        secure = True
    )

    # Flask-Login設定
    login_manager = LoginManager()
    login_manager.init_app(app)
    # 未ログイン時に飛ばされる先を指定 (authブループリントのlogin関数)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        user_data = cur.fetchone()
        cur.close()
        if user_data:
            is_admin = user_data.get('is_admin', False)
            return User(user_data['id'], user_data['username'], user_data['password_hash'], is_admin)
        return None

    # DB切断の登録
    app.teardown_appcontext(close_db)

    # Blueprintsの登録
    from .blueprints.auth import auth_bp
    from .blueprints.equipment import equipment_bp
    from .blueprints.admin import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(admin_bp)

    # DB初期化（テーブル作成）
    try:
        with app.app_context():
            init_db()
            print("DB初期化完了")
    except Exception as e:
        print(f"DB初期化スキップ: {e}")

    return app