from flask import Blueprint, request, jsonify
from dao.user_dao import create_user, validate_login, find_user_by_username

user_bp = Blueprint("user", __name__)


@user_bp.post("/users/register")
def register_user():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"ok": False, "error": "username과 password 필요"}), 400

    # 중복 체크
    if find_user_by_username(username):
        return jsonify({"ok": False, "error": "이미 존재하는 username"}), 409

    user = create_user(username, password)
    if user is None:
        return jsonify({"ok": False, "error": "회원가입 실패"}), 500

    return jsonify({"ok": True, "user": user}), 201


@user_bp.post("/users/login")
def login_user():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    user = validate_login(username, password)
    if user is None:
        return jsonify({"ok": False, "error": "로그인 실패"}), 401

    return jsonify({
        "ok": True,
        "user": {
            "id": user["id"],
            "username": user["username"],
        }
    }), 200
