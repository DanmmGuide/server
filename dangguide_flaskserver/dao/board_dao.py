# dangguide_flaskserver/dao/board_dao.py

from typing import Any, Dict, List, Optional
from db import get_conn


# ========================================
# 📌 게시글 목록
# ========================================
def get_posts() -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT 
            p.id,
            p.title,
            p.content,
            p.created_at,
            u.username AS author_name,
            (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.id) AS like_count,
            (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count
        FROM posts p
        JOIN users u ON u.id = p.user_id
        ORDER BY p.created_at DESC
        """
    )

    posts: List[Dict[str, Any]] = []
    rows = cur.fetchall()

    for row in rows:
        post_id = row["id"]

        # 이미지 목록
        img_cur = conn.cursor()
        img_cur.execute(
            """
            SELECT image_path
            FROM post_images
            WHERE post_id = ?
            ORDER BY id ASC
            """,
            (post_id,),
        )
        img_rows = img_cur.fetchall()
        image_list = [r["image_path"] for r in img_rows]

        posts.append(
            {
                "id": row["id"],
                "title": row["title"],
                "content": row["content"],
                "created_at": row["created_at"],
                "author_name": row["author_name"],
                "like_count": row["like_count"],
                "comment_count": row["comment_count"],
                "images": image_list,
            }
        )

    conn.close()
    return posts


# ========================================
# 📌 게시글 생성
# ========================================
def create_post(user_id: int, title: str, content: str) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO posts (user_id, title, content, like_count, comment_count)
        VALUES (?, ?, ?, 0, 0)
        """,
        (user_id, title, content),
    )
    conn.commit()

    post_id = cur.lastrowid

    cur.execute(
        """
        SELECT
            p.id,
            p.title,
            p.content,
            p.created_at,
            u.username AS author_name,
            p.like_count,
            p.comment_count
        FROM posts p
        JOIN users u ON u.id = p.user_id
        WHERE p.id = ?
        """,
        (post_id,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return {
            "id": post_id,
            "title": title,
            "content": content,
            "created_at": None,
            "author_name": None,
            "like_count": 0,
            "comment_count": 0,
            "images": [],
        }

    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "created_at": row["created_at"],
        "author_name": row["author_name"],
        "like_count": row["like_count"],
        "comment_count": row["comment_count"],
        "images": [],
    }


# ========================================
# 📌 게시글 단일 조회 (간단)
# ========================================
def get_post(post_id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            p.id,
            p.title,
            p.content,
            p.created_at,
            u.username AS author_name,
            (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.id) AS like_count,
            (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count
        FROM posts p
        JOIN users u ON u.id = p.user_id
        WHERE p.id = ?
        """,
        (post_id,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return None

    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "created_at": row["created_at"],
        "author_name": row["author_name"],
        "like_count": row["like_count"],
        "comment_count": row["comment_count"],
    }


# ========================================
# 📌 댓글 목록
# ========================================
def get_comments(post_id: int) -> List[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            c.id,
            c.content,
            c.created_at,
            u.username AS author_name
        FROM comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.post_id = ?
        ORDER BY c.created_at ASC
        """,
        (post_id,),
    )

    rows = cur.fetchall()
    conn.close()

    comments: List[Dict[str, Any]] = []
    for row in rows:
        comments.append(
            {
                "id": row["id"],
                "content": row["content"],
                "created_at": row["created_at"],
                "author_name": row["author_name"],
            }
        )

    return comments


# ========================================
# 📌 댓글 생성
# ========================================
def create_comment(user_id: int, post_id: int, content: str) -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO comments (user_id, post_id, content)
        VALUES (?, ?, ?)
        """,
        (user_id, post_id, content),
    )

    cur.execute(
        """
        UPDATE posts
        SET comment_count = comment_count + 1
        WHERE id = ?
        """,
        (post_id,),
    )

    conn.commit()
    conn.close()


# ========================================
# 📌 좋아요 토글 (post_likes 사용)
# ========================================
def toggle_like(post_id: int, user_id: int) -> bool:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id
        FROM post_likes
        WHERE post_id = ? AND user_id = ?
        """,
        (post_id, user_id),
    )
    row = cur.fetchone()

    if row:
        cur.execute(
            """
            DELETE FROM post_likes
            WHERE post_id = ? AND user_id = ?
            """,
            (post_id, user_id),
        )

        cur.execute(
            """
            UPDATE posts
            SET like_count = CASE
                WHEN like_count > 0 THEN like_count - 1
                ELSE 0
            END
            WHERE id = ?
            """,
            (post_id,),
        )

        conn.commit()
        conn.close()
        return False

    else:
        cur.execute(
            """
            INSERT INTO post_likes (post_id, user_id)
            VALUES (?, ?)
            """,
            (post_id, user_id),
        )

        cur.execute(
            """
            UPDATE posts
            SET like_count = like_count + 1
            WHERE id = ?
            """,
            (post_id,),
        )

        conn.commit()
        conn.close()
        return True


# ========================================
# 📌 게시글 이미지 추가
# ========================================
def add_post_image(post_id: int, image_path: str) -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO post_images (post_id, image_path)
        VALUES (?, ?)
        """,
        (post_id, image_path),
    )
    conn.commit()
    conn.close()


# ========================================
# 📌 게시글 상세
# ========================================
def get_post_detail(post_id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            p.id,
            p.title,
            p.content,
            p.created_at,
            u.username AS author_name,
            (SELECT COUNT(*) FROM post_likes pl WHERE pl.post_id = p.id) AS like_count,
            (SELECT COUNT(*) FROM comments c WHERE c.post_id = p.id) AS comment_count
        FROM posts p
        JOIN users u ON u.id = p.user_id
        WHERE p.id = ?
        """,
        (post_id,),
    )

    post_row = cur.fetchone()
    if not post_row:
        conn.close()
        return None

    cur.execute(
        """
        SELECT image_path
        FROM post_images
        WHERE post_id = ?
        ORDER BY id ASC
        """,
        (post_id,),
    )
    img_rows = cur.fetchall()
    images = [r["image_path"] for r in img_rows]

    cur.execute(
        """
        SELECT
            c.id,
            c.content,
            c.created_at,
            u.username AS author_name
        FROM comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.post_id = ?
        ORDER BY c.created_at ASC
        """,
        (post_id,),
    )
    comment_rows = cur.fetchall()

    comments: List[Dict[str, Any]] = []
    for r in comment_rows:
        comments.append(
            {
                "id": r["id"],
                "content": r["content"],
                "created_at": r["created_at"],
                "author_name": r["author_name"],
            }
        )

    conn.close()

    return {
        "id": post_row["id"],
        "title": post_row["title"],
        "content": post_row["content"],
        "created_at": post_row["created_at"],
        "author_name": post_row["author_name"],
        "like_count": post_row["like_count"],
        "comment_count": post_row["comment_count"],
        "images": images,
        "comments": comments,
    }
