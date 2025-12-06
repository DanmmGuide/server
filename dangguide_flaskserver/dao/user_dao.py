from db import get_conn
from datetime import datetime


def create_user(username: str, password: str):
    """회원가입 (비밀번호 평문 저장)"""
    conn = get_conn()
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO users (username, password, created_at)
            VALUES (?, ?, ?)
        """, (username, password, datetime.utcnow().isoformat()))
        conn.commit()
        user_id = cur.lastrowid
        return {"id": user_id, "username": username}
    except Exception as e:
        return None   # username UNIQUE 충돌 등
    finally:
        conn.close()


def find_user_by_username(username: str):
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cur.fetchone()
    conn.close()

    return row


def validate_login(username: str, password: str):
    user = find_user_by_username(username)
    if user is None:
        return None

    if user["password"] != password:  # 평문 비교
        return None

    return user
