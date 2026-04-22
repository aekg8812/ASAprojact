# -*- coding: utf-8 -*-
"""
Blueprintの登録と管理
"""

def register_blueprints(app):
    """
    すべてのブループリントをFlaskアプリケーションに登録
    
    Args:
        app: Flask アプリケーションインスタンス
    """
    from .auth import auth_bp
    from .equipment import equipment_bp
    from .admin import admin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(admin_bp)
