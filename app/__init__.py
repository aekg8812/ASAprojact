import os
import cloudinary
from flask import Flask
from flask_cors import CORS  # 👈 1. これを追加！
from flask_login import LoginManager
from .config import Config
from .db import init_db, close_db, get_user_by_id
from .models import User

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

  # CORS設定を修正
    CORS(app, resources={r"/*": {"origins": [
        "https://localhost:5173",    # ✅ 追加：HTTPSのローカル環境を許可
        "http://localhost:5173",     # (既存)
        "http://127.0.0.1:5173",    # (既存)
        "https://campkit-frontend.onrender.com" # (既存)
    ]}}, supports_credentials=True)

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
        user_data = get_user_by_id(user_id)
        if user_data:
            is_admin = user_data.get('is_admin', False)
            return User(user_data['id'], user_data['username'], user_data['password_hash'], is_admin)
        return None

    # DB切断の登録
    app.teardown_appcontext(close_db)

    # Blueprintsの登録
    from .blueprints import register_blueprints
    register_blueprints(app)

    # DB初期化（テーブル作成）
    try:
        with app.app_context():
            init_db()
            print("DB初期化完了")
    except Exception as e:
        print(f"DB初期化スキップ: {e}")

    return app