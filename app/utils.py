from functools import wraps
from flask import jsonify
from flask_login import current_user
from .config import Config
from .constants import ERROR_MESSAGES, HTTP_BAD_REQUEST

# ========== 権限チェックデコレータ ==========

def admin_required(f):
    """
    管理者権限チェック用デコレータ
    
    @admin_required でマークされたエンドポイントは、
    管理者権限を持つユーザーのみアクセス可能
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            return jsonify({
                'status': 'error', 
                'message': ERROR_MESSAGES['admin_required']
            }), HTTP_BAD_REQUEST
        return f(*args, **kwargs)
    return decorated_function

# ========== ファイル関連ユーティリティ ==========

def allowed_file(filename):
    """
    ファイルがアップロード可能かチェック
    
    Args:
        filename: ファイル名
    
    Returns:
        True: アップロード可能な拡張子
        False: アップロード不可の拡張子
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS