# dangguide_flaskserver/dao/board_dao.py
from typing import List, Dict, Any, Optional
from db import get_conn


# =========================
# 게시글 목록
# =========================
def get_posts() -> List[Dict[str, Any]]:
    """
    게시글 목록 조회
    - 작성자 username
    - like_count, comment_count 포함
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            p.id,
            p.title,
            p.content,
            p.created_at,
            p.like_count,
            p.comment_count,
            u.username AS author_name
        FROM posts p
        JOIN users u ON p.user_id = u.id
        ORDER BY p.id DESC
        """
    )

    rows = cur.fetchall()
    conn.close()

    posts = []
    for r in rows:
        posts.append(
            {
                "id": r["id"],
                "title": r["title"],
                "content": r["content"],
                "created_at": r["created_at"],
                "like_count": r["like_count"],
                "comment_count": r["comment_count"],
                "author_name": r["author_name"],
                # 목록에서는 이미지는 안 내려도 됨 (상세에서만)
            }
        )
    return posts


# =========================
# 게시글 생성
# =========================
def create_post(user_id: int, title: str, content: str) -> Dict[str, Any]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO posts (user_id, title, content)
        VALUES (?, ?, ?)
        """,
        (user_id, title, content),
    )
    post_id = cur.lastrowid

    # 작성자 이름
    cur.execute("SELECT username FROM users WHERE id = ?", (user_id,))
    user_row = cur.fetchone()
    author_name = user_row["username"] if user_row else "익명"

    conn.commit()
    conn.close()

    return {
        "id": post_id,
        "user_id": user_id,
        "title": title,
        "content": content,
        "created_at": None,
        "like_count": 0,
        "comment_count": 0,
        "author_name": author_name,
    }


# =========================
# 단일 게시글 (내부용)
# =========================
def get_post(post_id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            p.id,
            p.user_id,
            p.title,
            p.content,
            p.created_at,
            p.like_count,
            p.comment_count,
            u.username AS author_name
        FROM posts p
        JOIN users u ON p.user_id = u.id
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
        "user_id": row["user_id"],
        "title": row["title"],
        "content": row["content"],
        "created_at": row["created_at"],
        "like_count": row["like_count"],
        "comment_count": row["comment_count"],
        "author_name": row["author_name"],
    }


# =========================
# 댓글 목록
# =========================
def get_comments(post_id: int) -> List[Dict[str, Any]]:
    """
    댓글 목록 조회
    - 여러 개 허용 (user_id에 대한 제한 없음)
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            c.id,
            c.user_id,
            c.post_id,
            c.content,
            c.created_at,
            u.username AS author_name
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.id ASC
        """,
        (post_id,),
    )

    rows = cur.fetchall()
    conn.close()

    comments = []
    for r in rows:
        comments.append(
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "post_id": r["post_id"],
                "content": r["content"],
                "created_at": r["created_at"],
                "author_name": r["author_name"],
            }
        )
    return comments


# =========================
# 댓글 생성 (중복 제한 없음!)
# =========================
def create_comment(user_id: int, post_id: int, content: str) -> None:
    """
    같은 user_id가 같은 post_id에 여러 개 댓글 달 수 있음.
    DB에 UNIQUE 같은 거 안 둠.
    """
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO comments (user_id, post_id, content)
        VALUES (?, ?, ?)
        """,
        (user_id, post_id, content),
    )

    # posts.comment_count 증가
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


# =========================
# 좋아요 토글
# =========================
def toggle_like(post_id: int, user_id: int) -> bool:
    """
    True  -> 좋아요가 새로 생김
    False -> 좋아요가 취소됨
    """
    conn = get_conn()
    cur = conn.cursor()

    # 이미 좋아요 했는지 확인
    cur.execute(
        """
        SELECT id FROM post_likes
        WHERE post_id = ? AND user_id = ?
        """,
        (post_id, user_id),
    )
    row = cur.fetchone()

    if row:
        # 이미 있으면 삭제 = 좋아요 취소
        cur.execute(
            "DELETE FROM post_likes WHERE post_id = ? AND user_id = ?",
            (post_id, user_id),
        )
        cur.execute(
            """
            UPDATE posts
            SET like_count = CASE WHEN like_count > 0 THEN like_count - 1 ELSE 0 END
            WHERE id = ?
            """,
            (post_id,),
        )
        liked = False
    else:
        # 없으면 추가 = 좋아요
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
        liked = True

    conn.commit()
    conn.close()
    return liked


# =========================
# 게시글 이미지
# =========================
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


# =========================
# 게시글 상세 + 이미지 + 댓글 + liked_by_me
# =========================
def get_post_detail(
    post_id: int,
    current_user_id: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    cur = conn.cursor()

    # --- 게시글 기본 정보 + 작성자 이름 ---
    cur.execute(
        """
        SELECT
            p.id,
            p.user_id,
            p.title,
            p.content,
            p.created_at,
            p.like_count,
            p.comment_count,
            u.username AS author_name
        FROM posts p
        JOIN users u ON p.user_id = u.id
        WHERE p.id = ?
        """,
        (post_id,),
    )
    post_row = cur.fetchone()
    if not post_row:
        conn.close()
        return None

    # --- 이미지 목록 ---
    cur.execute(
        """
        SELECT image_path
        FROM post_images
        WHERE post_id = ?
        ORDER BY id ASC
        """,
        (post_id,),
    )
    image_rows = cur.fetchall()
    images = [r["image_path"] for r in image_rows]

    # --- 댓글 목록 (위에서 만든 get_comments 재사용해도 됨) ---
    cur.execute(
        """
        SELECT
            c.id,
            c.user_id,
            c.post_id,
            c.content,
            c.created_at,
            u.username AS author_name
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.post_id = ?
        ORDER BY c.id ASC
        """,
        (post_id,),
    )
    comment_rows = cur.fetchall()
    comments = []
    for r in comment_rows:
        comments.append(
            {
                "id": r["id"],
                "user_id": r["user_id"],
                "post_id": r["post_id"],
                "content": r["content"],
                "created_at": r["created_at"],
                "author_name": r["author_name"],
            }
        )

    # --- liked_by_me 계산 ---
    liked_by_me = False
    if current_user_id is not None:
        cur.execute(
            """
            SELECT 1 FROM post_likes
            WHERE post_id = ? AND user_id = ?
            """,
            (post_id, current_user_id),
        )
        if cur.fetchone():
            liked_by_me = True

    conn.close()

    return {
        "id": post_row["id"],
        "user_id": post_row["user_id"],
        "title": post_row["title"],
        "content": post_row["content"],
        "created_at": post_row["created_at"],
        "like_count": post_row["like_count"],
        "comment_count": post_row["comment_count"],
        "author_name": post_row["author_name"],

        "images": images,
        "comments": comments,
        "liked_by_me": liked_by_me,
    }
