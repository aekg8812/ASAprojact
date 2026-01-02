from functools import wraps
from flask import flash, redirect, url_for
from flask_login import current_user
from .config import Config

# 管理者権限チェック用デコレータ
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("この操作を行う権限（管理者権限）がありません。", "danger")
            return redirect('/')
        return f(*args, **kwargs)
    return decorated_function

# 拡張子チェック
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS