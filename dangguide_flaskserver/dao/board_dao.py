# dangguide_flaskserver/dao/board_dao.py

from typing import List, Dict, Optional
from db import get_conn


# =========================
# 게시글 목록
# =========================
def get_posts() -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            p.id,
            p.title,
            p.created_at,
            u.username AS author_name,
            COALESCE(p.like_count, 0)   AS likes,
            COALESCE(p.comment_count, 0) AS comments,
            (
                SELECT image_path
                FROM post_images
                WHERE post_id = p.id
                ORDER BY id ASC
                LIMIT 1
            ) AS thumbnail
        FROM posts p
        JOIN users u ON u.id = p.user_id
        ORDER BY p.id DESC
        """
    )

    rows = cur.fetchall()
    conn.close()

    posts: List[Dict] = []
    for r in rows:
        posts.append(
            {
                "id": r["id"],
                "title": r["title"],
                "created_at": r["created_at"],
                "author_name": r["author_name"],
                "likes": r["likes"],         # ← Flutter에서 PostItem.likes 로 쓰기
                "comments": r["comments"],   # ← Flutter에서 PostItem.comments
                "thumbnail": r["thumbnail"], # 필요 없으면 빼도 됨
            }
        )
    return posts


# =========================
# 게시글 생성
# =========================
def create_post(user_id: int, title: str, content: str) -> Dict:
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

    cur.execute(
        """
        SELECT
            p.id,
            p.title,
            p.content,
            p.created_at,
            u.username AS author_name,
            COALESCE(p.like_count, 0)   AS likes,
            COALESCE(p.comment_count, 0) AS comments
        FROM posts p
        JOIN users u ON u.id = p.user_id
        WHERE p.id = ?
        """,
        (post_id,),
    )
    row = cur.fetchone()
    conn.commit()
    conn.close()

    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "created_at": row["created_at"],
        "author_name": row["author_name"],
        "likes": row["likes"],
        "comments": row["comments"],
        "images": [],
        "comment_items": [],
    }


# =========================
# 댓글 목록
# =========================
def get_comments(post_id: int) -> List[Dict]:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT
            c.id,
            c.content,
            c.created_at,
            u.username AS user_name
        FROM comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.post_id = ?
        ORDER BY c.id ASC
        """,
        (post_id,),
    )
    rows = cur.fetchall()
    conn.close()

    comments: List[Dict] = []
    for r in rows:
        comments.append(
            {
                "id": r["id"],
                "content": r["content"],
                "created_at": r["created_at"],
                "user_name": r["user_name"],
            }
        )
    return comments


# =========================
# 댓글 생성
# =========================
def create_comment(user_id: int, post_id: int, content: str) -> None:
    conn = get_conn()
    cur = conn.cursor()

    # 댓글 삽입
    cur.execute(
        """
        INSERT INTO comments (user_id, post_id, content)
        VALUES (?, ?, ?)
        """,
        (user_id, post_id, content),
    )

    # 댓글 개수 재계산해서 posts.comment_count에 반영
    cur.execute(
        """
        UPDATE posts
        SET comment_count = (
            SELECT COUNT(*) FROM comments WHERE post_id = ?
        )
        WHERE id = ?
        """,
        (post_id, post_id),
    )

    conn.commit()
    conn.close()


# =========================
# 좋아요 토글 (여러 유저 가능)
# =========================
def toggle_like(post_id: int, user_id: int) -> bool:
    """
    True  → 이번 요청으로 '좋아요 ON'
    False → 이번 요청으로 '좋아요 OFF'
    """
    conn = get_conn()
    cur = conn.cursor()

    # 이 유저가 이미 이 글 좋아요 했는지 확인
    cur.execute(
        """
        SELECT 1
        FROM post_likes
        WHERE post_id = ? AND user_id = ?
        """,
        (post_id, user_id),
    )
    row = cur.fetchone()

    if row:
        # 이미 좋아요 → 취소
        cur.execute(
            """
            DELETE FROM post_likes
            WHERE post_id = ? AND user_id = ?
            """,
            (post_id, user_id),
        )
        liked = False
    else:
        # 아직 안 눌렀으면 → 좋아요 추가
        cur.execute(
            """
            INSERT INTO post_likes (post_id, user_id)
            VALUES (?, ?)
            """,
            (post_id, user_id),
        )
        liked = True

    # 🔥 좋아요 총 개수 다시 계산해서 posts.like_count에 반영
    cur.execute(
        """
        UPDATE posts
        SET like_count = (
            SELECT COUNT(*)
            FROM post_likes
            WHERE post_id = ?
        )
        WHERE id = ?
        """,
        (post_id, post_id),
    )

    conn.commit()
    conn.close()
    return liked


