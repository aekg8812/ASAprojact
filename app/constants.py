# -*- coding: utf-8 -*-
"""
プロジェクト全体で使用する定数
"""

# ========== 備品のステータス ==========
EQUIPMENT_STATUS_AVAILABLE = '在庫あり'  # 借りられる状態
EQUIPMENT_STATUS_BORROWED = '貸出中'    # 借りられている状態

# ステータスの選択肢
EQUIPMENT_STATUSES = [EQUIPMENT_STATUS_AVAILABLE, EQUIPMENT_STATUS_BORROWED]

# ========== デフォルトカテゴリ ==========
DEFAULT_CATEGORIES = [
    'テント・タープ',
    '寝具',
    '調理器具',
    '照明',
    'その他'
]

# ========== エラーメッセージ ==========
ERROR_MESSAGES = {
    'password_mismatch': 'パスワード（確認用）が一致しません。',
    'username_exists': 'そのユーザー名は既に使用されています。',
    'invalid_credentials': 'ユーザー名またはパスワードが違います',
    'user_not_found': 'ユーザーが見つかりません。',
    'equipment_not_found': '見つかりません',
    'already_borrowed': 'タッチの差で貸出中になりました。',
    'not_borrower': '他人が借りている備品を返却することはできません。',
    'cannot_delete_self': '自分自身を削除することはできません。',
    'has_borrowed_items': '未返却の備品があります。全て返却してから退会してください。',
    'admin_required': 'この操作を行う権限（管理者権限）がありません。',
    'duplicate_id': 'IDが重複しています',
    'id_already_exists': 'は既に存在するため登録できません。'
}

# ========== 成功メッセージ ==========
SUCCESS_MESSAGES = {
    'register_complete': '登録完了！ログインしてください。',
    'login_success': 'ログインしました！',
    'logout_success': 'ログアウトしました。',
    'password_reset': 'パスワードを再設定しました。ログインしてください。',
    'account_deleted': 'アカウントを削除しました。ご利用ありがとうございました。',
    'item_added': '備品「{name}」を追加しました。',
    'item_updated': '備品情報を更新しました。',
    'item_deleted': '備品を削除しました。',
    'item_borrowed': '{borrower} さんとして借りました！',
    'item_returned': '返却しました！',
    'user_deleted': 'ユーザー「{username}」を削除しました。',
    'category_added': 'カテゴリを追加しました。',
    'category_deleted': 'カテゴリを削除しました。'
}

# ========== HTTP ステータスコード ==========
HTTP_OK = 200
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
HTTP_CONFLICT = 409
HTTP_SERVER_ERROR = 500
