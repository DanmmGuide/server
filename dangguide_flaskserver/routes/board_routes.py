# dangguide_flaskserver/routes/board_routes.py

from flask import Blueprint, request, jsonify
from dao.board_dao import (
    get_posts, create_post, get_post,
    get_comments, create_comment, toggle_like,
    add_post_image, get_post_detail
)
from werkzeug.utils import secure_filename
from pathlib import Path
from datetime import datetime

board_bp = Blueprint("board", __name__)

# ====================================
# 🔥 업로드 경로 설정 (절대경로)
# ====================================
BASE_DIR = Path(__file__).resolve().parent.parent   # dangguide_flaskserver/
UPLOAD_FOLDER = BASE_DIR / "static" / "post_images"
ALLOWED_EXT = {"jpg", "jpeg", "png", "gif"}

UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


# ====================================
# 📌 게시글 목록
# ====================================
@board_bp.get("/posts")
def list_posts():
    posts = get_posts()
    return jsonify({"ok": True, "posts": posts}), 200


# ====================================
# 📌 게시글 생성
# ====================================
@board_bp.post("/posts")
def create_post_route():
    data = request.get_json(silent=True) or {}

    user_id = data.get("user_id")
    title = data.get("title")
    content = data.get("content")

    if not all([user_id, title, content]):
        return jsonify({"ok": False, "error": "user_id, title, content 필요"}), 400

    post = create_post(user_id, title, content)
    return jsonify({"ok": True, "post": post}), 201


# ====================================
# 📌 댓글 목록
# ====================================
@board_bp.get("/posts/<int:post_id>/comments")
def comments_list(post_id: int):
    return jsonify({"ok": True, "comments": get_comments(post_id)}), 200


# ====================================
# 📌 댓글 작성 (여러 번 허용)
# ====================================
@board_bp.post("/posts/<int:post_id>/comments")
def add_comment(post_id: int):
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    content = data.get("content")

    if not user_id or not content:
        return jsonify({"ok": False, "error": "user_id, content 필요"}), 400

    # ❌ 중복 검사 없음 → 같은 유저가 여러 댓글 달 수 있음
    create_comment(user_id, post_id, content)
    return jsonify({"ok": True}), 201


# ====================================
# 📌 좋아요 토글
# ====================================
@board_bp.post("/posts/<int:post_id>/like")
def like_post(post_id: int):
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"ok": False, "error": "user_id 필요"}), 400

    liked = toggle_like(post_id, user_id)
    return jsonify({"ok": True, "liked": liked}), 200


# ====================================
# 📌 이미지 업로드
# ====================================
@board_bp.post("/posts/<int:post_id>/images")
def upload_post_images(post_id: int):
    if "images" not in request.files:
        return jsonify({"ok": False, "error": "'images' 필드 필요"}), 400

    files = request.files.getlist("images")
    saved_files = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.utcnow().timestamp()
            final_name = f"{post_id}_{timestamp}_{filename}"

            save_path = UPLOAD_FOLDER / final_name
            file.save(str(save_path))

            add_post_image(post_id, final_name)
            saved_files.append(final_name)
        else:
            return jsonify({"ok": False, "error": "허용되지 않는 파일 형식"}), 400

    return jsonify({"ok": True, "files": saved_files}), 201


# ====================================
# 📌 게시글 상세
# ====================================
@board_bp.get("/posts/<int:post_id>")
def get_post_detail_route(post_id: int):
    """
    GET /api/posts/<post_id>?user_id=4
    → liked_by_me 계산하려면 user_id를 쿼리스트링으로 받음
    """
    current_user_id = request.args.get("user_id", type=int)

    detail = get_post_detail(post_id, current_user_id)
    if detail is None:
        return jsonify({"ok": False, "error": "post not found"}), 404

    # detail["images"] 는 DB에 저장된 파일 이름 리스트
    base_url = request.host_url.rstrip("/")
    detail["images"] = [
        f"{base_url}/static/post_images/{img}" for img in detail["images"]
    ]

    return jsonify({"ok": True, "post": detail}), 200
