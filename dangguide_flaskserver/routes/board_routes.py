# routes/board_routes.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from db import get_conn
from datetime import datetime

board_bp = Blueprint("board", __name__)

@board_bp.post("/posts/<int:post_id>/like")
def like_post(post_id: int):
    data = request.get_json(silent=True) or {}
    delta = int(data.get("delta", 1))  # 1 or -1

    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT like_count FROM posts WHERE id = ?", (post_id,))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return jsonify({"ok": False, "error": "post not found"}), 404

    new_like = max(0, row["like_count"] + delta)

    cur.execute(
        "UPDATE posts SET like_count = ? WHERE id = ?",
        (new_like, post_id),
    )
    conn.commit()
    conn.close()

    return jsonify({"ok": True, "like_count": new_like}), 200

@board_bp.get("/posts/<int:post_id>/comments")
def get_comments(post_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, author_name, content, created_at
        FROM comments
        WHERE post_id = ?
        ORDER BY id ASC
    """, (post_id,))
    rows = cur.fetchall()
    conn.close()

    comments = [
        {
            "id": row["id"],
            "author_name": row["author_name"],
            "content": row["content"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]

    return jsonify({"ok": True, "comments": comments}), 200


@board_bp.post("/posts/<int:post_id>/comments")
def create_comment(post_id: int):
    data = request.get_json(silent=True) or {}
    author_name = data.get("author_name")
    content = data.get("content")

    if not author_name or not content:
        return jsonify({"ok": False, "error": "author_name, content 필요"}), 400

    conn = get_conn()
    cur = conn.cursor()

    # 게시글 존재 여부 체크
    cur.execute("SELECT 1 FROM posts WHERE id = ?", (post_id,))
    if cur.fetchone() is None:
        conn.close()
        return jsonify({"ok": False, "error": "post not found"}), 404

    created_at = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO comments (post_id, author_name, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (post_id, author_name, content, created_at))
    conn.commit()
    conn.close()

    return jsonify({"ok": True}), 201


@board_bp.get("/posts")
def get_posts():
    conn = get_conn()
    cur = conn.cursor()

    # posts + 각 게시글의 댓글 개수
    cur.execute("""
        SELECT
          p.id,
          p.title,
          p.content,
          p.author_name,
          p.created_at,
          p.like_count,
          COUNT(c.id) AS comment_count
        FROM posts p
        LEFT JOIN comments c ON c.post_id = p.id
        GROUP BY p.id
        ORDER BY p.id DESC
    """)
    rows = cur.fetchall()
    conn.close()

    posts = [
        {
            "id": row["id"],
            "title": row["title"],
            "content": row["content"],
            "author_name": row["author_name"],
            "created_at": row["created_at"],
            "like_count": row["like_count"],
            "comment_count": row["comment_count"],
        }
        for row in rows
    ]

    return jsonify(posts), 200



@board_bp.post("/posts")
def create_post():
    """
    게시글 작성
    POST /api/posts
    body: { "title": "...", "content": "...", "author_name": "..." }
    """
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    content = data.get("content")
    author_name = data.get("author_name")

    if not title or not content or not author_name:
        return jsonify({
            "ok": False,
            "error": "title, content, author_name 모두 필요합니다."
        }), 400

    conn = get_conn()
    cur = conn.cursor()

    created_at = datetime.utcnow().isoformat()

    cur.execute(
        """
        INSERT INTO posts (title, content, author_name, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (title, content, author_name, created_at),
    )
    conn.commit()
    post_id = cur.lastrowid
    conn.close()

    return jsonify({
        "ok": True,
        "post": {
            "id": post_id,
            "title": title,
            "content": content,
            "author_name": author_name,
            "created_at": created_at,
        }
    }), 201
