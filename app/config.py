import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'secret_key_asa_project')
    
    # ---------------------------------------------------------
    # ★DB接続設定
    # ローカルで動かすときは、ここにRenderの「External Database URL」を貼ってください
    # 例: "postgresql://user:password@hostname/dbname"
    # ---------------------------------------------------------
    # 環境変数がなければ、下の文字列を使います
    # 環境変数から読み込む安全な状態に戻す
    DATABASE_URL = os.environ.get('DATABASE_URL')

    # RenderのURLが 'postgres://' で始まっている場合、 'postgresql://' に修正する処理
    if DATABASE_URL and DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    
    # Cloudinary設定
    CLOUDINARY_CLOUD_NAME = os.environ.get('CLOUDINARY_CLOUD_NAME') or "あなたのCloud Name"
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY') or "あなたのAPI Key"
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET') or "あなたのAPI Secret"

    # アップロードフォルダ
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # 管理者リスト
    ADMIN_USERNAMES = ["井手彩翔", "dkawa"]

    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = True