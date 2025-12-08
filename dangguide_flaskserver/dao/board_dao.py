# dangguide_flaskserver/dao/board_dao.py
from db import get_conn


def get_post_detail(post_id: int):
    conn = get_conn()
    cur = conn.cursor()

    # 게시글 + 글쓴이 이름
    cur.execute("""
        SELECT 
            p.id,
            p.title,
            p.content,
            p.created_at,
            u.username AS author_name
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
    """, (post_id,))
    row = cur.fetchone()

    if row is None:
        conn.close()
        return None

    post = {
        "id": row[0],
        "title": row[1],
        "content": row[2],
        "created_at": row[3],
        "author_name": row[4],
    }

    # 이미지 (있다면)
    cur.execute("""
        SELECT image_url
        FROM post_images
        WHERE post_id = ?
        ORDER BY id ASC
    """, (post_id,))
    image_rows = cur.fetchall()
    post["image_paths"] = [r[0] for r in image_rows]

    # 좋아요 수
    cur.execute("""
        SELECT COUNT(*)
        FROM likes
        WHERE post_id = ?
    """, (post_id,))
    post["like_count"] = cur.fetchone()[0]

    # 댓글 + 댓글 작성자 이름
    cur.execute("""
        SELECT 
            c.id,
            c.content,
            c.created_at,
            u.username AS author_name
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.id ASC
    """, (post_id,))

    comments = []
    for r in cur.fetchall():
        comments.append({
            "id": r[0],
            "content": r[1],
            "created_at": r[2],
            "author_name": r[3],
        })
    post["comments"] = comments
    post["comment_count"] = len(comments)

    conn.close()
    return post


def add_comment(post_id: int, user_id: int, content: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO comments (post_id, user_id, content)
        VALUES (?, ?, ?)
    """, (post_id, user_id, content))
    conn.commit()
    conn.close()


def toggle_like(post_id: int, user_id: int):
    """
    이미 좋아요 있으면 취소, 없으면 추가
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        SELECT 1 FROM likes
        WHERE post_id = ? AND user_id = ?
    """, (post_id, user_id))
    exists = cur.fetchone() is not None

    if exists:
        cur.execute("""
            DELETE FROM likes
            WHERE post_id = ? AND user_id = ?
        """, (post_id, user_id))
        liked = False
    else:
        cur.execute("""
            INSERT INTO likes (post_id, user_id)
            VALUES (?, ?)
        """, (post_id, user_id))
        liked = True

    conn.commit()

    # 현재 좋아요 수
    cur.execute("""
        SELECT COUNT(*) FROM likes
        WHERE post_id = ?
    """, (post_id,))
    like_count = cur.fetchone()[0]

    conn.close()
    return liked, like_count
