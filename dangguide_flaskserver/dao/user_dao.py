from __future__ import annotations

from typing import Optional, Dict, Any

from db import get_conn


def find_user_by_username(username: str) -> Optional[Dict[str, Any]]:
  conn = get_conn()
  cur = conn.cursor()

  cur.execute(
    "SELECT id, username, password, created_at FROM users WHERE username = ?",
    (username,),
  )
  row = cur.fetchone()
  conn.close()

  if row is None:
    return None

  return {
    "id": row["id"],
    "username": row["username"],
    "password": row["password"],
    "created_at": row["created_at"],
  }


def create_user(username: str, password: str) -> Optional[Dict[str, Any]]:
  """
  단순 예제용: 비밀번호 평문 저장.
  실제 서비스라면 반드시 해시 사용해야 함.
  """
  conn = get_conn()
  cur = conn.cursor()

  try:
    cur.execute(
      """
      INSERT INTO users (username, password)
      VALUES (?, ?)
      """,
      (username, password),
    )
    conn.commit()

    user_id = cur.lastrowid

    return {
      "id": user_id,
      "username": username,
    }
  except Exception:
    conn.rollback()
    return None
  finally:
    conn.close()


def validate_login(username: str, password: str) -> Optional[Dict[str, Any]]:
  user = find_user_by_username(username)
  if user is None:
    return None

  # 평문 비교 (예제용)
  if user["password"] != password:
    return None

  return {
    "id": user["id"],
    "username": user["username"],
  }
