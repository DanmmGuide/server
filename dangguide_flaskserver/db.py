# db.py
import sqlite3
from pathlib import Path

# 같은 폴더에 DB 파일 생성
DB_PATH = Path(__file__).parent / "dangguide_server.db"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # dict처럼 접근 가능
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # 1) 게시글 테이블
    cur.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            author_name TEXT NOT NULL,
            created_at TEXT NOT NULL,
            like_count INTEGER NOT NULL DEFAULT 0
        )
    """)

    # 2) 댓글 테이블
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            post_id INTEGER NOT NULL,
            author_name TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        )
    """)

    conn.commit()
    conn.close()


