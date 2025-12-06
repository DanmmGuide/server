from flask import Blueprint, request, jsonify
from dao.board_dao import (
    get_posts, create_post, get_post,
    get_comments, create_comment, toggle_like
    ,add_post_image, get_post_detail
)
import os
from werkzeug.utils import secure_filename
board_bp = Blueprint("board", __name__)


# --------------------------
# 게시글 목록
# --------------------------
@board_bp.get("/posts")
def list_posts():
    posts = get_posts()
    return jsonify({"ok": True, "posts": posts}), 200


# --------------------------
# 게시글 작성
# --------------------------
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


# --------------------------
# 댓글 가져오기
# --------------------------
@board_bp.get("/posts/<int:post_id>/comments")
def comments_list(post_id):
    return jsonify({"ok": True, "comments": get_comments(post_id)}), 200


# --------------------------
# 댓글 작성
# --------------------------
@board_bp.post("/posts/<int:post_id>/comments")
def add_comment(post_id):
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    content = data.get("content")

    if not user_id or not content:
        return jsonify({"ok": False, "error": "user_id, content 필요"}), 400

    create_comment(user_id, post_id, content)
    return jsonify({"ok": True}), 201


# --------------------------
# 좋아요
# --------------------------
@board_bp.post("/posts/<int:post_id>/like")
def like_post(post_id):
    data = request.get_json(silent=True) or {}
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"ok": False, "error": "user_id 필요"}), 400

    liked = toggle_like(post_id, user_id)
    return jsonify({"ok": True, "liked": liked}), 200

UPLOAD_FOLDER = "static/post_images"
ALLOWED_EXT = {"jpg", "jpeg", "png", "gif"}


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXT


@board_bp.post("/posts/<int:post_id>/images")
def upload_post_images(post_id):
    if "images" not in request.files:
        return jsonify({"ok": False, "error": "images 필드 필요"}), 400

    files = request.files.getlist("images")
    saved_files = []

    for file in files:
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)

            # 파일명 중복 방지
            final_name = f"{post_id}_{datetime.utcnow().timestamp()}_{filename}"

            save_path = os.path.join(UPLOAD_FOLDER, final_name)
            file.save(save_path)

            # DB에 저장
            add_post_image(post_id, final_name)
            saved_files.append(final_name)
        else:
            return jsonify({"ok": False, "error": "허용되지 않는 파일 형식"}), 400

    return jsonify({"ok": True, "files": saved_files}), 201

@board_bp.get("/posts/<int:post_id>/images")
def list_post_images(post_id):
    images = get_post_images(post_id)

    # URL 형태로 변환
    base_url = request.host_url.rstrip("/")
    image_urls = [f"{base_url}/static/post_images/{img}" for img in images]

    return jsonify({"ok": True, "images": image_urls}), 200

@board_bp.get("/posts/<int:post_id>")
def get_post_detail_route(post_id: int):
    row = get_post_detail(post_id)  # 내부에서 comments까지 붙여서 dict 하나로 준다고 가정
    if not row:
        return jsonify({"ok": False, "error": "NOT_FOUND"}), 404

    return jsonify({"ok": True, "post": row}), 200