# =========================
# 게시글 이미지 추가
# =========================
def add_post_image(post_id: int, filename: str) -> None:
    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO post_images (post_id, image_path)
        VALUES (?, ?)
        """,
        (post_id, filename),
    )

    conn.commit()
    conn.close()


# =========================
# 게시글 단건 상세 + 이미지/댓글/좋아요
# =========================
def get_post_detail(post_id: int, current_user_id: Optional[int]) -> Optional[Dict]:
    conn = get_conn()
    cur = conn.cursor()

    # 기본 게시글 + 작성자
    cur.execute(
        """
        SELECT
            p.id,
            p.title,
            p.content,
            p.created_at,
            u.username AS author_name,
            COALESCE(p.like_count, 0)   AS likes,
            COALESCE(p.comment_count, 0) AS comments
        FROM posts p
        JOIN users u ON u.id = p.user_id
        WHERE p.id = ?
        """,
        (post_id,),
    )
    row = cur.fetchone()
    if not row:
        conn.close()
        return None

    detail: Dict = {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "created_at": row["created_at"],
        "author_name": row["author_name"],
        "likes": row["likes"],
        "comments": row["comments"],
    }

    # 이미지 목록 (파일명 리스트, 라우트에서 URL로 변환)
    cur.execute(
        """
        SELECT image_path
        FROM post_images
        WHERE post_id = ?
        ORDER BY id ASC
        """,
        (post_id,),
    )
    detail["images"] = [r["image_path"] for r in cur.fetchall()]

    # 댓글 목록
    cur.execute(
        """
        SELECT
            c.id,
            c.content,
            c.created_at,
            u.username AS user_name
        FROM comments c
        JOIN users u ON u.id = c.user_id
        WHERE c.post_id = ?
        ORDER BY c.id ASC
        """,
        (post_id,),
    )
    comment_rows = cur.fetchall()
    comment_items: List[Dict] = []
    for r in comment_rows:
        comment_items.append(
            {
                "id": r["id"],
                "content": r["content"],
                "created_at": r["created_at"],
                "user_name": r["user_name"],
            }
        )
    detail["comment_items"] = comment_items

    # 댓글 수를 DB와 동기화해 두고 싶다면:
    cur.execute(
        """
        UPDATE posts
        SET comment_count = ?
        WHERE id = ?
        """,
        (len(comment_items), post_id),
    )

    # 좋아요 실제 개수 다시 계산 (혹시 모를 싱크 맞추기)
    cur.execute(
        """
        SELECT COUNT(*) AS cnt
        FROM post_likes
        WHERE post_id = ?
        """,
        (post_id,),
    )
    like_cnt = cur.fetchone()["cnt"]
    detail["likes"] = like_cnt

    cur.execute(
        """
        UPDATE posts
        SET like_count = ?
        WHERE id = ?
        """,
        (like_cnt, post_id),
    )

    # 내가 좋아요 눌렀는지
    liked_by_me = False
    if current_user_id is not None:
        cur.execute(
            """
            SELECT 1
            FROM post_likes
            WHERE post_id = ? AND user_id = ?
            """,
            (post_id, current_user_id),
        )
        liked_by_me = cur.fetchone() is not None

    detail["liked_by_me"] = liked_by_me

    conn.commit()
    conn.close()
    return detail
