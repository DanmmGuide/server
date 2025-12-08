from __future__ import annotations

from flask import Blueprint, request, jsonify

from dao.user_dao import (
    create_user,
    validate_login,
    find_user_by_username,
    delete_user_by_credentials
)

user_bp = Blueprint("user", __name__)


@user_bp.get("/users/check")
def check_username():
  """
  GET /api/users/check?username=xxx
  → { ok: true, exists: true/false }
  """
  username = (request.args.get("username") or "").strip()

  if not username:
    return jsonify({"ok": False, "error": "username 파라미터 필요"}), 400

  user = find_user_by_username(username)
  exists = user is not None

  return jsonify({"ok": True, "exists": exists}), 200


@user_bp.post("/users/register")
def register_user():
  data = request.get_json(silent=True) or {}
  username = (data.get("username") or "").strip()
  password = (data.get("password") or "").strip()

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
  username = (data.get("username") or "").strip()
  password = (data.get("password") or "").strip()

  if not username or not password:
    return jsonify({"ok": False, "error": "username과 password 필요"}), 400

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

@user_bp.post("/users/delete")
def delete_user_route():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({
            "ok": False,
            "error": "username, password 필요"
        }), 400

    ok = delete_user_by_credentials(username, password)

    if not ok:
        return jsonify({
            "ok": False,
            "error": "아이디 또는 비밀번호가 올바르지 않습니다."
        }), 400

    # 여기까지 오면 users에서 해당 유저 삭제 완료
    # posts / comments / post_likes / user_profiles 도 FK CASCADE로 함께 삭제됨
    return jsonify({"ok": True}), 200