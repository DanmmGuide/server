from db import get_conn
from datetime import datetime


# --------------------------
# 게시글 관련
# --------------------------

def create_post(user_id: int, title: str, content: str):
    conn = get_conn()
    cur = conn.cursor()

    created_at = datetime.utcnow().isoformat()

    cur.execute("""
        INSERT INTO posts (user_id, title, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, title, content, created_at))

    conn.commit()
    post_id = cur.lastrowid
    conn.close()

    return {
        "id": post_id,
        "user_id": user_id,
        "title": title,
        "content": content,
        "created_at": created_at,
        "like_count": 0,
        "comment_count": 0,
    }


def get_posts():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            p.id,
            p.user_id,
            u.username,
            p.title,
            p.content,
            p.created_at,
            p.like_count,
            p.comment_count
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.id DESC
    """)

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "user_id": row["user_id"],
            "username": row["username"],
            "title": row["title"],
            "content": row["content"],
            "created_at": row["created_at"],
            "like_count": row["like_count"],
            "comment_count": row["comment_count"]
        }
        for row in rows
    ]


def get_post(post_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT p.*, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
    """, (post_id,))
    row = cur.fetchone()
    conn.close()

    return row


# --------------------------
# 댓글 관련
# --------------------------

def create_comment(user_id: int, post_id: int, content: str):
    conn = get_conn()
    cur = conn.cursor()

    created_at = datetime.utcnow().isoformat()

    # 댓글 추가
    cur.execute("""
        INSERT INTO comments (user_id, post_id, content, created_at)
        VALUES (?, ?, ?, ?)
    """, (user_id, post_id, content, created_at))

    # 게시글 댓글 수 증가
    cur.execute("""
        UPDATE posts SET comment_count = comment_count + 1
        WHERE id = ?
    """, (post_id,))

    conn.commit()
    comment_id = cur.lastrowid
    conn.close()

    return comment_id


def get_comments(post_id: int):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT c.id, c.content, c.created_at, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.id ASC
    """, (post_id,))

    rows = cur.fetchall()
    conn.close()

    return [
        {
            "id": row["id"],
            "username": row["username"],
            "content": row["content"],
            "created_at": row["created_at"],
        }
        for row in rows
    ]


# --------------------------
# 좋아요 관련
# --------------------------

def toggle_like(post_id: int, user_id: int):
    conn = get_conn()
    cur = conn.cursor()

    # 좋아요 이미 있는지 확인
    cur.execute("""
        SELECT 1 FROM post_likes
        WHERE post_id = ? AND user_id = ?
    """, (post_id, user_id))
    exists = cur.fetchone()

    if exists:
        # 좋아요 취소
        cur.execute("""
            DELETE FROM post_likes
            WHERE post_id = ? AND user_id = ?
        """, (post_id, user_id))

        cur.execute("""
            UPDATE posts SET like_count = like_count - 1
            WHERE id = ?
        """, (post_id,))
        conn.commit()
        conn.close()
        return False  # 좋아요 취소됨

    else:
        # 좋아요 추가
        cur.execute("""
            INSERT INTO post_likes (post_id, user_id)
            VALUES (?, ?)
        """, (post_id, user_id))

        cur.execute("""
            UPDATE posts SET like_count = like_count + 1
            WHERE id = ?
        """, (post_id,))

        conn.commit()
        conn.close()
        return True  # 좋아요 추가됨

def add_post_image(post_id: int, image_path: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO post_images (post_id, image_path)
        VALUES (?, ?)
    """, (post_id, image_path))

    conn.commit()
    conn.close()

def get_post_detail(post_id: int):
    conn = get_conn()
    cur = conn.cursor()

    # 게시글 정보 + 작성자 이름
    cur.execute("""
        SELECT p.*, u.username
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
    """, (post_id,))
    post = cur.fetchone()

    if post is None:
        conn.close()
        return None

    # 이미지
    cur.execute("SELECT image_path FROM post_images WHERE post_id = ?", (post_id,))
    images = [row["image_path"] for row in cur.fetchall()]

    # 댓글
    cur.execute("""
        SELECT c.id, c.content, c.created_at, u.username
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.id ASC
    """, (post_id,))
    comments = [
        {
            "id": row["id"],
            "username": row["username"],
            "content": row["content"],
            "created_at": row["created_at"]
        }
        for row in cur.fetchall()
    ]

    conn.close()

    return {
        "id": post["id"],
        "user_id": post["user_id"],
        "username": post["username"],
        "title": post["title"],
        "content": post["content"],
        "created_at": post["created_at"],
        "like_count": post["like_count"],
        "comment_count": post["comment_count"],
        "images": images,
        "comments": comments
    }
