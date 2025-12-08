# dangguide_flaskserver/routes/board_routes.py
from flask import Blueprint, request, jsonify, session

from dao.board_dao import (
    get_post_detail,
    add_comment,
    toggle_like,
)

board_bp = Blueprint("board_bp", __name__)


def get_current_user_id() -> int | None:
    """
    로그인 시 session["user_id"]에 넣어뒀다고 가정.
    JWT 쓰면 여기서 토큰 decode해서 user_id 꺼내기.
    """
    return session.get("user_id")


# -----------------------------
# 게시글 상세 (글쓴이/댓글 작성자 이름 포함)
# -----------------------------
@board_bp.route("/posts/<int:post_id>", methods=["GET"])
def api_get_post_detail(post_id):
    post = get_post_detail(post_id)
    if post is None:
        return jsonify({"ok": False, "error": "NOT_FOUND"}), 404

    return jsonify({"ok": True, "post": post})


# -----------------------------
# 댓글 작성 (로그인 유저 기준)
# -----------------------------
@board_bp.route("/posts/<int:post_id>/comments", methods=["POST"])
def api_add_comment(post_id):
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"ok": False, "error": "UNAUTHORIZED"}), 401

    data = request.get_json() or {}
    content = data.get("content", "").strip()

    if not content:
        return jsonify({"ok": False, "error": "EMPTY_CONTENT"}), 400

    add_comment(post_id, user_id, content)

    # 새 댓글까지 포함된 최신 post 정보 다시 내려주기
    post = get_post_detail(post_id)
    return jsonify({"ok": True, "post": post})


# -----------------------------
# 좋아요 토글 (로그인 유저 기준)
# -----------------------------
@board_bp.route("/posts/<int:post_id>/like", methods=["POST"])
def api_toggle_like(post_id):
    user_id = get_current_user_id()
    if user_id is None:
        return jsonify({"ok": False, "error": "UNAUTHORIZED"}), 401

    liked, like_count = toggle_like(post_id, user_id)

    return jsonify({
        "ok": True,
        "liked": liked,
        "like_count": like_count,
    })
